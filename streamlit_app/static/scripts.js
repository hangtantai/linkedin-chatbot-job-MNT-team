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