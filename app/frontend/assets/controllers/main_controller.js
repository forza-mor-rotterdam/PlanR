import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  initialize() {
    if (this.getBrowser().includes('safari')) {
      document.body.classList.add('css--safari')
    }

    this.notificationsTurboFrame = document.getElementById('notificatie_lijst_public')
    this.sessionTimerTurboFrame = document.getElementById('tf_session_timer')
    this.notificationsTurboFrameReloadTimeout = null

    setTimeout(() => {
      document.addEventListener('turbo:fetch-request-error', (event) => {
        event.preventDefault()
        window.location.replace(`/login/?next=${document.location.pathname}`)
      })
      document.addEventListener('turbo:frame-load', (event) => {
        event.preventDefault()
        if (![this.notificationsTurboFrame, this.sessionTimerTurboFrame].includes(event.target)) {
          this.reloadNotificationsTurboFrame()
        }
      })
    }, 1000)
    document.addEventListener('turbo:frame-missing', (event) => {
      const {
        detail: { response, visit },
      } = event
      event.preventDefault()
      console.error('Content missing', response.url, visit)
      if (![this.notificationsTurboFrame, this.sessionTimerTurboFrame].includes(event.target)) {
        this.reloadNotificationsTurboFrame()
      }
    })
  }
  reloadNotificationsTurboFrame() {
    if (!this.notificationsTurboFrameReloadTimeout) {
      this.notificationsTurboFrameReloadTimeout = setTimeout(() => {
        try {
          this.notificationsTurboFrame?.reload()
          this.sessionTimerTurboFrame?.reload()
          this.notificationsTurboFrameReloadTimeout = null
        } catch (e) {
          console.error('reloadNotificationsTurboFrame error: ', e)
        }
      }, 200)
    }
  }

  getBrowser() {
    let userAgent = navigator.userAgent
    let browser = 'onbekend'
    if (/Safari/.test(userAgent)) {
      browser = 'safari'
    }
    return browser
  }
}
