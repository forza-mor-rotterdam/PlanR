import { Controller } from '@hotwired/stimulus'

let observer = null
export default class extends Controller {
  initialize() {
    // eslint-disable-next-line no-unused-vars
    observer = new IntersectionObserver((entries, { rootMargin = '0', treshold = 0.6 }) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          this.element.classList.add('in-viewport')
        }
      })
    })
    observer.observe(this.element)
  }

  disconnect() {
    observer.disconnect(this.element)
  }
}
