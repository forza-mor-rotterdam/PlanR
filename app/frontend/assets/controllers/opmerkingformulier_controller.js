import { Controller } from '@hotwired/stimulus'

let form = null
// eslint-disable-next-line no-unused-vars
let formData = null
const defaultErrorMessage = 'Voeg a.u.b. een opmerking of een afbeelding toe.'

export default class extends Controller {
  static targets = ['formOpmerking', 'errorMessage']

  connect() {
    form = this.formOpmerkingTarget
    formData = new FormData(form)
  }

  checkValids() {
    const inputList = form.querySelectorAll('input[type="file"], textarea')
    let count = 0
    for (const input of inputList) {
      if (input.value.length < 1) {
        count++
      }
    }
    return count <= 1
  }

  onSubmit(event) {
    event.preventDefault()
    const allFieldsValid = this.checkValids()
    if (!allFieldsValid) {
      this.errorMessageTarget.textContent = defaultErrorMessage
    } else {
      this.errorMessageTarget.textContent = ''
      this.formOpmerkingTarget.requestSubmit()
    }
  }
}
