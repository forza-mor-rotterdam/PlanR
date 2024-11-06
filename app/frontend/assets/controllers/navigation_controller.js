import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = []

  initialize() {}

  connect() {
    if (sessionStorage.getItem('navSmall')) {
      document.body.classList.add(sessionStorage.getItem('navSmall'))
    }
  }

  toggleMenu(e) {
    document.body.classList.toggle('nav--small')
    let navSize = document.body.classList.contains('nav--small') ? 'nav--small' : ''
    sessionStorage.setItem('navSmall', navSize)
    e.target.closest('button').blur()
  }
}
