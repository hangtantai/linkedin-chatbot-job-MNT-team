function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Optional: Show feedback that text was copied
        const button = event.target;
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        setTimeout(() => {
            button.textContent = originalText;
        }, 2000);
    });
}

function setupAutoRefresh() {
    if (!window.init_refresh_set) {
        window.init_refresh_set = true;
        setTimeout(function() {
            window.location.reload();
        }, 3000);  // Check every 3 seconds
    }
}

// Execute when document is ready
document.addEventListener('DOMContentLoaded', setupAutoRefresh);


function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        // Optional: Show success message
        console.log('Text copied successfully');
    }).catch(function(err) {
        console.error('Failed to copy text:', err);
    });
}