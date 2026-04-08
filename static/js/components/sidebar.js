const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const sidebar = document.getElementById('sidebar');

if (mobileMenuToggle && sidebar) {
    mobileMenuToggle.addEventListener('click', (event) => {
        event.preventDefault();
        sidebar.classList.toggle('show');
    });
}

// cerrar al hacer click fuera
document.addEventListener('click', (event) => {
    if (window.innerWidth <= 768 && sidebar && mobileMenuToggle) {
        const isClickInsideSidebar = sidebar.contains(event.target);
        const isClickOnToggle = mobileMenuToggle.contains(event.target);

        if (!isClickInsideSidebar && !isClickOnToggle) {
            sidebar.classList.remove('show');
        }
    }
});
