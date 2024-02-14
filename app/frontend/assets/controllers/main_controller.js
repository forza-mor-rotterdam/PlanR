import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  initialize() {
    if (this.getBrowser().includes('safari')) {
      document.body.classList.add('css--safari')
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
