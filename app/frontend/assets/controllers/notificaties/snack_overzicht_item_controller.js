import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  connect() {
    this.element.controller = this
    this.manager = null
    console.log(`${this.identifier} connected`)
  }
  initializeManager(manager) {
    this.manager = manager
  }
  markeerAlsGelezen() {
    this.element.classList.add('is-watched')
  }
}
