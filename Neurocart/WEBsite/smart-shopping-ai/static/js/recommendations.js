document.addEventListener('DOMContentLoaded', () => {
    const customerLookupForm = document.getElementById('customer-lookup-form');
    const recommendationsContent = document.getElementById('recommendations-content');
    
    customerLookupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const customerId = document.getElementById('customer-id').value;
        if (!customerId) {
            alert('Please enter a customer ID');
            return;
        }
        
        try {
            recommendationsContent.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading recommendations...</p>
                </div>
            `;
            
            const response = await fetch(`/api/recommendations/${customerId}`);
            const data = await response.json();
            
            if (data.error) {
                recommendationsContent.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle"></i>
                        ${data.error}
                    </div>
                `;
                return;
            }
            
            // Format recommendations
            const recommendationsHtml = data.recommendations.map((rec, index) => `
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="card-title mb-0">${rec.product.name}</h5>
                            <span class="badge bg-primary">${rec.confidence_score.toFixed(2)}</span>
                        </div>
                        <p class="card-text text-muted">${rec.product.category}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="h5 mb-0">$${rec.product.price.toFixed(2)}</span>
                            <button class="btn btn-outline-primary btn-sm track-event" 
                                    data-product-id="${rec.product.product_id}"
                                    data-event-type="view">
                                View Details
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
            
            recommendationsContent.innerHTML = `
                <div class="mb-3">
                    <h6 class="text-muted">Customer Segment</h6>
                    <span class="badge bg-info">${data.segment.segment_tag}</span>
                    <small class="text-muted ms-2">Score: ${data.segment.score.toFixed(2)}</small>
                </div>
                <div class="recommendations-list">
                    ${recommendationsHtml}
                </div>
            `;
            
            // Add event listeners to track buttons
            document.querySelectorAll('.track-event').forEach(button => {
                button.addEventListener('click', async (e) => {
                    const productId = e.target.dataset.productId;
                    const eventType = e.target.dataset.eventType;
                    
                    try {
                        await fetch('/api/track_event', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                customer_id: customerId,
                                product_id: productId,
                                event_type: eventType
                            })
                        });
                        
                        // Show success message
                        const toast = document.createElement('div');
                        toast.className = 'toast align-items-center text-white bg-success border-0';
                        toast.setAttribute('role', 'alert');
                        toast.innerHTML = `
                            <div class="d-flex">
                                <div class="toast-body">
                                    Event tracked successfully
                                </div>
                                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                            </div>
                        `;
                        document.body.appendChild(toast);
                        const bsToast = new bootstrap.Toast(toast);
                        bsToast.show();
                        
                        // Remove toast after it's hidden
                        toast.addEventListener('hidden.bs.toast', () => {
                            toast.remove();
                        });
                        
                    } catch (error) {
                        console.error('Error tracking event:', error);
                    }
                });
            });
            
        } catch (error) {
            console.error('Error getting recommendations:', error);
            recommendationsContent.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle"></i>
                    Error loading recommendations
                </div>
            `;
        }
    });
}); 