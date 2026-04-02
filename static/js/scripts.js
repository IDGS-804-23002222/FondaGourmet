document.addEventListener('DOMContentLoaded', () => {
    // Modal handling para usuarios (ejemplo)
    const modal = document.getElementById('modalUsuario');
    const btnNew = document.getElementById('nuevoUsuario');
    const span = modal ? modal.querySelector('.close') : null;
    if (btnNew && modal) {
        btnNew.onclick = () => modal.style.display = 'block';
        if (span) span.onclick = () => modal.style.display = 'none';
        window.onclick = (event) => {
            if (event.target == modal) modal.style.display = 'none';
        };
    }
});