import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['notificatie']

  static values = {
    duration: String,
  }

  connect() {
    if (this.hasDurationValue) {
      setTimeout(() => {
        this.hideNotification()
      }, Number(this.durationValue))
    }
  }

  hideNotification() {
    const notificatie = this.element
    notificatie.classList.add('hide')

    notificatie.addEventListener('transitionend', () => {
      if (notificatie.nodeName === 'TURBO-FRAME') {
        notificatie.setAttribute('src', notificatie.getAttribute('data-src'))
      }
      notificatie.dispatchEvent(
        new CustomEvent('notificatieVerwijderd', {
          bubbles: true,
        })
      )
      notificatie.remove()
    })
  }
}
