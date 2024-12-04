import { Controller } from '@hotwired/stimulus'
import { renderStreamMessage } from '@hotwired/turbo'

export default class extends Controller {
  static targets = []
  static values = {
    snackItem: String,
    snackItemId: String,
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
    const timeIsUpMax = this.sessionExpiryMaxTimestamp <= currentDate.getTime()
    const timeLeft = parseInt(
      Math.abs(
        currentDate.getTime() -
          new Date(this.sessionExpiryTimestamp + this.sessionExpireAfterLastActivityGracePeriod)
      ) / 1000
    )
    const expiryTimestampTimeIsUp =
      this.sessionExpiryTimestamp + this.sessionExpireAfterLastActivityGracePeriod - 60000 <=
      currentDate.getTime()
    const expiryTimestampTimeIsUpMax =
      this.sessionExpiryMaxTimestamp - 60000 <= currentDate.getTime()
    const timeLeftMax = parseInt(
      Math.abs(currentDate.getTime() - new Date(this.sessionExpiryMaxTimestamp)) / 1000
    )
    const timeLeftTotal = timeLeft < timeLeftMax ? timeLeft : timeLeftMax

    const timeLeftHuman = this.humanDuration(timeLeftTotal)

    console.log('timeLeft: ', this.humanDuration(timeLeft))
    console.log('timeLeftMax: ', this.humanDuration(timeLeftMax))
    let snackItem = document.getElementById(this.snackItemIdValue)
    if (expiryTimestampTimeIsUp || expiryTimestampTimeIsUpMax) {
      const uitleg =
        timeLeft < timeLeftMax
          ? `Vernieuw de pagina binnen ${timeLeftHuman}`
          : `Je wordt uitgelogd over ${timeLeftHuman}`

      if (!snackItem) {
        renderStreamMessage(this.snackItemValue)
      }
      snackItem = document.getElementById(this.snackItemIdValue)
      if (snackItem) {
        snackItem.controller.contentTarget.textContent = uitleg
      }

      if (timeIsUp || timeIsUpMax) {
        if (snackItem) {
          snackItem.controller.contentTarget.remove()
          snackItem.controller.titelTarget.textContent = 'Je bent uitgelogd.'
        }
        clearInterval(this.timer)
      }
    } else {
      if (snackItem) {
        snackItem.remove()
      }
    }
  }
}
