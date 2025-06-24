import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['statusField', 'submitButton']
  connect() {
    this.valid = this.submitButtonTarget.disabled
    this.submitButtonTarget.disabled = true
  }
  onStatusChangeHandler(e) {
    this.submitButtonTarget.disabled = e.target.value && this.valid
  }
}
