let errorTime,
  errorURL,
  errorAgent,
  mailtoLink = null

document.body.classList.remove('no-js')

document.querySelector('#showAction').addEventListener('click', () => {
  const containers = document.querySelectorAll('.container__error')

  containers.forEach((container) => {
    container.classList.toggle('show')
  })
})

document.querySelector('#sendEmail').addEventListener('click', (e) => {
  e.target.classList.add('disabled')
  document.querySelector('.btn-action-v2.hidden').classList.remove('hidden')
})

const getCurrentDate = () => {
  const today = new Date()
  const date = `${today.getDate()}-${
    today.getMonth() + 1
  }-${today.getFullYear()}, ${today.getHours()}:${today.getMinutes()} (Computertijd)`
  return date
}

document.querySelector('#sendEmail').addEventListener('click', (e) => {
  e.preventDefault()
  window.location.href = mailtoLink
})

window.onload = () => {
  errorAgent = navigator.userAgent
  errorTime = getCurrentDate()
  errorURL = window.location.href
  mailtoLink = `${document
    .querySelector('#sendEmail')
    .getAttribute(
      'href'
    )}%0D%0ATijdstip van de foutmelding: ${errorTime}%0D%0AURL van de foutmelding: ${errorURL} %0D%0ABrowser: ${errorAgent} %0D%0A%0D%0AWellicht heb je nog meer informatie voor ons:%0D%0AKomt deze fout vaker voor:%0D%0AHeb je een patroon kunnen ontdekken:%0D%0AErvaren je collega’s dezelfde fout:%0D%0A %0D%0AHoe meer informatie we ontvangen, des te beter we de fout kunnen analyseren. Dank voor het melden van de fout.%0D%0A %0D%0A`

  if (
    document.querySelector('#errorTime') &&
    document.querySelector('#errorTime').textContent.trim().length === 0
  ) {
    document.querySelector('#errorTime').textContent = getCurrentDate()
  }
  if (
    document.querySelector('#errorURL') &&
    document.querySelector('#errorURL').textContent.trim().length === 0
  ) {
    document.querySelector('#errorURL').textContent = errorURL
  }
  if (
    document.querySelector('#errorAgent') &&
    document.querySelector('#errorAgent').textContent.trim().length === 0
  ) {
    document.querySelector('#errorAgent').textContent = errorAgent
  }
}
