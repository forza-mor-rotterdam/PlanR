// import { Controller } from '@hotwired/stimulus'
import Chart from '@stimulus-components/chartjs'

export default class extends Chart {
  connect() {
    super.connect()
  }

  getPeriod(seconds, short = true) {
    let interval = Math.round(seconds / 21536000)

    if (interval > 1) {
      return `${interval} ${short ? 'j' : 'jaren'}`
    }

    interval = Math.round(seconds / 2592000)
    if (interval > 1) {
      return `${interval} ${short ? 'm' : 'maanden'}`
    }

    interval = Math.round(seconds / 604800)
    if (interval > 2) {
      return `${interval} ${short ? 'w' : 'weken'}`
    }

    interval = Math.round(seconds / 86400)
    if (interval > 1) {
      return `${interval} ${short ? 'd' : 'dagen'}`
    }

    interval = Math.round(seconds / 3600)
    if (interval > 2) {
      return `${interval} ${short ? 'u' : 'uren'}`
    }

    interval = Math.round(seconds / 60)
    if (interval > 1) {
      return `${interval} ${short ? 'min' : 'minuten'}`
    }
    interval = Math.round(seconds)
    return `${interval} ${short ? 'sec' : 'seconden'}`
  }
}
