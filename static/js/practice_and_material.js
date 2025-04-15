function filterMaterials() {
    const searchBar = document.querySelector('.search-bar');
    const filter = searchBar.value.toLowerCase();
    const cards = document.querySelectorAll('.card');

    cards.forEach(card => {
        const name = card.getAttribute('data-name').toLowerCase();
        if (name.includes(filter)) {
            card.classList.remove('hidden');
        } else {
            card.classList.add('hidden');
        }
    });
}