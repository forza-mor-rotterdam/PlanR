import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  connect() {
    const list = this.element.querySelectorAll('li')
    // eslint-disable-next-line for-direction
    for (let i = list.length - 1; i >= 0; i--) {
      setTimeout(
        () => {
          list[i].classList.add('init')
        },
        2000 * (-i + list.length)
      )
      setTimeout(
        () => {
          list[i].classList.replace('init', 'show')
        },
        2000 * (-i + list.length + 1)
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
