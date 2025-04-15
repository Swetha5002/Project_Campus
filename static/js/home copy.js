function openPopup(id) {
    const popup = document.getElementById(`popup-${id}`);
    if (popup) {
        popup.style.display = 'flex';
    }
}

function closePopup(id) {
    const popup = document.getElementById(`popup-${id}`);
    if (popup) {
        popup.style.display = 'none';
    }
}
