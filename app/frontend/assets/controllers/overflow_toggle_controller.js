import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static classes = ['item']
  static targets = ['container', 'toggle']

  connect() {
    const items = this.element.querySelectorAll(`.${this.itemClass}`)
    items.forEach((item) => {
      item.style.webkitLineClamp = '6'
      item.addEventListener('transitionend', () => {
        if (!this.containerTarget.classList.contains('is-expanded')) {
          item.style.webkitLineClamp = '6'
        }
      })
    })

    const overflowDetected = Array.from(items).some((item) => item.scrollHeight > item.offsetHeight)
    if (overflowDetected) {
      this.containerTarget.classList.add('has-overflow')
    }
    if (overflowDetected && this.hasToggleTarget) {
      this.toggleTarget.hidden = false
    }
  }

  toggle() {
    const items = this.element.querySelectorAll(`.${this.itemClass}`)
    const expanded = this.containerTarget.classList.toggle('is-expanded')

    items.forEach((item) => {
      this.containerTarget.classList.toggle('is-expanded', expanded)
      item.style.maxHeight = expanded ? `${item.scrollHeight}px` : '8rem'
      item.style.webkitLineClamp = expanded ? `unset` : ''
    })
  }
}
