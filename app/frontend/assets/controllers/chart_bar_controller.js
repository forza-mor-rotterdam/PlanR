// import { Controller } from '@hotwired/stimulus'
import Chart from '@stimulus-components/chartjs'
export default class extends Chart {
  static targets = ['canvas']
  connect() {
    super.connect()
  }

  get defaultOptions() {
    return {
      maintainAspectRatio: false,
      backgroundColor: '#EAEEF1',
      hoverBackgroundColor: '#FFF1CE',
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
        x: {
          display: false,
        },
        y: {
          display: false,
        },
      },
    }
  }
}
