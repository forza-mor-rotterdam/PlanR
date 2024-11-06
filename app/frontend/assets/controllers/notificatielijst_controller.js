import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['notificatie']

  connect() {
    const list = this.notificatieTargets
    // eslint-disable-next-line for-direction
    for (let i = list.length - 1; i >= 0; i--) {
      setTimeout(
        () => {
          list[i].classList.add('init')
        },
        200 * (i - list.length)
      )
      setTimeout(
        () => {
          list[i].classList.replace('init', 'show')
        },
        2000 + 100 * (-i + list.length)
      )
    }
  }

  hideNotification(e) {
    const notification = e.target.closest('.notification')
    notification.classList.add('hide')

    notification.addEventListener('transitionend', () => {
      notification.remove()
    })
  }

  showAll(e) {
    if (e.target === this.element) {
      // this.element.classList.add('showAll')
    }
  }
}
