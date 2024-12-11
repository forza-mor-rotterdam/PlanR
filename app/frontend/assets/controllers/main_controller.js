import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  initialize() {
    if (this.getBrowser().includes('safari')) {
      document.body.classList.add('css--safari')
    }

    this.sessionTimerTurboFrame = document.getElementById('tf_session_timer')
    this.toastTurboFrame = document.getElementById('tf_toast_lijst')
    this.notificationsTurboFrameReloadTimeout = null

    document.addEventListener('turbo:fetch-request-error', (event) => {
      event.preventDefault()
      window.location.replace(`/login/?next=${document.location.pathname}`)
    })

    setTimeout(() => {
      document.addEventListener('turbo:frame-load', (event) => {
        if (![this.toastTurboFrame, this.sessionTimerTurboFrame].includes(event.target)) {
          this.reloadNotificationsTurboFrame()
        }
        console.log(this.getCookieValue('_session_init_timestamp_'))
        console.log(this.getCookieValue('_session_current_timestamp_'))
      })
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
    }, 1000)
  }
  getCookieValue(name) {
    const regex = new RegExp(`(^| )${name}=([^;]+)`)
    const match = document.cookie.match(regex)
    if (match) {
      return match[2]
    }
  }
  reloadNotificationsTurboFrame() {
    if (!this.notificationsTurboFrameReloadTimeout) {
      this.notificationsTurboFrameReloadTimeout = setTimeout(() => {
        try {
          this.toastTurboFrame?.reload()
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
