// import { Controller } from '@hotwired/stimulus'
import Chart from '@stimulus-components/chartjs'
import 'chartjs-adapter-moment'
// import {nl} from 'date-fns/locale';
import * as moment from 'moment'

export default class extends Chart {
  static targets = ['canvas', 'button']
  static values = {
    yTicks: String,
  }
  connect() {
    super.connect()
    this.chart.update()
  }
  initialize() {
    this.ticks = {
      y: {
        default: {
          count: 8,
          stepSize: 100,
        },
        duration: {
          count: 8,
          stepSize: 60 * 60,
          beginAtZero: true,
          callback: (value) => {
            let m = moment.duration(value, 'seconds')
            return m.locale('nl').humanize(false)
          },
        },
      },
    }
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
  getTicks() {
    console.log(this.identifier)
    console.log(this.ticks)
    return this.ticks.y[this.hasYTicksValue ? this.yTicksValue : 'default']
  }

  get defaultOptions() {
    return {
      // maintainAspectRatio: true,
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
          ticks: this.getTicks(),
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
