console.log('jslinkedd frfrfrfrfr');

// Example starter JavaScript for disabling form submissions if there are invalid fields
(() => {
  'use strict'

  // Fetch all the forms we want to apply custom Bootstrap validation styles to
  const forms = document.querySelectorAll('.needs-validation')

  // Loop over them and prevent submission
  Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {

      let hiddenElements = document.querySelector('.hidden-elm')

      hiddenElements.style.visibility = "visible"

      let hiddenAlert = document.querySelector('.alert-danger')

      hiddenAlert.style.visibility = "visible"

      if (!form.checkValidity()) {
        event.preventDefault()
        event.stopPropagation()
      }

      form.classList.add('was-validated')

      
    }, false)
  })
})()


