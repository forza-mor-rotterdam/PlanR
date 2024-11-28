import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  initialize() {
    if (this.getBrowser().includes('safari')) {
      document.body.classList.add('css--safari')
    }

    this.toastTurboFrame = document.getElementById('tf_toast_lijst')
    this.notificationsTurboFrameReloadTimeout = null

    setTimeout(() => {
      document.addEventListener('turbo:frame-load', (event) => {
        event.preventDefault()
        if (![this.toastTurboFrame].includes(event.target)) {
          this.reloadNotificationsTurboFrame()
        }
      })
    }, 1000)
    document.addEventListener('turbo:frame-missing', (event) => {
      const {
        detail: { response, visit },
      } = event
      console.log(response)
      console.log(event)
      event.preventDefault()
      // visit(document.location.href)

      console.error('Content missing', response.url, visit)
      if (![this.toastTurboFrame].includes(event.target)) {
        this.reloadNotificationsTurboFrame()
      }
    })
  }
  reloadNotificationsTurboFrame() {
    if (!this.notificationsTurboFrameReloadTimeout && this.toastTurboFrame) {
      this.notificationsTurboFrameReloadTimeout = setTimeout(() => {
        this.toastTurboFrame.reload()
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
