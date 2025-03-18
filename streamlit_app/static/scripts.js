// function copyToClipboard(text) {
//     navigator.clipboard.writeText(text).then(() => {
//         // Optional: Show feedback that text was copied
//         const button = event.target;
//         const originalText = button.textContent;
//         button.textContent = 'Copied!';
//         setTimeout(() => {
//             button.textContent = originalText;
//         }, 2000);
//     });
// }

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

// Function to copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
        .then(() => {
            // Create a temporary element to show "Copied!" feedback
            const button = document.activeElement;
            const originalText = button.innerText;
            button.innerText = "✓ Copied!";
            
            // Reset button text after 2 seconds
            setTimeout(() => {
                button.innerText = originalText;
            }, 2000);
        })
        .catch(err => {
            console.error('Failed to copy text: ', err);
            alert('Failed to copy text. Please try again.');
        });
}

// Function to check if the chatbot is ready
function checkChatbotStatus() {
    // Look for elements that indicate the chatbot is ready
    const statusElement = document.querySelector('[data-testid="stAppViewBlockContainer"]');
    
    if (statusElement) {
        const text = statusElement.textContent;
        // If we find the initialization message, keep polling
        if (text.includes("initializing")) {
            setTimeout(checkChatbotStatus, 1000); // Check every second
        } else {
            // If we don't find the initialization message, the chatbot might be ready
            // Additional check - if we see any chat messages or the input is enabled
            const chatMessages = document.querySelectorAll('.stChatMessage');
            const chatInput = document.querySelector('.stChatInputContainer input:not([disabled])');
            
            if (chatMessages.length > 0 || chatInput) {
                console.log("Chatbot appears to be ready, but page wasn't reloaded automatically.");
                // Only reload if we haven't just loaded the page (prevents reload loops)
                if (window.performance && window.performance.navigation.type !== window.performance.navigation.TYPE_RELOAD) {
                    console.log("Reloading page...");
                    window.location.reload();
                }
            } else {
                // Keep checking
                setTimeout(checkChatbotStatus, 1000);
            }
        }
    } else {
        // If we can't find the status element, keep polling
        setTimeout(checkChatbotStatus, 1000);
    }
}

// Function for polling the ready state
function pollForReadyState() {
    let checkCount = 0;
    
    function check() {
        checkCount++;
        console.log("Checking if chatbot is ready (attempt " + checkCount + ")");
        
        // Force reload after 30 checks (approximately 60 seconds)
        if (checkCount > 30) {
            console.log("Forcing page reload after 30 attempts");
            window.location.reload();
            return;
        }
        
        // Look for indicators that the chatbot is ready
        const loadingMessage = document.querySelector('p[style*="text-align: center; color: #4b6cb7"]');
        const chatInput = document.querySelector('.stChatInputContainer input');
        
        if (!loadingMessage || (chatInput && !chatInput.disabled)) {
            console.log("Chatbot appears to be ready, reloading page...");
            window.location.reload();
        } else {
            console.log("Chatbot still initializing, checking again in 2 seconds...");
            setTimeout(check, 2000);
        }
    }
    
    // Start checking
    setTimeout(check, 2000);
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Start checking status after a short delay
    setTimeout(checkChatbotStatus, 2000);
    
    // Start polling for ready state if we're in initialization mode
    if (document.querySelector('p[style*="text-align: center; color: #4b6cb7"]')) {
        setTimeout(pollForReadyState, 2000);
    }
});

// Function to check initialization status and reload if necessary
function initializationChecker() {
    let checkCount = 0;
    
    function pollForReadyState() {
        checkCount++;
        console.log("Checking if chatbot is ready (attempt " + checkCount + ")");
        
        // Force reload after 30 checks (approximately 60 seconds)
        if (checkCount > 30) {
            console.log("Forcing page reload after 30 attempts");
            window.location.reload();
            return;
        }
        
        // Look for indicators that the chatbot is ready
        const loadingMessage = document.querySelector('p[style*="text-align: center; color: #4b6cb7"]');
        const chatInput = document.querySelector('.stChatInputContainer input');
        
        if (!loadingMessage || (chatInput && !chatInput.disabled)) {
            console.log("Chatbot appears to be ready, reloading page...");
            window.location.reload();
        } else {
            console.log("Chatbot still initializing, checking again in 2 seconds...");
            setTimeout(pollForReadyState, 2000);
        }
    }
    
    // Start polling after a short delay
    setTimeout(pollForReadyState, 2000);
}

// Add event listener to start the initialization checker if needed
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('p[style*="text-align: center; color: #4b6cb7"]')) {
        initializationChecker();
    }
});