document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData();
        const customersFile = document.getElementById('customers-file').files[0];
        const productsFile = document.getElementById('products-file').files[0];
        const eventsFile = document.getElementById('events-file').files[0];
        
        if (!customersFile || !productsFile) {
            alert('Please upload both customers.csv and products.csv files');
            return;
        }
        
        formData.append('customers', customersFile);
        formData.append('products', productsFile);
        if (eventsFile) {
            formData.append('events', eventsFile);
        }
        
        try {
            const submitButton = uploadForm.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Uploading...
            `;
            
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.error) {
                throw new Error(result.error);
            }
            
            alert('Files uploaded successfully!');
            uploadForm.reset();
            
        } catch (error) {
            console.error('Error uploading files:', error);
            alert(`Error uploading files: ${error.message}`);
        } finally {
            const submitButton = uploadForm.querySelector('button[type="submit"]');
            submitButton.disabled = false;
            submitButton.innerHTML = 'Upload Files';
        }
    });
    
    // Add file validation
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file && !file.name.endsWith('.csv')) {
                alert('Please upload a CSV file');
                e.target.value = '';
            }
        });
    });
}); 