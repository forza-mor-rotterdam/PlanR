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
    meldingAfhandelredenLijst: String,
  }
  static targets = [
    'externeOmschrijvingTekst',
    'externeOmschrijvingTitel',
    'zichtbaarheidField',
    'nietOpgelostContainer',
    'nietOpgelostRedenField',
    'nietOpgelostSpecificatiesContainer',
    'nietOpgelostSpecificatieOptiesField',
    'submitButton',
  ]

  connect() {
    console.log(this.meldingAfhandelredenLijstValue)
    this.meldingAfhandelredenLijst = JSON.parse(this.meldingAfhandelredenLijstValue)
    if (this.hasExterneOmschrijvingTekstTarget) {
      externeOmschrijvingTekstMaxCharacter = document.createElement('small')
      this.externeOmschrijvingTekstTarget.parentNode.insertBefore(
        externeOmschrijvingTekstMaxCharacter,
        this.externeOmschrijvingTekstTarget.nextSibling
      )
      externeOmschrijvingTekstMaxCharacter.classList.add('help-block', 'no-margin')
      externeOmschrijvingTekstMaxCharacter.innerHTML = `${externeOmschrijvingTekstMaxCharacterPrefix}${this.externeOmschrijvingTekstTarget.value.length}/${this.externeOmschrijvingTekstTarget.maxLength}`

      if (this.externeOmschrijvingTekstTarget.textContent.length > 0) {
        this.externalMessage = this.externeOmschrijvingTekstTarget.textContent
      }
    }

    form = this.element
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
    this.specificatieUrls = []
    this.update()
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
  onChangeHandler() {
    this.update()
  }
  filterSpecificaties(nietOpgelostRedenValue) {
    const reden = this.meldingAfhandelredenLijst.find(
      (reden) => reden.id === parseInt(nietOpgelostRedenValue)
    )
    this.specificatieUrls = reden?.specificatie_opties ?? []
    Array.from(
      this.element.querySelectorAll(
        `input[name='${this.nietOpgelostSpecificatieOptiesFieldTarget.name}']`
      )
    ).map((elem) => {
      const show = this.specificatieUrls.includes(elem.value)
      if (!show) {
        elem.checked = false
      }
      elem.disabled = !show
      elem.closest('li').style.display = show ? 'block' : 'none'
      // elem.closest('li').style.opacity = show ? '1' : '.5'
    })
  }
  update() {
    const NIET_OPGELOST = 'niet_opgelost'
    const titel = this.externeOmschrijvingTitelTarget?.value
    const tekst = this.externeOmschrijvingTekstTarget?.value
    const zichtbaarheid = this.element.querySelector(
      `input[name='${this.zichtbaarheidFieldTarget.name}']:checked`
    )?.value
    const nietOpgelost =
      this.element.querySelector(`input[name='${this.zichtbaarheidFieldTarget.name}']:checked`)
        ?.value === NIET_OPGELOST

    this.updateCharacterCount(tekst.length)
    if (!nietOpgelost) {
      Array.from(
        this.element.querySelectorAll(`input[name='${this.nietOpgelostRedenFieldTarget.name}']`)
      ).map((elem) => {
        elem.checked = false
      })
    }
    const nietOpgelostRedenValue = this.element.querySelector(
      `input[name='${this.nietOpgelostRedenFieldTarget.name}']:checked`
    )?.value
    this.filterSpecificaties(nietOpgelostRedenValue)
    const specificatieValue = this.element.querySelector(
      `input[name='${this.nietOpgelostSpecificatieOptiesFieldTarget.name}']:checked`
    )?.value

    this.nietOpgelostContainerTargets.map((elem) => {
      elem.classList[nietOpgelost ? 'remove' : 'add']('hide')
    })
    this.nietOpgelostSpecificatiesContainerTargets.map((elem) => {
      elem.classList[this.specificatieUrls.length ? 'remove' : 'add']('hide')
    })

    let showSubmitButton = zichtbaarheid && zichtbaarheid != NIET_OPGELOST && titel && tekst

    console.log(!!this.specificatieUrls.length)
    console.log(specificatieValue)
    console.log(!!specificatieValue)
    console.log('')

    showSubmitButton =
      showSubmitButton ||
      (titel &&
        tekst &&
        zichtbaarheid === NIET_OPGELOST &&
        !!nietOpgelostRedenValue &&
        ((!!specificatieValue && !!this.specificatieUrls.length) ||
          (!this.specificatieUrls.length && !specificatieValue)))

    this.submitButtonTarget.disabled = !showSubmitButton
  }
}
