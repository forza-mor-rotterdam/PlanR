import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['modal', 'modalBackdrop']
  static values = {
    session_expiry_timestamp: String,
    session_expiry_max_timestamp: String,
  }

  connect() {
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
    const self = this
    const sessionExpiryTimestamp = parseInt(this.sessionExpiryTimestampValue) * 1000
    const sessionExpiryMaxTimestamp = parseInt(this.sessionExpiryMaxTimestampValue) * 1000
    var timer = setInterval(function () {
      const currentDate = new Date()
      const timeIsUp = sessionExpiryTimestamp <= parseInt(parseInt(currentDate.getTime()))
      const timeIsUpMax = sessionExpiryMaxTimestamp <= parseInt(parseInt(currentDate.getTime()))
      if (timeIsUp || timeIsUpMax) {
        clearInterval(timer)
        self.openModal()
      }
    }, 1000 * 60)
  }
}
