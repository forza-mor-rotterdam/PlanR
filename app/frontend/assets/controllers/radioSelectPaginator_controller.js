import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  connect() {
    this.form = this.element.closest('form')
  }
  onPageChangeHandler() {
    this.form.requestSubmit()
  }
}
