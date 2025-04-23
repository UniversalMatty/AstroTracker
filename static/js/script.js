// Main script for the astrological calculator

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form elements and event listeners
    initializeDateTimePickers();
    setupFormValidation();
    setupFileUpload();
});

function initializeDateTimePickers() {
    // Set default date to today
    const dateInput = document.getElementById('dob_date');
    if (dateInput) {
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        
        dateInput.value = `${year}-${month}-${day}`;
        
        // Set max date to today (can't calculate for future dates)
        dateInput.max = `${year}-${month}-${day}`;
    }
}

function setupFormValidation() {
    const form = document.getElementById('birth-details-form');
    if (form) {
        form.addEventListener('submit', function(event) {
            if (!validateForm()) {
                event.preventDefault();
            }
        });
    }
}

function validateForm() {
    let isValid = true;
    
    // Required fields
    const dobDate = document.getElementById('dob_date');
    const country = document.getElementById('country');
    const city = document.getElementById('city');
    
    // Reset previous validation messages
    document.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
    document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    
    // Validate date
    if (!dobDate.value) {
        isValid = false;
        showValidationError(dobDate, 'Birth date is required');
    }
    
    // Validate location
    if (!country.value.trim()) {
        isValid = false;
        showValidationError(country, 'Country is required');
    }
    
    if (!city.value.trim()) {
        isValid = false;
        showValidationError(city, 'City is required');
    }
    
    return isValid;
}

function showValidationError(element, message) {
    element.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    element.parentNode.appendChild(errorDiv);
}

function setupFileUpload() {
    const fileInput = document.getElementById('ephemerides_file');
    const fileLabel = document.querySelector('.custom-file-label');
    
    if (fileInput && fileLabel) {
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                fileLabel.textContent = fileInput.files[0].name;
            } else {
                fileLabel.textContent = 'Choose file (optional)';
            }
            
            // Validate file extension
            if (fileInput.files.length > 0) {
                const fileName = fileInput.files[0].name;
                const extension = fileName.split('.').pop().toLowerCase();
                
                if (!['json', 'csv', 'txt'].includes(extension)) {
                    showValidationError(fileInput, 'Only JSON, CSV or TXT files are allowed');
                    fileInput.value = '';
                    fileLabel.textContent = 'Choose file (optional)';
                }
            }
        });
    }
}
