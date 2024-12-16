import { Controller } from '@hotwired/stimulus'
import { renderStreamMessage } from '@hotwired/turbo'

export default class extends Controller {
  static targets = ['herlaad']
  static values = {
    toastUrl: String,
  }
  initialize() {}
  connect() {}
  herlaadTargetConnected() {
    this.laadToasts()
  }
  laadToasts() {
    fetch(this.toastUrlValue)
      .then((response) => response.text())
      .then((text) => renderStreamMessage(text))
  }
}
