

        // Open popup
        function openPopup(id) {
            document.getElementById('popup-' + id).style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }

        // Close popup
        function closePopup(id) {
            document.getElementById('popup-' + id).style.display = 'none';
            document.body.style.overflow = 'auto';
        }

        // Close popup when clicking outside content
        document.querySelectorAll('.popup-overlay').forEach(popup => {
            popup.addEventListener('click', function (e) {
                if (e.target === this) {
                    const id = this.id.split('-')[1];
                    closePopup(id);
                }
            });
        });
