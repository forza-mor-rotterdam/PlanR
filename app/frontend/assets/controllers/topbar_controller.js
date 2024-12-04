import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
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
    })
  }

  show(e) {
    if (e.target.tagName != 'A') {
      this.element.querySelectorAll('.show').forEach((element) => {
        element.classList.remove('show')
      })
      e.target.closest('.container__uitklapper').classList.add('show')
    }
  }
}
