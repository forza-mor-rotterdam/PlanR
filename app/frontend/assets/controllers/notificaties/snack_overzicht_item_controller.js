import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  connect() {
    this.element.controller = this
    console.log(`${this.identifier} connected`)
  }
}
