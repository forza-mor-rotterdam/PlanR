import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['numbersReceived', 'numbersDone', 'numbersNotDone', 'numbersOpen']
  connect() {
    if (this.hasNumbersDoneTarget) {
      this.animateValue(this.numbersReceivedTarget, this.data.get('received'))
      this.animateValue(this.numbersDoneTarget, this.data.get('done'))
      this.animateValue(this.numbersNotDoneTarget, this.data.get('notDone'))
      this.animateValue(this.numbersOpenTarget, this.data.get('open'))
    }
  }

  animateValue(object, end, duration = 1000) {
    let startTimestamp = null
    let start = 0
    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp
      const progress = Math.min((timestamp - startTimestamp) / duration, 1)
      object.innerHTML = Math.floor(progress * (end - start) + start)
      if (progress < 1) {
        window.requestAnimationFrame(step)
      }
    }
    window.requestAnimationFrame(step)
  }
}
