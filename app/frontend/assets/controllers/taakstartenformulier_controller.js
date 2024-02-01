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
  static targets = ['formTaakStarten']

  initializeSelect2() {
    $(this.formTaakStartenTarget.querySelector('.select2')).select2({
      dropdownParent: $('#meldingDetailModal'),
      matcher: (params, data) => {
        const originalMatcher = $.fn.select2.defaults.defaults.matcher
        const result = originalMatcher(params, data)

        if (result && data.children && result.children && data.children.length) {
          if (
            data.children.length !== result.children.length &&
            data.text.toLowerCase().includes(params.term.toLowerCase())
          ) {
            return {
              ...result,
              children: data.children,
            }
          }
        }

        return result
      },
    })

    $(this.formTaakStartenTarget.querySelector('.select2')).on('select2:select', function (e) {
      const select = e.target
      const error = select.closest('.form-row').getElementsByClassName('invalid-text')[0]
      if (select.validity.valid) {
        select.closest('.form-row').classList.remove('is-invalid')
        error.textContent = ''
      } else {
        error.textContent = defaultErrorMessage
        select.closest('.form-row').classList.add('is-invalid')
      }
    })
  }

  connect() {
    form = this.formTaakStartenTarget
    inputList = this.element.querySelectorAll('select')

    formData = new FormData(form)
    this.initializeSelect2()

    form.addEventListener('submit', (event) => {
      const allFieldsValid = this.checkValids()

      if (!allFieldsValid) {
        const errorList = this.element.querySelectorAll('div.is-invalid')
        errorList[0].scrollIntoView({ behavior: 'smooth' })
        event.preventDefault()
      }
    })
  }

  checkValids() {
    //check all inputfields (except checkboxes) for validity
    // if 1 or more fields is invalid, don't send the form (return false)
    inputList = this.element.querySelectorAll('select')
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
