// ZapLink Main Client Interactions

document.addEventListener('DOMContentLoaded', () => {
    // 1. Advanced Options Drawer Toggle
    const optionsTrigger = document.getElementById('options-trigger');
    const optionsContent = document.getElementById('options-content');
    const optionsChevron = document.getElementById('options-chevron');

    if (optionsTrigger && optionsContent) {
        optionsTrigger.addEventListener('click', () => {
            optionsContent.classList.toggle('hidden');
            if (optionsChevron) {
                optionsChevron.classList.toggle('rotate');
            }
        });
    }

    // 2. AJAX Form Submission
    const shortenForm = document.getElementById('shorten-form');
    const submitBtn = document.getElementById('submit-btn');
    const errorAlert = document.getElementById('error-alert');
    const errorMessage = document.getElementById('error-message');
    const successCard = document.getElementById('success-card');
    
    // Result card elements
    const resultShortUrl = document.getElementById('result-short-url');
    const resultOriginalUrl = document.getElementById('result-original-url');
    const resultAnalyticsLink = document.getElementById('result-analytics-link');
    const copyBtn = document.getElementById('copy-btn');

    if (shortenForm) {
        shortenForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Clear prior states
            errorAlert.classList.add('hidden');
            successCard.classList.add('hidden');
            
            // Get values
            const formData = new FormData(shortenForm);
            
            // Button loading state
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                <span>Processing...</span>
                <div class="spinner"></div>
            `;
            
            try {
                const response = await fetch('/shorten', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Populate success card
                    resultShortUrl.textContent = data.short_url;
                    resultOriginalUrl.textContent = data.original_url;
                    resultOriginalUrl.title = data.original_url;
                    
                    // Set up analytics link
                    resultAnalyticsLink.href = `/analytics/${data.short_code}`;
                    
                    // Set up copy button clipboard target
                    copyBtn.setAttribute('data-clipboard', data.short_url);
                    
                    // Reveal success card
                    successCard.classList.remove('hidden');
                    
                    // Reset inputs
                    document.getElementById('url-input').value = '';
                    const customCodeInput = document.getElementById('custom-code-input');
                    if (customCodeInput) customCodeInput.value = '';
                } else {
                    // Show error
                    errorMessage.textContent = data.message || 'An error occurred while shortening the URL.';
                    errorAlert.classList.remove('hidden');
                }
            } catch (err) {
                console.error(err);
                errorMessage.textContent = 'Failed to connect to the server. Please try again.';
                errorAlert.classList.remove('hidden');
            } finally {
                // Restore button
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
                // Reinitialize lucide icons for success card components
                if (window.lucide) {
                    window.lucide.createIcons();
                }
            }
        });
    }

    // 3. Clipboard Copy Actions
    
    // Helper function to handle clipboard write & UI feedback
    async function copyToClipboard(text, element, originalHtml, successText = 'Copied!') {
        try {
            await navigator.clipboard.writeText(text);
            
            // UI Visual feedback
            element.classList.add('success');
            
            // Check if it's the main copy button or a table button
            if (element.id === 'copy-btn') {
                element.innerHTML = `
                    <i data-lucide="check" class="copy-icon"></i>
                    <span>${successText}</span>
                `;
            } else {
                element.innerHTML = `<i data-lucide="check"></i>`;
            }
            
            if (window.lucide) {
                window.lucide.createIcons();
            }
            
            // Revert back after delay
            setTimeout(() => {
                element.classList.remove('success');
                element.innerHTML = originalHtml;
                if (window.lucide) {
                    window.lucide.createIcons();
                }
            }, 2000);
        } catch (err) {
            console.error('Failed to copy: ', err);
            alert('Failed to copy to clipboard.');
        }
    }

    // Main result copy button
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const textToCopy = copyBtn.getAttribute('data-clipboard');
            const originalHtml = `
                <i data-lucide="copy" class="copy-icon"></i>
                <span>Copy</span>
            `;
            copyToClipboard(textToCopy, copyBtn, originalHtml);
        });
    }

    // Table copy buttons
    document.querySelectorAll('.btn-copy-table').forEach(button => {
        button.addEventListener('click', () => {
            const textToCopy = button.getAttribute('data-copy-value');
            const originalHtml = `<i data-lucide="copy"></i>`;
            copyToClipboard(textToCopy, button, originalHtml);
        });
    });

    // Analytics details page mini copy button
    document.querySelectorAll('.btn-copy-mini').forEach(button => {
        button.addEventListener('click', () => {
            const textToCopy = button.getAttribute('data-copy-value');
            const originalHtml = `<i data-lucide="copy"></i>`;
            copyToClipboard(textToCopy, button, originalHtml);
        });
    });
});
