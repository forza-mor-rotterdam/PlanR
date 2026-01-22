import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  static targets = ['selectedLabel', 'list']
  connect() {
    console.log(this.identifier)
  }
  onChangeHandler(e) {
    this.selectedLabelTarget.textContent = e.target.closest('li').querySelector('label').textContent
  }
}
