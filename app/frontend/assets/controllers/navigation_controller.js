import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = []

  initialize() {}

  connect() {
    console.log(sessionStorage.getItem('navSmall'))
    this.element.classList.add(sessionStorage.getItem('navSmall'))
  }

  toggleMenu(e) {
    this.element.classList.toggle('nav--small')
    console.log(sessionStorage.getItem('navSmall') === 'true')
    let navSize = this.element.classList.contains('nav--small')
      ? 'nav--small'
      : 'sessionStorage.setItem'
    sessionStorage.setItem('navSmall', navSize)
    e.target.closest('button').blur()
  }
}
