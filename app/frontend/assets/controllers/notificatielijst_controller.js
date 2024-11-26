import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  connect() {
    this.setList(this.element.classList.value.includes('toast'))
    this.element.addEventListener('notificatieVerwijderd', () => {
      // wacht tot notificatie echt is verwijderd
      setTimeout(() => {
        this.resetList(this.element.classList.value.includes('toast'))
      }, 100)
      console.log(this.notificatieTargets.length)
    })
  }
  notificatieTargetConnected() {
    console.log(`item index: ${this.notificatieTargets.length}`)
    this.setList(this.element.classList.value.includes('toast'))
  }
  setList(isToast) {
    const list = this.notificatieTargets
    // eslint-disable-next-line for-direction
    for (let i = list.length - 1; i >= 0; i--) {
      setTimeout(
        () => {
          list[i].classList.add('init')
          if (i === 0) {
            this.element.classList.remove('busy')
          }
        },
        600 * (-i + list.length)
      )
    }

    setTimeout(() => {
      if (!this.element.classList.contains('expanded')) {
        this.element.classList.add('collapsed')
      }
    }, 5000)
  }
}
