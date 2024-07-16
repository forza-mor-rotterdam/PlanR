// import { Controller } from '@hotwired/stimulus'
import Chart from '@stimulus-components/chartjs'

const maandArray = [
  'januari',
  'februari',
  'maart',
  'april',
  'mei',
  'juni',
  'juli',
  'augustus',
  'september',
  'oktober',
  'november',
  'december',
]

export default class extends Chart {
  static targets = ['canvas']
  connect() {
    super.connect()

    const nu = new Date()
    var maandtekst = maandArray[nu.getMonth()]
    const labels = []
    for (let i = 6; i >= 0; i--) {
      const date = new Date(nu.getFullYear(), nu.getMonth(), nu.getDate() - i)
      labels.push(`${date.getDate()} ${maandtekst}`)
    }

    this.chart.data.labels = labels
    this.chart.update()
  }

  async update(e) {
    this.setActiveButton(e)
    const newData = e.params.newdata.split(',')
    this.chart.data.datasets[0].data = newData
    this.chart.data.datasets[0].label = e.target.querySelector('.decorated').textContent
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
        xAxes: [
          {
            type: 'time',
            time: {
              min: this.start,
              max: this.end,
              unit: 'day',
            },
          },
        ],
      },
      animation: {
        easing: 'easeInOutSine',
      },
    }
  }
}
