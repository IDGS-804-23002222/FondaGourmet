const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const sidebar = document.getElementById('sidebar');

if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', () => {
        sidebar.classList.toggle('show');
    });
}

// cerrar al hacer click fuera
document.addEventListener('click', (event) => {
    if (window.innerWidth <= 768) {
        const isClickInsideSidebar = sidebar.contains(event.target);
        const isClickOnToggle = mobileMenuToggle.contains(event.target);

        if (!isClickInsideSidebar && !isClickOnToggle) {
            sidebar.classList.remove('show');
        }
    }
});
