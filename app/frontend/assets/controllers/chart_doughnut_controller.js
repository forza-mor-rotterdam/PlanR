// import { Controller } from '@hotwired/stimulus'
import Chart from '@stimulus-components/chartjs'

export default class extends Chart {
  static targets = ['canvas']
  connect() {
    super.connect()

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
    }
  }
}
