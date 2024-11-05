import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['notificatie', 'releaseNote', 'hideable']

  connect() {
    console.log(this.identifier)
    console.log(this.element.querySelector("[name='bericht_type']"))
    console.log(this.element.querySelector("[name='bericht_type']").value)
    console.log(
      this.snakeToCamel(
        `${this.element.querySelector("[name='bericht_type']:checked").value}_targets`
      )
    )
    console.log(
      this[
        this.snakeToCamel(
          `${this.element.querySelector("[name='bericht_type']:checked").value}_targets`
        )
      ]
    )
    console.log(this.hideableTargets)

    // this.hideableTargets.map((elem) => elem.style.display = "none")
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
  berichtTypeChangeHandler(e) {
    console.log(e)
    this.hideableTargets.map((elem) => this.hide(elem))
    this[
      this.snakeToCamel(
        `${this.element.querySelector("[name='bericht_type']:checked").value}_targets`
      )
    ].map((elem) => this.show(elem))
  }
}
