// import { Controller } from '@hotwired/stimulus'
import Chart from '@stimulus-components/chartjs'
export default class extends Chart {
  static targets = ['canvas', 'percentage', 'percentagePill']
  connect() {
    super.connect()

    const w1 = this.percentageTarget.offsetWidth + 2
    const w2 = this.percentagePillTarget.offsetWidth + 2
    this.percentageTarget.setAttribute('style', `width: ${w1}px;`)
    this.percentagePillTarget.setAttribute('style', `width: ${w2}px;`)
    this.animateValue(this.percentageTarget, this.data.get('percentage'))
    this.animateValue(this.percentagePillTarget, this.data.get('percentage'))

    // The chart.js instance
    this.chart

    // Options from the data attribute.
    this.options

    // Default options for every charts.
    this.defaultOptions
  }

  // You can set default options in this getter for all your charts.
  get defaultOptions() {
    return {
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false,
        },
      },
      circumference: 180,
      rotation: -90,
      cutout: '95%',
      borderWidth: 6,
      aspectRatio: 1.5,
      animation: {
        easing: 'easeInOutSine',
      },
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
