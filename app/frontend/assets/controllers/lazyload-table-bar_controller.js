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
          let splitted = number.textContent.split('.')
          console.log(splitted)
          let end = parseInt(splitted[0])
          let isFloat = splitted.length > 1
          let floatStart = 0
          let floatEnd = isFloat ? parseInt(number.textContent.split('.')[1]) : 0

          let duration = 1000
          let startTimestamp = null
          let start = 0
          const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp
            const progress = Math.min((timestamp - startTimestamp) / duration, 1)
            let intNumber = Math.floor(progress * (end - start) + start)
            let floatNumber = Math.floor(progress * (floatEnd - floatStart) + floatStart)
            number.textContent = `${intNumber}` + (isFloat ? `,${floatNumber}` : ``)
            if (progress < 1) {
              window.requestAnimationFrame(step)
            }
          }
          window.requestAnimationFrame(step)
        })
      }
    })
  }

  disconnect() {
    observer.disconnect(this.element)
  }
}
