    // Hide the message after 7 seconds
    window.onload = function() {
        const messageDiv = document.getElementById("message");
        if (messageDiv) {
            setTimeout(function() {
                messageDiv.style.opacity = '0'; // Fade out
                setTimeout(() => messageDiv.style.display = "none", 500); // Hide after fade-out
            }, 7000); // 7000 milliseconds = 7 seconds
        }
    };