// import { Controller } from '@hotwired/stimulus'
import Chart from '@stimulus-components/chartjs'

export default class extends Chart {
  connect() {
    super.connect()
  }

  getPeriod(seconds) {
    let interval = Math.round(seconds / 21536000)

    if (interval > 1) {
      return interval + 'jaar'
    }

    interval = Math.round(seconds / 2592000)
    if (interval > 1) {
      return `${interval} maanden`
    }

    interval = Math.round(seconds / 604800)
    if (interval > 2) {
      return `${interval} weken`
    }

    interval = Math.round(seconds / 86400)
    if (interval > 1) {
      return `${interval} dagen`
    }

    interval = Math.round(seconds / 3600)
    if (interval > 2) {
      return `${interval} uren`
    }

    interval = Math.round(seconds / 60)
    if (interval > 1) {
      return `${interval} minuten`
    }
    interval = Math.round(seconds)
    return `${interval} seconden`
  }
}
