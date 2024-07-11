// import { Controller } from '@hotwired/stimulus'
import Chart from '@stimulus-components/chartjs'

export default class extends Chart {
  static targets = ['canvas', 'received', 'done', 'open']
  connect() {
    super.connect()
    this.animateValue(this.receivedTarget, this.data.get('received'))
    this.animateValue(this.doneTarget, this.data.get('done'))
    this.animateValue(this.openTarget, this.data.get('open'))

    // The chart.js instance
    this.chart

    // Options from the data attribute.
    this.options

    // Default options for every charts.
    this.defaultOptions
  }

  // Bind an action on this method
  async update(e) {
    this.setActiveButton(e)

    const randomList = []
    for (let i = 0; i < this.chart.data.labels.length; i++) {
      randomList.push(this.getRandomInt())
    }

    this.chart.data.datasets[0].data = randomList
    this.chart.update()
  }

  getRandomInt() {
    const min = 50
    const max = 400
    const range = max - min
    const num = Math.floor(Math.random() * range + min)
    return num
  }

  setActiveButton(e) {
    console.log('setActiveButton', e)
    const button = e.target.closest('button')
    const buttonList = e.target.closest('li').parentNode.querySelectorAll('button')
    console.log('buttonList', buttonList)
    buttonList.forEach((element) => {
      element.classList.remove('active')
    })
    button.classList.add('active')
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

  // You can set default options in this getter for all your charts.
  get defaultOptions() {
    return {
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false,
        },
      },
      scales: {
        y: {
          min: 0,
          ticks: {
            stepSize: 100,
          },
        },
        x: {
          grid: {
            display: false,
          },
        },
      },
      animation: {
        easing: 'easeInOutSine',
      },
    }
  }
}
