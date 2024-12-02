import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['modal', 'modalBackdrop', 'uitleg', 'datumtijd']
  static values = {
    sessionShowTimerSeconds: String,
    sessionExpiryTimestamp: String,
    sessionExpiryMaxTimestamp: String,
    sessionExpireAfterLastActivityGracePeriod: String,
    sessionCheckItervalSeconds: String,
  }

  connect() {
    this.sessionCheckItervalSeconds = parseInt(this.sessionCheckItervalSecondsValue) * 1000
    this.sessionShowTimerSeconds = parseInt(this.sessionShowTimerSecondsValue) * 1000
    this.sessionExpiryTimestamp = parseInt(this.sessionExpiryTimestampValue) * 1000
    this.sessionExpiryMaxTimestamp = parseInt(this.sessionExpiryMaxTimestampValue) * 1000
    this.sessionExpireAfterLastActivityGracePeriod =
      parseInt(this.sessionExpireAfterLastActivityGracePeriodValue) * 1000
    this.sessionTimer()
  }

  openModal() {
    this.modalTarget.classList.add('show')
    this.modalBackdropTarget.classList.add('show')
    document.body.classList.add('show-modal')
  }

  closeModal() {
    window.location.reload(true)
    this.modalTarget.classList.remove('show')
    this.modalBackdropTarget.classList.remove('show')
    document.body.classList.remove('show-modal')
  }

  sessionTimer() {
    console.log(this.sessionCheckItervalSeconds)
    console.log(this.sessionShowTimerSeconds)
    console.log(this.sessionExpiryTimestamp)
    console.log(this.sessionExpiryMaxTimestamp)
    console.log(this.sessionExpireAfterLastActivityGracePeriod)
    this.timer = setInterval(() => this.onInterval(), this.sessionCheckItervalSeconds)
    this.onInterval()
    window.addEventListener('beforeunload', () => {
      clearInterval(this.timer)
      this.timer = null
    })
  }
  humanDuration(seconds) {
    const timeLeftHours = Math.floor(seconds / (60 * 60))
    const timeLeftMinutes = Math.floor((seconds / 60) % 60)
    const timeLeftSeconds = seconds % 60

    const timeLeftHoursHuman = timeLeftHours < 10 ? `0${timeLeftHours}` : `${timeLeftHours}`
    const timeLeftMinutesHuman = timeLeftMinutes < 10 ? `0${timeLeftMinutes}` : `${timeLeftMinutes}`
    const timeLeftSecondsHuman = timeLeftSeconds < 10 ? `0${timeLeftSeconds}` : `${timeLeftSeconds}`

    return `${timeLeftHoursHuman}:${timeLeftMinutesHuman}:${timeLeftSecondsHuman}`
  }
  disconnect() {
    clearInterval(this.timer)
    this.timer = null
  }
  onInterval() {
    const currentDate = new Date()
    const timeIsUp =
      this.sessionExpiryTimestamp + this.sessionExpireAfterLastActivityGracePeriod <=
      currentDate.getTime()
    const expiryTimestampTimeIsUp = this.sessionExpiryTimestamp <= currentDate.getTime()
    const timeIsUpMax = this.sessionExpiryMaxTimestamp <= currentDate.getTime()
    const timeLeft = parseInt(
      Math.abs(
        currentDate.getTime() -
          new Date(this.sessionExpiryTimestamp + this.sessionExpireAfterLastActivityGracePeriod)
      ) / 1000
    )
    const timeLeftMax = parseInt(
      Math.abs(currentDate.getTime() - new Date(this.sessionExpiryMaxTimestamp)) / 1000
    )
    const timeLeftTotal = timeLeft < timeLeftMax ? timeLeft : timeLeftMax

    const timeLeftHuman = this.humanDuration(timeLeftTotal)

    console.log('timeLeft: ', this.humanDuration(timeLeft))
    console.log('timeLeftMax: ', this.humanDuration(timeLeftMax))
    if (expiryTimestampTimeIsUp) {
      const uitleg =
        timeLeft < timeLeftMax
          ? `Vernieuw de pagina binnen ${timeLeftHuman}`
          : `Je wordt uitgelogd over ${timeLeftHuman}`
      this.uitlegTarget.textContent = uitleg

      if (timeIsUp || timeIsUpMax) {
        clearInterval(this.timer)
        this.uitlegTarget.textContent = 'Je bent uitgelogd.'
        //window.location.replace(`/login/?next=${document.location.pathname}`)
      }
    }
  }
}
