let errorTime,
  errorURL,
  errorAgent = null
// let mailtoLink =
// 'mailto:productowner-morsb@rotterdam.nl?subject=Interne serverfout: 500&body=Type foutmelding: Interne serverfout 500, PlanR {{ server_id }}%0D%0ATijdstip van de foutmelding: {{ current_time }}%0D%0AURL van de foutmelding: {{ path }}%0D%0ABrowser: {{ user_agent }}%0D%0A%0D%0AWellicht heb je nog meer  informatie voor ons:%0D%0AKomt deze fout vaker voor:%0D%0AHeb je een patroon kunnen ontdekken:%0D%0AErvaren je collega’s dezelfde fout:%0D%0A %0D%0AHoe meer informatie we ontvangen, des te beter we de fout kunnen analyseren. Dank voor het melden van de fout.%0D%0A %0D%0A'

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
  }-${today.getFullYear()}, ${today.getHours()}:${today.getMinutes()}`
  return date
}

window.onload = () => {
  // setvars
  errorAgent = navigator.userAgent
  errorTime = getCurrentDate()
  errorURL = window.location.href
  console.log('agent', errorAgent)
  console.log('time', errorTime)
  console.log('url', errorURL)
  console.log('hostname', window.location.hostname)
  console.log('pathname', window.location.pathname)

  if (document.querySelector('#errorTime').textContent.length === 0) {
    document.querySelector('#errorTime').textContent = getCurrentDate()
  }
  if (document.querySelector('#errorURL').textContent.length === 0) {
    document.querySelector('#errorURL').textContent = errorURL
  }
  if (document.querySelector('#errorAgent').textContent.length === 0) {
    document.querySelector('#errorAgent').textContent = errorAgent
  }
}
