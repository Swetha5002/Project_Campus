document.addEventListener('DOMContentLoaded', function() {
    // View test details button functionality
    const viewDetailsButtons = document.querySelectorAll('.view-details');
    
    viewDetailsButtons.forEach(button => {
        button.addEventListener('click', function() {
            const testId = this.getAttribute('data-test-id');
            // Here you would typically fetch the test details via AJAX
            // For now, we'll just show an alert
            alert(`Viewing details for test ID: ${testId}\nThis would normally open a modal with detailed results.`);
            
            // In a real implementation, you might do something like:
            // fetch(`/api/test-results/${testId}/`)
            //     .then(response => response.json())
            //     .then(data => showTestDetailsModal(data))
            //     .catch(error => console.error('Error:', error));
        });
    });
    
    // Animation for stats cards
    const statCards = document.querySelectorAll('.stat-card');
    
    statCards.forEach((card, index) => {
        // Add slight delay for each card
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Function to show test details modal (would be used with AJAX)
function showTestDetailsModal(testData) {
    // This would populate and show a modal with the test details
    console.log('Showing test details:', testData);
    // Example:
    // const modal = new bootstrap.Modal(document.getElementById('testDetailsModal'));
    // document.getElementById('testDetailsTitle').textContent = testData.test_title;
    // document.getElementById('testDetailsScore').textContent = testData.score;
    // ... populate other fields ...
    // modal.show();
}