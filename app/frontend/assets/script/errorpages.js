document.body.classList.remove('no-js')

document.querySelector('#showAction').addEventListener('click', () => {
  console.log('klik')
  const containers = document.querySelectorAll('.container__error')

  containers.forEach((container) => {
    container.classList.toggle('show')
  })
})

document.querySelector('#sendEmail').addEventListener('click', (e) => {
  console.log(e.target)
  e.target.classList.add('disabled')
  document.querySelector('.btn-action-v2.hidden').classList.remove('hidden')
})
