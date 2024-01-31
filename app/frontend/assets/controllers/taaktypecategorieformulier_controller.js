import { Controller } from '@hotwired/stimulus'
import $ from 'jquery' // Import jQuery
// eslint-disable-next-line no-unused-vars
import Select2 from 'select2'

let form = null
let inputList = null
// eslint-disable-next-line no-unused-vars
let formData = null
const defaultErrorMessage = 'Vul a.u.b. dit veld in.'

export default class extends Controller {
  static targets = ['formTaaktypeCategorie']

  initializeSelect2() {
    $(this.formTaaktypeCategorieTarget.querySelector('.select2')).select2({})
  }

  connect() {
    form = this.formTaaktypeCategorieTarget
    inputList = document.querySelectorAll('[type="text"], [type="radio"], select, textarea')

    formData = new FormData(form)
    this.initializeSelect2()

    for (let i = 0; i < inputList.length; i++) {
      const input = inputList[i]
      const error = input.closest('.form-row').getElementsByClassName('invalid-text')[0]

      input.addEventListener('input', () => {
        if (input.validity.valid) {
          input.closest('.form-row').classList.remove('is-invalid')
          error.textContent = ''
        } else {
          error.textContent = defaultErrorMessage
          input.closest('.form-row').classList.add('is-invalid')
        }
      })
    }

    form.addEventListener('submit', (event) => {
      const allFieldsValid = this.checkValids()

      if (!allFieldsValid) {
        const errorList = document.querySelectorAll('div.is-invalid')
        errorList[0].scrollIntoView({ behavior: 'smooth' })
        event.preventDefault()
      }
    })
  }

  checkValids() {
    //check all inputfields (except checkboxes) for validity
    // if 1 or more fields is invalid, don't send the form (return false)
    inputList = document.querySelectorAll('select')
    let count = 0
    for (let i = 0; i < inputList.length; i++) {
      const input = inputList[i]
      const error = input.closest('.form-row').getElementsByClassName('invalid-text')[0]
      if (input.validity.valid) {
        error.textContent = ''
        input.closest('.form-row').classList.remove('is-invalid')
      } else {
        error.textContent = defaultErrorMessage
        input.closest('.form-row').classList.add('is-invalid')
        count++
      }
    }
    if (count > 0) {
      return false
    } else {
      return true
    }
  }
}
