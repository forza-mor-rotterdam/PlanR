// import { Controller } from '@hotwired/stimulus'
import Chart from '@stimulus-components/chartjs'
export default class extends Chart {
  static targets = ['canvas']
  connect() {
    super.connect()
  }

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
}
