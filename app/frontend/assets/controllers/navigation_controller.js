import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = []

  initialize() {}

  connect() {}

  toggleMenu(e) {
    console.log(e)
    this.element.classList.toggle('nav--small')
    e.target.closest('button').blur()
  }
}
