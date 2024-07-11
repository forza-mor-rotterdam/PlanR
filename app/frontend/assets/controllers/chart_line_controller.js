// import { Controller } from '@hotwired/stimulus'
import Chart from '@stimulus-components/chartjs'

export default class extends Chart {
  static targets = ['canvas']
  connect() {
    super.connect()
    console.log('Do what you want here.')

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
    }
  }
}
