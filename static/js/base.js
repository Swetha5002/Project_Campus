



const enterFullscreenButton = document.getElementById('enterFullscreen');
const exitFullscreenButton = document.getElementById('exitFullscreen');

// Add event listeners to the buttons
enterFullscreenButton.addEventListener('click', enterFullscreen);
exitFullscreenButton.addEventListener('click', exitFullscreen);

setInterval(updateLiveDateTime, 1000);  // Update every second
window.onload = updateLiveDateTime;  // Update when the page loads

// Function to enter fullscreen mode
function enterFullscreen() {
    if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen();
    } else if (document.documentElement.mozRequestFullScreen) { // Firefox
        document.documentElement.mozRequestFullScreen();
    } else if (document.documentElement.webkitRequestFullscreen) { // Chrome, Safari
        document.documentElement.webkitRequestFullscreen();
    } else if (document.documentElement.msRequestFullscreen) { // IE/Edge
        document.documentElement.msRequestFullscreen();
    }

    // Show the exit button and hide the enter button
    enterFullscreenButton.style.display = "none";
    exitFullscreenButton.style.display = "inline-block";
}

// Function to exit fullscreen mode
function exitFullscreen() {
    if (document.exitFullscreen) {
        document.exitFullscreen();
    } else if (document.mozCancelFullScreen) { // Firefox
        document.mozCancelFullScreen();
    } else if (document.webkitExitFullscreen) { // Chrome, Safari
        document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) { // IE/Edge
        document.msExitFullscreen();
    }

    // Show the enter button and hide the exit button
    enterFullscreenButton.style.display = "inline-block";
    exitFullscreenButton.style.display = "none";
}

function updateLiveDateTime() {
            const today = new Date();

            // Get and format date as day/month/year
            const day = today.getDate().toString().padStart(2, '0');
            const month = (today.getMonth() + 1).toString().padStart(2, '0');
            const year = today.getFullYear();
            const formattedDate = `${day}/${month}/${year}`;
            document.getElementById('liveDate').innerHTML = formattedDate;

            // Get and format time as HH:MM:SS
            const hours = today.getHours().toString().padStart(2, '0');
            const minutes = today.getMinutes().toString().padStart(2, '0');
            const period = hours >= 12 ? 'PM' : 'AM';
            const formattedTime = `${hours}:${minutes} ${period}`;
            document.getElementById('liveTime').innerHTML = formattedTime;
        }

        const navLinks = document.querySelectorAll('.nav-list li a');

navLinks.forEach(link => {
    link.addEventListener('click', function() {
        // Remove active class from all links
        navLinks.forEach(link => link.classList.remove('active'));

        // Add active class to the clicked link
        this.classList.add('active');
    });
});

function showMessage() {
    // Show the message
    const messageDiv = document.getElementById("message");
    messageDiv.style.display = "block"; // Make it visible

    // Hide the message after 7 seconds
    setTimeout(() => {
        messageDiv.style.display = "none";
    }, 7000); // 7000 milliseconds = 4 seconds
}




function initializeSPA() {
    const section = window.location.hash.substring(1) || 'home';
    showSection(section);
    window.onpopstate = function(event) {
        if (event.state && event.state.section) {
            showSection(event.state.section);
        }
    };
}

function navigateTo(section) {
    showSection(section);
    history.pushState({ section: section }, '', `#${section}`);
}

function showSection(section) {
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(sec => sec.style.display = 'none');
    const activeSection = document.getElementById(`${section}Section`);
    if (activeSection) {
        activeSection.style.display = 'block';
    }
    document.querySelectorAll('.nav-list a').forEach(link => link.classList.remove('active'));
    const activeLink = document.getElementById(section);
    if (activeLink) {
        activeLink.classList.add('active');
    }
}

window.addEventListener('load', () => {
    const section = window.location.hash.substring(1) || 'home';
    showSection(section);
});
