import { Controller } from '@hotwired/stimulus'

let observer = null

export default class extends Controller {
  initialize() {
    let options = {
      root: null,
      rootMargin: '0px',
      threshold: 0.6,
    }
    observer = new IntersectionObserver(this.handleIntersect, options)
    observer.observe(this.element)
  }

  handleIntersect(entries) {
    entries.forEach((entry) => {
      if (entry.isIntersecting && !entry.target.classList.contains('in-viewport')) {
        entry.target.classList.add('in-viewport')
        const numbersToAnimate = entry.target.querySelectorAll('.animated')
        numbersToAnimate.forEach((number) => {
          let end = number.textContent
          let duration = 1000
          let startTimestamp = null
          let start = 0
          const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp
            const progress = Math.min((timestamp - startTimestamp) / duration, 1)
            number.textContent = Math.floor(progress * (end - start) + start)
            if (progress < 1) {
              window.requestAnimationFrame(step)
            }
          }
          window.requestAnimationFrame(step)
        })
        // observer.unobserve(entry.target)
      }
    })
  }

  disconnect() {
    observer.disconnect(this.element)
  }
}
