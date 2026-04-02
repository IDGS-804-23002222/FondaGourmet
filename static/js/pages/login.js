document.querySelectorAll('.toggle-password').forEach(btn => {
    btn.addEventListener('click', function () {
        const input = this.parentElement.querySelector('input');
        const icon = this.querySelector('i');

        if (input.type === "password") {
            input.type = "text";
            icon.classList.replace("bi-eye", "bi-eye-slash");
        } else {
            input.type = "password";
            icon.classList.replace("bi-eye-slash", "bi-eye");
        }
    });
});
