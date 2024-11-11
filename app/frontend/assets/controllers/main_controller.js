import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  initialize() {
    if (this.getBrowser().includes('safari')) {
      document.body.classList.add('css--safari')
    }

    const observerOptions = {
      childList: true,
      subtree: true,
    }

    this.notificationsTurboFrame = document.getElementById('notificatie_lijst_public')
    this.notificationsTurboFrameReloadTimeout = null

    setTimeout(() => {
      const observer = new MutationObserver((records) => {
        const turboFrames = records
          .filter(
            (record) => record?.target?.nodeName == 'TURBO-FRAME' && record?.addedNodes.length > 0
          )
          .map((record) => record)
        if (turboFrames.length > 0) {
          this.reloadNotificationsTurboFrame()
        }
      })
      observer.observe(this.element, observerOptions)
    }, 1000)

    document.addEventListener('turbo:frame-missing', (event) => {
      const {
        detail: { response, visit },
      } = event
      event.preventDefault()
      console.error('Content missing', response.url, visit)
      this.reloadNotificationsTurboFrame()
    })
  }
  reloadNotificationsTurboFrame() {
    if (!this.notificationsTurboFrameReloadTimeout && this.notificationsTurboFrame) {
      this.notificationsTurboFrameReloadTimeout = setTimeout(() => {
        this.notificationsTurboFrame.reload()
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
