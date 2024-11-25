import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  initialize() {
    if (this.getBrowser().includes('safari')) {
      document.body.classList.add('css--safari')
    }

    this.notificationsTurboFrame = document.getElementById('notificatie_lijst_public')
    this.profielNotificatiesTurboFrame = document.getElementById('tf_profiel_notificatie_lijst')
    this.notificationsTurboFrameReloadTimeout = null

    setTimeout(() => {
      document.addEventListener('turbo:frame-load', (event) => {
        event.preventDefault()
        if (
          ![this.notificationsTurboFrame, this.profielNotificatiesTurboFrame].includes(event.target)
        ) {
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
      if (
        ![this.notificationsTurboFrame, this.profielNotificatiesTurboFrame].includes(event.target)
      ) {
        this.reloadNotificationsTurboFrame()
      }
    })
  }
  reloadNotificationsTurboFrame() {
    if (!this.notificationsTurboFrameReloadTimeout && this.notificationsTurboFrame) {
      this.notificationsTurboFrameReloadTimeout = setTimeout(() => {
        // this.notificationsTurboFrame.reload()
        // this.profielNotificatiesTurboFrame.reload()
        this.notificationsTurboFrameReloadTimeout = null
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
