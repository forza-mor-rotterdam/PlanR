import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['notificatie', 'releaseNote', 'hideable']

  connect() {
    this.hideableTargets.map((elem) => this.hide(elem))

    this[
      this.snakeToCamel(
        `${this.element.querySelector("[name='bericht_type']:checked").value}_targets`
      )
    ].map((elem) => this.show(elem))
  }
  hide(elem) {
    elem.style.display = 'none'
  }
  show(elem) {
    elem.style.display = 'block'
  }
  snakeToCamel = (str) =>
    str
      .toLowerCase()
      .replace(/([-_][a-z])/g, (group) => group.toUpperCase().replace('-', '').replace('_', ''))
  berichtTypeChangeHandler() {
    this.hideableTargets.map((elem) => this.hide(elem))
    this[
      this.snakeToCamel(
        `${this.element.querySelector("[name='bericht_type']:checked").value}_targets`
      )
    ].map((elem) => this.show(elem))
  }
}
