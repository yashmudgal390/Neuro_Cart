// Check system health
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        const healthStatus = document.getElementById('health-status');
        if (data.status === 'healthy') {
            healthStatus.className = 'alert alert-success';
            healthStatus.innerHTML = `
                <i class="fas fa-check-circle"></i>
                System is healthy
                <small class="d-block text-muted">Last checked: ${new Date().toLocaleString()}</small>
            `;
        } else {
            healthStatus.className = 'alert alert-danger';
            healthStatus.innerHTML = `
                <i class="fas fa-exclamation-circle"></i>
                System is unhealthy: ${data.error}
            `;
        }
    } catch (error) {
        console.error('Error checking health:', error);
        const healthStatus = document.getElementById('health-status');
        healthStatus.className = 'alert alert-danger';
        healthStatus.innerHTML = `
            <i class="fas fa-exclamation-circle"></i>
            Error checking system health
        `;
    }
}

// Load recent activity
async function loadRecentActivity() {
    try {
        const response = await fetch('/api/reports/latest');
        const data = await response.json();
        
        const activityList = document.getElementById('recent-activity');
        if (data.error) {
            activityList.innerHTML = `
                <div class="list-group-item text-muted">
                    No recent activity found
                </div>
            `;
            return;
        }
        
        // Format the activity data
        const activities = [
            {
                title: 'Latest Report',
                description: `Type: ${data.type}`,
                timestamp: new Date().toLocaleString()
            }
        ];
        
        activityList.innerHTML = activities.map(activity => `
            <div class="list-group-item">
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">${activity.title}</h6>
                    <small class="text-muted">${activity.timestamp}</small>
                </div>
                <p class="mb-1">${activity.description}</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading recent activity:', error);
        const activityList = document.getElementById('recent-activity');
        activityList.innerHTML = `
            <div class="list-group-item text-danger">
                Error loading recent activity
            </div>
        `;
    }
}

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    loadRecentActivity();
    
    // Refresh data every 30 seconds
    setInterval(() => {
        checkHealth();
        loadRecentActivity();
    }, 30000);
}); 