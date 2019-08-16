const pass = document.getElementById('pass'),
      pass_reap = document.getElementById('pass_reap'),
      err = document.querySelector('.err-mess'),
      createBtn = document.getElementById('create');

pass_reap.addEventListener('input',() => {
    if (pass_reap.value !== pass.value ) {
      err.classList.remove('d-none')
      createBtn.classList.add('d-none')
    }else{
      err.classList.add('d-none')
      createBtn.classList.remove('d-none')
    }
});
