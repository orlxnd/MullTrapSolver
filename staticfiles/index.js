document.addEventListener('DOMContentLoaded', function() {
    // Obtiene la referencia del de alternar contraseña por su id
    const togglePassword = document.getElementById('togglePassword');
    // Obtiene la referencia al campo de contraseña por su id
    const password = document.getElementById('password');

    //evento de clic del btn de alternar contraseña
    togglePassword.addEventListener('click', function() {
        // Obtiene el tipo actual del campo de contraseña 
        const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
        // Cambia el tipo del campo de contraseña al tipo opuesto obtenido
        password.setAttribute('type', type);
        // Alterna la clase active en el btn de alternar 
        this.classList.toggle('active');
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // btn contraseña 2
    const togglePassword1 = document.getElementById('togglePassword1');
    const password1 = document.getElementById('password1');
    
    togglePassword1.addEventListener('click', function() {
        const type = password1.getAttribute('type') === 'password' ? 'text' : 'password';
        password1.setAttribute('type', type);
        this.classList.toggle('active');
    });
    
    // btn contraseña 2
    const togglePassword2 = document.getElementById('togglePassword2');
    const password2 = document.getElementById('password2');
    
    togglePassword2.addEventListener('click', function() {
        const type = password2.getAttribute('type') === 'password' ? 'text' : 'password';
        password2.setAttribute('type', type);
        this.classList.toggle('active');
    });

    //validacion contraseña
    const form = document.querySelector('form');
    
    form.addEventListener('submit', function(event) {
        const passwordValue1 = password1.value.trim();
        const passwordValue2 = password2.value.trim();
        
        if (passwordValue1 !== passwordValue2) {
            alert("Las contraseñas no coinciden");
            event.preventDefault(); //evitar que se envíe el formulario
        }
        
        //contraseña mayor de 8 caracteres
        if (passwordValue1.length < 8) {
            alert("La contraseña debe tener al menos 8 caracteres");
            event.preventDefault(); 
        }

         //al menos una letra mayuscula
         const uppercaseRegex = /[A-Z]/;
         if (!uppercaseRegex.test(passwordValue1)) {
             alert("La contraseña debe tener al menos una letra mayuscula");
             event.preventDefault(); 
             return;
         }
        
         //al menos un caracter especial
        const specialCharRegex = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/;
        if (!specialCharRegex.test(passwordValue1)) {
            alert("La contraseña debe tener al menos un caracter especial (!, @, #, etc.)");
            event.preventDefault(); 
            return;
        }
    });
});

