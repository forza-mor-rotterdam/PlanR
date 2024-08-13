// import { Controller } from '@hotwired/stimulus'
import Chart from '@stimulus-components/chartjs'

export default class extends Chart {
  static targets = ['canvas', 'button']
  connect() {
    super.connect()
    this.chart.update()
  }

  async update(e) {
    this.setActiveButton(e)
    console.log(e.params.datasets)
    this.chart.data.datasets = e.params.datasets
    this.chart.update()
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
        tooltip: {
          backgroundColor: '#ffffff',
          borderColor: 'rgba(0, 0 ,0 , .8)',
          borderWidth: 1,
          bodyAlign: 'center',
          bodyColor: '#000000',
          titleColor: '#000000',
          titleAlign: 'center',
          displayColors: false,
          borderRadius: 0,
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
