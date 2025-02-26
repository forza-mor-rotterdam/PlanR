import { Controller } from '@hotwired/stimulus'
import $ from 'jquery' // Import jQuery
// eslint-disable-next-line no-unused-vars
import Select2 from 'select2'

export default class extends Controller {
  static targets = ['targetField']

  connect() {
    $(this.targetFieldTarget).select2({
      dropdownParent: $('#dialogGeneral'),
    })
  }
}
