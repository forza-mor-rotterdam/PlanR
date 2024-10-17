document.body.classList.remove('no-js')

document.querySelector('#showAction').addEventListener('click', () => {
  console.log('klik')
  const containers = document.querySelectorAll('.container__error')

  console.log('containers', containers)
  containers.forEach((container) => {
    container.classList.toggle('show')
  })
})
