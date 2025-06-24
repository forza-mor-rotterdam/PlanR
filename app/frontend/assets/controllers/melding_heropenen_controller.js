import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['internalText', 'submitButton']

  connect() {
    this.submitButtonTarget.disabled = !this.internalTextTarget.value

    this.internalTextTarget.addEventListener('input', () => {
      this.submitButtonTarget.disabled = !this.internalTextTarget.value
    })
  }
}
