import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static values = {
    niveau: String,
  }

  connect() {
    console.log(`Connect: ${this.identifier}`)
    this.element.controller = this
    this.manager = null
    if (this.hasNiveauValue) {
      const duration = this.niveauValue == 'error' ? 5000 : 3000
      setTimeout(() => {
        this.hideNotification()
      }, Number(duration))
    }
  }
  initializeManager(manager) {
    this.manager = manager
  }
  dispatchRedraw() {
    this.element.dispatchEvent(
      new CustomEvent('notificatieVerwijderd', {
        bubbles: true,
      })
    )
  }
  hideNotification() {
    const notificatie = this.element
    if (notificatie.classList.contains('notification')) {
      notificatie.classList.add('hide')
      setTimeout(() => {
        notificatie.remove()
      }, 500)
    }
  }
}
