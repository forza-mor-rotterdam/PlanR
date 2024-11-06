import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['notificatie']

  connect() {
    this.setList()
  }

  setList() {
    const list = this.notificatieTargets
    console.log('list', list)
    // eslint-disable-next-line for-direction
    for (let i = list.length - 1; i >= 0; i--) {
      setTimeout(
        () => {
          list[i].classList.add('init')
        },
        600 * (-i + list.length)
      )
    }

    for (let i = 0; i < list.length; i++) {
      setTimeout(
        () => {
          list[i].classList.replace('init', 'show')
          console.log(list[i].height)
          list[i].style.transform = `translateY(-${
            list[i].offsetTop - i * 20 + (list[i].offsetHeight - list[0].offsetHeight)
          }px) scale(${1 - i * 0.02})`
        },
        5000 + 100 * i
      )
    }
  }

  resetList() {
    const list = this.notificatieTargets
    for (let i = 0; i < list.length; i++) {
      list[i].style.transform = `translateY(-${
        list[i].offsetTop - i * 20 + (list[i].offsetHeight - list[0].offsetHeight)
      }px) scale(${1 - i * 0.02})`
    }
    console.log('resetList', list)
  }

  hideNotification(e) {
    const notification = e.target.closest('.notification')
    notification.classList.add('hide')

    notification.addEventListener('transitionend', () => {
      notification.remove()
      this.resetList()
    })
  }

  showAll(e) {
    if (e.target === this.element) {
      // this.element.classList.add('showAll')
    }
  }
}
