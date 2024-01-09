import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static values = {
    dateObject: String,
  }

  static targets = ['timeHoursMinutes', 'resolutie']

  connect() {
    const dateObject = new Date(this.data.get('dateObjectValue'))
    const minutes =
      dateObject.getMinutes() < 10 ? `0${dateObject.getMinutes()}` : dateObject.getMinutes()
    const time = `${dateObject.getHours()}:${minutes}`

    if (this.hasTimeHoursMinutesTarget) {
      this.timeHoursMinutesTarget.textContent = time
    }

    if (this.hasResolutieTarget) {
      if (this.resolutieTarget.innerHTML.toLowerCase() !== 'opgelost') {
        this.resolutieTarget.closest('details').open = true
      }
    }
  }
}
