document.addEventListener('DOMContentLoaded', async () => {
    const segmentsContent = document.getElementById('segments-content');
    
    try {
        const response = await fetch('/api/segments');
        const data = await response.json();
        
        if (data.error) {
            segmentsContent.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle"></i>
                    ${data.error}
                </div>
            `;
            return;
        }
        
        // Create canvas for chart
        const canvas = document.createElement('canvas');
        canvas.id = 'segments-chart';
        segmentsContent.innerHTML = '';
        segmentsContent.appendChild(canvas);
        
        // Prepare data for chart
        const segments = data.segments;
        const labels = segments.map(s => s.segment_tag);
        const counts = segments.map(s => s.count);
        const total = counts.reduce((a, b) => a + b, 0);
        const percentages = counts.map(c => ((c / total) * 100).toFixed(1));
        
        // Create chart
        new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: labels.map((label, i) => `${label} (${percentages[i]}%)`),
                datasets: [{
                    data: counts,
                    backgroundColor: [
                        '#3498db',
                        '#2ecc71',
                        '#e74c3c',
                        '#f1c40f',
                        '#9b59b6',
                        '#1abc9c'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right'
                    },
                    title: {
                        display: true,
                        text: 'Customer Segment Distribution'
                    }
                }
            }
        });
        
        // Add segment details
        const detailsDiv = document.createElement('div');
        detailsDiv.className = 'mt-4';
        detailsDiv.innerHTML = `
            <h6 class="text-muted mb-3">Segment Details</h6>
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Segment</th>
                            <th>Count</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${segments.map((segment, i) => `
                            <tr>
                                <td>
                                    <span class="badge bg-primary">${segment.segment_tag}</span>
                                </td>
                                <td>${segment.count}</td>
                                <td>${percentages[i]}%</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        segmentsContent.appendChild(detailsDiv);
        
    } catch (error) {
        console.error('Error loading segments:', error);
        segmentsContent.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle"></i>
                Error loading segment data
            </div>
        `;
    }
}); 