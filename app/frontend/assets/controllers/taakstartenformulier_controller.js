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
    this.handleTaaktypeChoicesRadio()
  }
  hideRadioButton = (radioButton) => {
    radioButton.style.display = 'none'
    const label = radioButton.closest('label')
    if (label) {
      label.style.display = 'none'
    }
  }

  showRadioButton = (radioButton) => {
    radioButton.style.display = 'block'
    const label = radioButton.closest('label')
    if (label) {
      label.style.display = 'inline-block'
    }
  }

  toggleRadioButtons = (taaktypeField, taaktypeRadioButtons, taaktypes, categorie) => {
    let hasMatchingOptions = false
    taaktypeRadioButtons.forEach((radioButton) => {
      const value = radioButton.value
      const [matchingOption] =
        // eslint-disable-next-line no-unused-vars
        taaktypes.find(([_, options]) => {
          return options.some(([optionValue]) => optionValue === value)
        }) || []
      if (matchingOption && matchingOption === categorie) {
        this.showRadioButton(radioButton)
        hasMatchingOptions = true
      } else {
        this.hideRadioButton(radioButton)
      }
    })
    // Show the form field if there are matching options, otherwise hide it
    taaktypeField.style.display = hasMatchingOptions ? 'block' : 'none'
  }

  handleTaaktypeChoicesRadio = () => {
    const taaktypeField = this.taaktypeFieldTarget
    const taaktypeRadioButtons = this.element.querySelectorAll(
      'input[type="radio"][data-taakstartenformulier-target="taaktypeField"]'
    )

    // Hide the entire form field initially
    taaktypeField.style.display = 'none'
    taaktypeRadioButtons.forEach(this.hideRadioButton)
    const taaktypes = JSON.parse(this.formTaakStartenTarget.dataset.taakstartenformulierTaaktypes)

    this.categorieFieldTarget.addEventListener('change', () => {
      const categorie = this.categorieFieldTarget.value
      if (!categorie) {
        // Hide the form field and its options when no category is selected
        taaktypeField.style.display = 'none'
        taaktypeRadioButtons.forEach(this.hideRadioButton)
        return
      }
      // Toggle radio buttons based on selected category
      this.toggleRadioButtons(taaktypeField, taaktypeRadioButtons, taaktypes, categorie)
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
