// Global chart instances
let productsChart = null;
let conversionChart = null;
let heatmapChart = null;

// Fetch and update report data
async function updateReportData() {
    try {
        const response = await fetch('/api/reports/latest');
        if (!response.ok) {
            throw new Error('Failed to fetch report data');
        }
        const data = await response.json();
        
        // Update metrics
        document.getElementById('aov').textContent = `$${data.metrics.average_order_value.toFixed(2)}`;
        document.getElementById('conversion').textContent = `${(data.metrics.conversion_rate * 100).toFixed(1)}%`;
        document.getElementById('retention').textContent = `${(data.metrics.retention_rate * 100).toFixed(1)}%`;
        
        // Update charts
        updateProductsChart(data.best_performing_products);
        updateConversionChart(data.conversion_by_segment);
        updateHeatmapChart(data.engagement_heatmap);
        
    } catch (error) {
        console.error('Error updating report data:', error);
        showError('Failed to load report data. Please try again later.');
    }
}

// Update best performing products chart
function updateProductsChart(products) {
    const ctx = document.getElementById('productsChart').getContext('2d');
    
    if (productsChart) {
        productsChart.destroy();
    }
    
    productsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: products.map(p => p.name),
            datasets: [{
                label: 'Sales Count',
                data: products.map(p => p.sales_count),
                backgroundColor: 'rgba(54, 162, 235, 0.8)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Sales'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Update conversion rates by segment chart
function updateConversionChart(segments) {
    const ctx = document.getElementById('conversionChart').getContext('2d');
    
    if (conversionChart) {
        conversionChart.destroy();
    }
    
    conversionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: segments.map(s => s.segment),
            datasets: [{
                label: 'Conversion Rate',
                data: segments.map(s => s.conversion_rate * 100),
                backgroundColor: 'rgba(75, 192, 192, 0.8)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Conversion Rate (%)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Update engagement heatmap chart
function updateHeatmapChart(heatmapData) {
    const ctx = document.getElementById('heatmapChart').getContext('2d');
    
    if (heatmapChart) {
        heatmapChart.destroy();
    }
    
    // Prepare data for heatmap
    const segments = [...new Set(heatmapData.map(d => d.segment))];
    const categories = [...new Set(heatmapData.map(d => d.category))];
    
    const data = segments.map(segment => {
        return categories.map(category => {
            const entry = heatmapData.find(d => d.segment === segment && d.category === category);
            return entry ? entry.engagement_score : 0;
        });
    });
    
    heatmapChart = new Chart(ctx, {
        type: 'matrix',
        data: {
            datasets: [{
                data: heatmapData.map(d => ({
                    x: d.category,
                    y: d.segment,
                    v: d.engagement_score
                })),
                backgroundColor(context) {
                    const value = context.dataset.data[context.dataIndex].v;
                    const alpha = (value - 0) / (1 - 0);
                    return `rgba(255, 99, 132, ${alpha})`;
                },
                borderColor: 'white',
                borderWidth: 1,
                width: ({ chart }) => (chart.chartArea || {}).width / categories.length - 1,
                height: ({ chart }) => (chart.chartArea || {}).height / segments.length - 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'category',
                    labels: categories,
                    offset: true
                },
                y: {
                    type: 'category',
                    labels: segments,
                    offset: true
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        title() {
                            return '';
                        },
                        label(context) {
                            const v = context.dataset.data[context.dataIndex];
                            return [
                                `Segment: ${v.y}`,
                                `Category: ${v.x}`,
                                `Engagement: ${v.v.toFixed(2)}`
                            ];
                        }
                    }
                }
            }
        }
    });
}

// Show error message
function showError(message) {
    const container = document.querySelector('.container');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    container.insertBefore(errorDiv, container.firstChild);
}

// Initialize report page
document.addEventListener('DOMContentLoaded', () => {
    updateReportData();
    // Refresh data every 5 minutes
    setInterval(updateReportData, 5 * 60 * 1000);
}); 