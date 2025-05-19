import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  initialize() {
    if (this.getBrowser().includes('safari') && !navigator.userAgent.includes('Chrome')) {
      document.body.classList.add('css--safari')
    }

    this.sessionTimerTurboFrame = document.getElementById('tf_session_timer')
    this.toastTurboFrame = document.getElementById('tf_toast_lijst')
    this.notificationsTurboFrameReloadTimeout = null

    // setTimeout(() => {

    document.addEventListener('turbo:fetch-request-error', (event) => {
      event.preventDefault()
      window.location.replace(`/login/?next=${document.location.pathname}`)
    })
    document.addEventListener('turbo:frame-load', (event) => {
      if (![this.toastTurboFrame, this.sessionTimerTurboFrame].includes(event.target)) {
        // this.reloadNotificationsTurboFrame()
      }
    })
    // document.addEventListener('turbo:before-stream-render', (event) => {
    //     console.log('turbo:before-stream-render', event.detail)
    //     this.reloadNotificationsTurboFrame()
    // })
    // }, 1000)
    document.addEventListener('turbo:frame-missing', (event) => {
      const {
        detail: { response, visit },
      } = event
      console.log(response)
      console.log(event)
      event.preventDefault()
      // visit(document.location.href)

      console.error('Content missing', response.url, visit)
      if (![this.toastTurboFrame, this.sessionTimerTurboFrame].includes(event.target)) {
        this.reloadNotificationsTurboFrame()
      }
    })
  }
  reloadNotificationsTurboFrame() {
    if (!this.notificationsTurboFrameReloadTimeout) {
      this.notificationsTurboFrameReloadTimeout = setTimeout(() => {
        try {
          // this.toastTurboFrame?.reload()
          this.sessionTimerTurboFrame?.reload()
          this.notificationsTurboFrameReloadTimeout = null
        } catch (e) {
          console.error('reloadNotificationsTurboFrame error: ', e)
        }
      }, 4000)
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
