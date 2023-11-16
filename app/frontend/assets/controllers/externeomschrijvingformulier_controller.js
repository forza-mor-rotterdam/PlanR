import { Controller } from '@hotwired/stimulus'

let form = null
let inputList = null
const defaultErrorMessage = 'Vul a.u.b. dit veld in.'
let externeOmschrijvingTextMaxCharacter = null
const externeOmschrijvingTextMaxCharacterPrefix = 'Aantal karakters: '

export default class extends Controller {
  static values = {
    formIsSubmitted: Boolean,
    parentContext: String,
  }
  static targets = ['externeOmschrijvingText']

  connect() {
    if (this.hasExterneOmschrijvingTextTarget) {
      externeOmschrijvingTextMaxCharacter = document.createElement('small')
      this.externeOmschrijvingTextTarget.parentNode.insertBefore(
        externeOmschrijvingTextMaxCharacter,
        this.externeOmschrijvingTextTarget.nextSibling
      )
      externeOmschrijvingTextMaxCharacter.classList.add('help-block', 'no-margins')
      externeOmschrijvingTextMaxCharacter.innerHTML = `${externeOmschrijvingTextMaxCharacterPrefix}${this.externeOmschrijvingTextTarget.value.length}/${this.externeOmschrijvingTextTarget.maxLength}`

      if (this.externeOmschrijvingTextTarget.textContent.length > 0) {
        this.externalMessage = this.externeOmschrijvingTextTarget.textContent
      }
    }

    form = document.querySelector('#externeOmschrijvingForm')
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

  onChangeExterneOmschrijvingText(e) {
    this.updateCharacterCount(e.target.value.length)
  }

  updateCharacterCount(count) {
    if (externeOmschrijvingTextMaxCharacter) {
      externeOmschrijvingTextMaxCharacter.innerHTML = `${externeOmschrijvingTextMaxCharacterPrefix}${count}/${this.externeOmschrijvingTextTarget.maxLength}`
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
    if (this.hasExterneOmschrijvingTextTarget) {
      this.choice = evt.params.index
      this.externalMessage = JSON.parse(this.standaardafhandeltekstenValue)[evt.target.value]
      this.externeOmschrijvingTextTarget.value = this.externalMessage
    }
  }

  defaultExternalMessage() {
    if (this.externalMessage.length === 0) return

    this.externeOmschrijvingTextTarget.value = this.externalMessage
  }

  clearExternalMessage() {
    this.externeOmschrijvingTextTarget.value = ''
  }
}
