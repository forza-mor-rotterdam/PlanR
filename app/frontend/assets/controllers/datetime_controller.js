import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static values = {
    dateObject: String,
  }

  static targets = ['timeHoursMinutes']

  connect() {
    const dateObject = new Date(this.data.get('dateObjectValue'))
    const minutes =
      dateObject.getMinutes() < 10 ? `0${dateObject.getMinutes()}` : dateObject.getMinutes()
    const time = `${dateObject.getHours()}:${minutes}`

    if (this.hasTimeHoursMinutesTarget) {
      this.timeHoursMinutesTarget.textContent = time
    }
  }
}
