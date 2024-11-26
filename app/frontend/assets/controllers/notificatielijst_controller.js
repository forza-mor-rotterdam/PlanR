import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['notificatie']

  connect() {
    if (!this.element.classList.value.includes('toast')) {
      this.element.addEventListener('mouseover', () => {
        this.element.classList.remove('collapsed')
        this.element.classList.add('expanded')
      })
      this.element.addEventListener('mouseleave', () => {
        this.element.classList.remove('expanded')
        this.element.classList.add('collapsed')
      })
      setTimeout(() => {
        if (!this.element.classList.contains('expanded')) {
          this.element.classList.add('collapsed')
        }
      }, 5000)
    }
  }
}
