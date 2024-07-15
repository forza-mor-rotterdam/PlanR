import { Controller } from '@hotwired/stimulus'

let dataValue = null

export default class extends Controller {
  static targets = ['percentageHeader', 'percentageLabel', 'bar', 'wrapper']

  connect() {
    dataValue = this.data.get('percentage')

    if (this.hasWrapperTarget) {
      this.wrapperTarget.setAttribute('style', `max-width:${dataValue}%`)
    }
    if (this.hasBarTarget) {
      this.barTarget.setAttribute('style', `max-width:${dataValue}%`)
    }
    if (this.hasPercentageHeaderTarget) {
      this.animateValue(this.percentageHeaderTarget, dataValue)
    }
    if (this.hasPercentageLabelTarget) {
      this.animateValue(this.percentageLabelTarget, dataValue)
    }
  }

  animateValue(object, end, duration = 1000) {
    let startTimestamp = null
    let start = 0
    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp
      const progress = Math.min((timestamp - startTimestamp) / duration, 1)
      object.innerHTML = Math.floor(progress * (end - start) + start)
      if (progress < 1) {
        window.requestAnimationFrame(step)
      }
    }
    window.requestAnimationFrame(step)
  }
}
