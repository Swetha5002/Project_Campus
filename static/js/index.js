function showSection(section) {
    // Hide all sections
    let sections = document.querySelectorAll('.content-section');
    sections.forEach(function (section) {
        section.style.display = 'none';
    });

    // Show the clicked section
    let activeSection = document.getElementById(section + 'Section');
    if (activeSection) {
        activeSection.style.display = 'block';
    }

    // Remove active class from all links
    let navLinks = document.querySelectorAll('.nav-list li a');
    navLinks.forEach(function (link) {
        link.classList.remove('active');
    });

    // Add active class to the clicked link
    let activeLink = document.getElementById(section);
    if (activeLink) {
        activeLink.classList.add('active');
    }
}

// Show the correct section based on the URL hash when the page loads
window.addEventListener('load', () => {
    const section = window.location.hash.substring(1) || 'home';
    showSection(section);
});
