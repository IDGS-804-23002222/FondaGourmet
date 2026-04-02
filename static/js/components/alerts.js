document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('#alerts-container .alert');

    alerts.forEach(function (alert) {
        // Auto cerrar después de 5 segundos
        setTimeout(function () {
            if (alert && alert.parentNode) {
                // Animación de salida suave
                alert.style.transition = 'all 0.4s ease';
                alert.style.opacity = '0';
                alert.style.transform = 'translateX(30px)';

                setTimeout(function () {
                    if (alert.parentNode) alert.remove();
                }, 400);
            }
        }, 5000);   // 5 segundos
    });
});