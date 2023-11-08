import { Controller } from '@hotwired/stimulus'

let form = null
let inputList = null
const defaultErrorMessage = 'Vul a.u.b. dit veld in.'
let externalTextMaxCharacter = null
const externalTextMaxCharacterPrefix = 'Aantal karakters: '

export default class extends Controller {
  static values = {
    formIsSubmitted: Boolean,
    parentContext: String,
    standaardafhandelteksten: String,
  }
  static targets = ['externalText', 'internalText', 'standardTextChoice']

  connect() {
    if (this.hasExternalTextTarget) {
      externalTextMaxCharacter = document.createElement('small')
      this.externalTextTarget.parentNode.insertBefore(
        externalTextMaxCharacter,
        this.externalTextTarget.nextSibling
      )
      externalTextMaxCharacter.classList.add('help-block', 'no-margins')
      externalTextMaxCharacter.innerHTML = `${externalTextMaxCharacterPrefix}${this.externalTextTarget.value.length}/${this.externalTextTarget.maxLength}`

      if (this.externalTextTarget.textContent.length > 0) {
        this.externalMessage = this.externalTextTarget.textContent
      }
    }

    form = document.querySelector('#afhandelForm')
    inputList = document.querySelectorAll('.js-validation textarea')

    for (const element of inputList) {
      const input = element
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

  onChangeExternalText(e) {
    this.updateCharacterCount(e.target.value.length)
  }

  onChangeStandardTextChoice() {
    this.updateExternalTextValue()
  }

  updateExternalTextValue() {
    if (this.hasExternalTextTarget && this.hasStandardTextChoiceTarget) {
      const selectedOption =
        this.standardTextChoiceTarget.options[this.standardTextChoiceTarget.selectedIndex]
      if (selectedOption) {
        this.externalTextTarget.value = selectedOption.value
        this.updateCharacterCount(selectedOption.value.length)
      }
    }
  }

  updateCharacterCount(count) {
    if (externalTextMaxCharacter) {
      externalTextMaxCharacter.innerHTML = `${externalTextMaxCharacterPrefix}${count}/${this.externalTextTarget.maxLength}`
    }
  }

  checkValids() {
    //check all inputfields (except checkboxes) for validity
    // if 1 or more fields is invalid, don't send the form (return false)
    inputList = document.querySelectorAll('textarea')
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

  cancelHandle() {
    this.element.dispatchEvent(
      new CustomEvent('cancelHandle', {
        detail: JSON.parse(this.parentContextValue),
        bubbles: true,
      })
    )
  }

  setExternalMessage(evt) {
    if (this.hasExternalTextTarget) {
      this.choice = evt.params.index
      this.externalMessage = JSON.parse(this.standaardafhandeltekstenValue)[evt.target.value]
      this.externalTextTarget.value = this.externalMessage
    }
  }

  defaultExternalMessage() {
    if (this.externalMessage.length === 0) return

    this.externalTextTarget.value = this.externalMessage
  }

  clearExternalMessage() {
    this.externalTextTarget.value = ''
  }
}
