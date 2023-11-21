import { Controller } from '@hotwired/stimulus'

let form = null
let inputList = null
const defaultErrorMessage = 'Vul a.u.b. dit veld in.'
let externeOmschrijvingTekstMaxCharacter = null
const externeOmschrijvingTekstMaxCharacterPrefix = 'Aantal karakters: '

export default class extends Controller {
  static values = {
    formIsSubmitted: Boolean,
    parentContext: String,
  }
  static targets = ['externeOmschrijvingTekst', 'externeOmschrijvingTitel']

  connect() {
    if (this.hasExterneOmschrijvingTekstTarget) {
      externeOmschrijvingTekstMaxCharacter = document.createElement('small')
      this.externeOmschrijvingTekstTarget.parentNode.insertBefore(
        externeOmschrijvingTekstMaxCharacter,
        this.externeOmschrijvingTekstTarget.nextSibling
      )
      externeOmschrijvingTekstMaxCharacter.classList.add('help-block', 'no-margins')
      externeOmschrijvingTekstMaxCharacter.innerHTML = `${externeOmschrijvingTekstMaxCharacterPrefix}${this.externeOmschrijvingTekstTarget.value.length}/${this.externeOmschrijvingTekstTarget.maxLength}`

      if (this.externeOmschrijvingTekstTarget.textContent.length > 0) {
        this.externalMessage = this.externeOmschrijvingTekstTarget.textContent
      }
    }

    form = document.querySelector('#externeOmschrijvingForm')
    inputList = document.querySelectorAll('[type="text"], textarea')

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

  onChangeExterneOmschrijvingTekst(e) {
    this.updateCharacterCount(e.target.value.length)
  }

  updateCharacterCount(count) {
    if (externeOmschrijvingTekstMaxCharacter) {
      externeOmschrijvingTekstMaxCharacter.innerHTML = `${externeOmschrijvingTekstMaxCharacterPrefix}${count}/${this.externeOmschrijvingTekstTarget.maxLength}`
    }
  }

  checkValids() {
    //check all inputfields (except checkboxes) for validity
    // if 1 or more fields is invalid, don't send the form (return false)
    inputList = document.querySelectorAll('[type="text"], textarea')
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
    if (this.hasExterneOmschrijvingTekstTarget) {
      this.choice = evt.params.index
      this.externalMessage = JSON.parse(this.standaardafhandeltekstenValue)[evt.target.value]
      this.externeOmschrijvingTekstTarget.value = this.externalMessage
    }
  }

  defaultExternalMessage() {
    if (this.externalMessage.length === 0) return

    this.externeOmschrijvingTekstTarget.value = this.externalMessage
  }

  clearExternalMessage() {
    this.externeOmschrijvingTekstTarget.value = ''
  }
}
