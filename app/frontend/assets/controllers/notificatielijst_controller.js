import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['notificatie']

  connect() {
    this.setList(this.element.classList.value.includes('toast'))
    this.element.addEventListener('notificatieVerwijderd', () => {
      // wacht tot notificatie echt is verwijderd
      setTimeout(() => {
        this.resetList(this.element.classList.value.includes('toast'))
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
            if (i === 0) {
              list[i].style.transform = `translateY(0) scale(1, 1)`
            } else {
              list[i].style.transform = `translateY(-${
                list[i].offsetTop - list[0].offsetHeight
              }px) translateY(-100%) translateY(${i * 8}px) scale(${1 - i * 0.02}, 1)`
            }
          },
          5000 + 100 * i
        )
      }
    }
  }

  resetList(isToast) {
    if (!isToast) {
      // Alleen als het geen toast is achter elkaar tonen
      const list = this.notificatieTargets
      console.log('list', list)
      for (let i = 0; i < list.length; i++) {
        if (i === 0) {
          list[i].style.transform = `translateY(0) scale(1, 1)`
        } else {
          list[i].style.transform = `translateY(-${
            list[i].offsetTop - list[0].offsetHeight
          }px) translateY(-100%) translateY(${i * 8}px) scale(${1 - i * 0.02}, 1)`
        }
      }
    }
  }
}
