import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['notificatie']

  connect() {
    const list = this.notificatieTargets
    console.log('list', list)
    // eslint-disable-next-line for-direction
    for (let i = 0; i < list.length; i++) {
      setTimeout(() => {
        list[i].classList.add('init')
      }, 2000 * i)
      setTimeout(
        () => {
          list[i].classList.replace('init', 'show')
        },
        2000 * (i + 1)
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
