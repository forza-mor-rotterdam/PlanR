import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['notificatie']

  connect() {
    this.setList(this.element.classList.value.includes('toast'))
    this.element.addEventListener('notificatieVerwijderd', () => {
      // wacht tot notificatie echt is verwijderd
      setTimeout(() => {
        this.resetList()
      }, 100)
    })
  }

  setList(isToast) {
    const list = this.notificatieTargets
    // eslint-disable-next-line for-direction
    for (let i = list.length - 1; i >= 0; i--) {
      setTimeout(
        () => {
          list[i].classList.add('init')
        },
        600 * (-i + list.length)
      )
    }

    if (!isToast) {
      // Alleen als het geen toast is achter elkaar tonen
      for (let i = 0; i < list.length; i++) {
        setTimeout(
          () => {
            list[i].classList.replace('init', 'show')
            list[i].style.transform = `translateY(-${
              list[i].offsetTop - i * 8 + (list[i].offsetHeight - list[0].offsetHeight)
            }px) scale(${1 - i * 0.02}, 1)`
          },
          5000 + 100 * i
        )
      }
    }
  }

  resetList() {
    const list = this.notificatieTargets
    for (let i = 0; i < list.length; i++) {
      list[i].style.transform = `translateY(-${
        list[i].offsetTop - i * 8 + (list[i].offsetHeight - list[0].offsetHeight)
      }px) scale(${1 - i * 0.02}, 1)`
    }
  }
}
