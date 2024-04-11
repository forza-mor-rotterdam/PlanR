import { Controller } from '@hotwired/stimulus'
import $ from 'jquery' // Import jQuery
// eslint-disable-next-line no-unused-vars
import Select2 from 'select2'

let form = null
// eslint-disable-next-line no-unused-vars
let inputList = null
// eslint-disable-next-line no-unused-vars
let formData = null
const defaultErrorMessage = 'Vul a.u.b. dit veld in.'

export default class extends Controller {
  static targets = ['formTaakStarten', 'categorieField', 'taaktypeField']

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
    this.handleTaaktypeChoices()
  }

  handleTaaktypeChoices() {
    this.categorieFieldTarget.addEventListener('change', () => {
      const categorie = this.categorieFieldTarget.value
      const taaktypeField = this.taaktypeFieldTarget

      // Clear previous options
      taaktypeField.innerHTML = ''

      // Add default option
      const defaultOption = document.createElement('option')
      defaultOption.textContent = 'Selecteer een taak'
      defaultOption.value = ''
      taaktypeField.appendChild(defaultOption)

      // Add options based on selected categorie
      const taaktypes = JSON.parse(form.dataset.taakstartenformulierTaaktypes)

      taaktypes.forEach((categorieOptions) => {
        const [category, options] = categorieOptions
        const isMatchedCategory = !categorie || category === categorie

        if (Array.isArray(options) && isMatchedCategory) {
          const optgroup = document.createElement('optgroup')
          optgroup.label = category

          options.forEach((taaktype) => {
            const [value, text] = taaktype
            const option = document.createElement('option')
            option.value = value
            option.textContent = text
            optgroup.appendChild(option)
          })

          taaktypeField.appendChild(optgroup)
        }
      })
    })
  }

  checkValids() {
    // Check all input fields (except checkboxes) for validity
    // If one or more fields are invalid, don't send the form (return false)
    const inputList = document.querySelectorAll('select')
    let count = 0
    for (const input of inputList) {
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
    return count === 0
  }
}
