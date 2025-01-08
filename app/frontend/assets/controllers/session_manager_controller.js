import { Controller } from '@hotwired/stimulus'
import { renderStreamMessage } from '@hotwired/turbo'

export default class extends Controller {
  static targets = []
  static values = {
    snackItem: String,
    sessionExpiryTimestamp: String,
    sessionExpiryMaxTimestamp: String,
    sessionExpiryMaxTimestampCookieName: String,
    sessionExpiryTimestampCookieName: String,
    sessionExpiryNotificationPeriod: String,
    sessionExpiryMaxNotificationPeriod: String,
    sessionExpireSeconds: String,
    sessionExpireAfterLastActivityGracePeriod: String,
  }

  connect() {
    this.sessieStatus = {
      verlengbaar: 'verlengbaar',
      nietVerlengbaar: 'nietVerlengbaar',
      bijnaUitgelogd: 'bijnaUitgelogd',
      uitgelogd: 'uitgelogd',
    }
    this.sessionProlongSeconds =
      parseInt(this.sessionExpireSecondsValue) +
      parseInt(this.sessionExpireAfterLastActivityGracePeriodValue)
    this.sessionTimer()
  }
  sessionTimer() {
    this.showSnack = true
    this.timer = setInterval(() => this.onInterval(), 1000)
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
  getCookieValue(name) {
    const regex = new RegExp(`(^| )${name}=([^;]+)`)
    const match = document.cookie.match(regex)
    if (match) {
      return match[2]
    }
  }
  disconnect() {
    clearInterval(this.timer)
    this.timer = null
  }
  sluitSnack() {
    this.showSnack = false
  }
  onInterval() {
    const time = new Date().getTime()
    const showNotificationPeriod = parseInt(this.sessionExpiryNotificationPeriodValue) * 1000
    const showMaxNotificationPeriod = parseInt(this.sessionExpiryMaxNotificationPeriodValue)
    const sessionExpiryMaxTimestamp =
      parseInt(this.getCookieValue(this.sessionExpiryMaxTimestampCookieNameValue)) * 1000
    const sessionExpiryTimestamp =
      parseInt(this.getCookieValue(this.sessionExpiryTimestampCookieNameValue)) * 1000

    const timeIsUp = sessionExpiryTimestamp <= time
    const timeIsUpMax = sessionExpiryMaxTimestamp <= time
    const timeLeft = parseInt(Math.abs(time - new Date(sessionExpiryTimestamp)) / 1000)
    const expiryTimestampTimeIsUp = sessionExpiryTimestamp - showNotificationPeriod <= time
    const expiryTimestampTimeIsUpMax = sessionExpiryMaxTimestamp - showNotificationPeriod <= time

    const timeLeftMax = parseInt(Math.abs(time - new Date(sessionExpiryMaxTimestamp)) / 1000)
    const timeLeftTotal = timeLeft < timeLeftMax ? timeLeft : timeLeftMax

    console.log('timeLeft: ', this.humanDuration(timeLeft))
    console.log('timeLeftMax: ', this.humanDuration(timeLeftMax))

    let snackItem = document.getElementById('notificatie_snack_sessie')
    if (expiryTimestampTimeIsUp || expiryTimestampTimeIsUpMax) {
      let status = this.sessieStatus.verlengbaar

      if (!snackItem && this.showSnack) {
        renderStreamMessage(this.snackItemValue)
        this.showSnack = true
      }
      snackItem = document.getElementById('notificatie_snack_sessie')
      const snackItemController = snackItem?.controllers['notificaties--sessie-snack-item']

      if (timeLeftMax < timeLeft && timeLeftMax < this.sessionProlongSeconds) {
        status = this.sessieStatus.nietVerlengbaar

        if (timeLeftMax < showMaxNotificationPeriod) {
          status = this.sessieStatus.bijnaUitgelogd
          this.showSnack = true
        }
      }

      if (timeIsUp || timeIsUpMax) {
        status = this.sessieStatus.uitgelogd
      }
      if (snackItemController) {
        snackItemController.setStatus(status, timeLeftTotal)
      }
      if (status === this.sessieStatus.uitgelogd) {
        clearInterval(this.timer)
      }
    } else {
      if (snackItem) {
        snackItem.remove()
      }
    }
  }
}
