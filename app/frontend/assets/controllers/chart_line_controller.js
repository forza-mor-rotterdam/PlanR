// import { Controller } from '@hotwired/stimulus'
import Chart from '@stimulus-components/chartjs'

export default class extends Chart {
  static targets = ['canvas']
  connect() {
    super.connect()
  }

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
    const button = e.target.closest('button')
    const buttonList = e.target.closest('li').parentNode.querySelectorAll('button')
    buttonList.forEach((element) => {
      element.classList.remove('active')
    })
    button.classList.add('active')
  }

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
