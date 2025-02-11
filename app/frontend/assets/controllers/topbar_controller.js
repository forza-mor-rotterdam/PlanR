import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  static targets = ['containerUitklapper']

  connect() {
    window.addEventListener('click', (e) => {
      if (
        !(e.target.closest('.container__uitklapper') || e.target.hasAttribute('data-action')) || // data-action conflicts with window.evenlistener
        e.target.classList.contains('btn-close--small')
      ) {
        this.element.querySelectorAll('.show').forEach((element) => {
          element.classList.remove('show')
        })
      }
      document.body.classList.toggle(
        'show--notificatie-lijst',
        this.element.querySelector('.show .container__profiel_notificatie_lijst')
      )
    })

    this.element.addEventListener('keydown', function (e) {
      if (e.code == 'Enter') {
        document.activeElement.click()
      }
    })
  }

  containerUitklapperTargetConnected(element) {
    element.addEventListener('keydown', function (e) {
      if (e.code == 'Space') {
        e.preventDefault()
        document.activeElement.click()
      }
    })
  }

  show(e) {
    if (
      e.target.tagName.toUpperCase() != 'A' &&
      e.target.tagName.toUpperCase() != 'BUTTON' &&
      !e.target.closest('.content--uitklapper')
    ) {
      if (this.element.querySelectorAll('.show').length) {
        this.element.querySelectorAll('.show').forEach((element) => {
          if (element != e.target.closest('.container__uitklapper')) {
            element.classList.remove('show')
          }
          e.target.closest('.container__uitklapper').classList.toggle('show')
        })
      } else {
        e.target.closest('.container__uitklapper').classList.add('show')
      }
    }

    document.body.classList.toggle(
      'show--notificatie-lijst',
      this.element.querySelector('.show .container__profiel_notificatie_lijst')
    )
  }
}
