import { Controller } from '@hotwired/stimulus'

let externalTextMaxCharacter = null
const externalTextMaxCharacterPrefix = 'Aantal karakters: '

export default class extends Controller {
  static values = {
    formIsSubmitted: Boolean,
    parentContext: String,
    standaardafhandelteksten: String,
    standaardExterneOmschrijvingLijst: String,
    meldingAfhandelredenLijst: String,
  }
  static targets = [
    'externalText',
    'internalText',
    'standardTextChoice',
    'meldingBehandelFormulier',
    'nietOpgelostRedenField',
    'specificatieField',
    'resolutieField',
    'contentContainer',
    'resolutieContainer',
    'redenContainer',
    'specificatieContainer',
    'standaardtekstContainer',
    'standaardtekstOptionsContainer',
    'noStandaardtekstOptionsAlert',
    'alertContainer',
    'submitButton',
  ]

  connect() {
    if (!this.hasNietOpgelostRedenFieldTarget || !this.hasStandardTextChoiceTarget) {
      return
    }
    this.standaardExterneOmschrijvingLijst = JSON.parse(this.standaardExterneOmschrijvingLijstValue)
    this.meldingAfhandelredenLijst = JSON.parse(this.meldingAfhandelredenLijstValue)
    if (this.hasExternalTextTarget) {
      externalTextMaxCharacter = document.createElement('small')
      this.externalTextTarget.parentNode.insertBefore(
        externalTextMaxCharacter,
        this.externalTextTarget.nextSibling
      )
      externalTextMaxCharacter.classList.add('help-block', 'no-margin')
      externalTextMaxCharacter.innerHTML = `${externalTextMaxCharacterPrefix}${this.externalTextTarget.value.length}/${this.externalTextTarget.maxLength}`

      if (this.externalTextTarget.textContent.length > 0) {
        this.externalMessage = this.externalTextTarget.textContent
      }
    }

    this.aangepasteTekstOption = this.standardTextChoiceTarget.querySelector(
      'option[value="aangepasteTekst"]'
    )
    this.heeftAangepastTekst = false
    this.aangepastTekst = ''
    this.onResolutieChangeHandler()
    this.specificatieUrls = []
    this.update()

    // bepaal de maximale hoogte van de formuliercontent
    const footerElement = this.element.querySelector('.modal-footer--sticky')
    const maxHeightDialog = window.innerHeight - 60
    const heightFooter = parseFloat(getComputedStyle(footerElement).height)
    const heightTop = this.element.offsetTop
    const maxHeight = maxHeightDialog - heightTop - heightFooter - 20
    this.contentContainerTarget.style.maxHeight = `${maxHeight}px`
  }
  onResolutieChangeHandler() {
    this.heeftAangepastTekst = false
    this.aangepastTekst = ''
    this.resolutie = this.element.querySelector(
      `input[name='${this.resolutieFieldTarget.name}']:checked`
    )?.value
    this.standaardExterneOmschrijvingen = this.standaardExterneOmschrijvingLijst.filter(
      (omschrijving) => ['altijd', this.resolutie].includes(omschrijving.zichtbaarheid)
    )
    this.update()
  }
  onChangeRedenHandler() {
    this.heeftAangepastTekst = false
    this.aangepastTekst = ''
    Array.from(
      this.element.querySelectorAll(`input[name='${this.specificatieFieldTarget.name}']`)
    ).map((elem) => {
      elem.checked = false
    })
    this.update()
  }
  onChangeExternalText(e) {
    this.aangepastTekst = e.target.value
    this.heeftAangepastTekst = true
    this.update()
  }

  onChangeStandardTextChoice(e) {
    if (e.target.value === 'aangepasteTekst') {
      this.externalTextTarget.value = this.aangepastTekst
      this.updateCharacterCount(this.aangepastTekst.length)
      return
    } else if (this.aangepastTekst === '') {
      this.heeftAangepastTekst = false
    }
    const standaardExterneOmschrijving = this.standaardExterneOmschrijvingen.find(
      (omschrijving) => omschrijving.id === parseInt(e.target.value)
    )
    this.externalTextTarget.value = standaardExterneOmschrijving.tekst
    this.updateCharacterCount(standaardExterneOmschrijving.tekst.length)
  }

  updateCharacterCount(count) {
    if (externalTextMaxCharacter) {
      externalTextMaxCharacter.innerHTML = `${externalTextMaxCharacterPrefix}${count}/${this.externalTextTarget.maxLength}`
    }
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
  filterSpecificaties(nietOpgelostRedenValue) {
    const reden = this.meldingAfhandelredenLijst.find(
      (reden) => reden.id === parseInt(nietOpgelostRedenValue)
    )
    const standaardExterneOmschrijvingLijstAltijdzichtbaar =
      this.standaardExterneOmschrijvingen.filter(
        (omschrijving) => omschrijving.zichtbaarheid === 'altijd'
      )
    console.log(standaardExterneOmschrijvingLijstAltijdzichtbaar)
    const standaardExterneOmschrijvingLijstReden = this.standaardExterneOmschrijvingen.filter(
      (omschrijving) => omschrijving.reden === parseInt(nietOpgelostRedenValue)
    )
    this.specificatieUrls = reden?.specificatie_opties ?? []
    Array.from(
      this.element.querySelectorAll(`input[name='${this.specificatieFieldTarget.name}']`)
    ).map((elem) => {
      const standaardExterneOmschrijvingLijstRedenSpecificatieUrls =
        standaardExterneOmschrijvingLijstReden.filter((omschrijving) =>
          omschrijving.specificatie_opties.includes(elem.value)
        )
      console.log(standaardExterneOmschrijvingLijstRedenSpecificatieUrls)
      const show = this.specificatieUrls.includes(elem.value) // && (standaardExterneOmschrijvingLijstAltijdzichtbaar.length || standaardExterneOmschrijvingLijstRedenSpecificatieUrls.length)
      elem.disabled = !show
      elem.closest('li').style.display = show ? 'block' : 'none'
    })
    if (this.specificatieUrls.length === 1) {
      const specificatieField = this.specificatieFieldTargets.find(
        (input) => input.value === this.specificatieUrls[0]
      )
      if (specificatieField) {
        specificatieField.checked = true
      }
    }
  }
  filterStandaardExterneOmschrijvingLijst(specificatieUrl, nietOpgelostReden) {
    const nietOpgelost = this.resolutie === 'niet_opgelost'
    this.updateCharacterCount(0)
    const reden = this.meldingAfhandelredenLijst.find(
      (reden) => reden.id === parseInt(nietOpgelostReden)
    )
    this.specificatieUrls = reden?.specificatie_opties ?? []
    const standaardExterneOmschrijvingLijst = this.standaardExterneOmschrijvingen.filter(
      (omschrijving) => {
        if (!nietOpgelostReden && nietOpgelost) {
          return false
        }
        if (nietOpgelostReden && !specificatieUrl && this.specificatieUrls.length) {
          return false
        }
        if (omschrijving.zichtbaarheid === 'altijd') {
          return true
        }
        if (specificatieUrl) {
          return omschrijving.specificatie_opties.includes(specificatieUrl)
        }
        if (nietOpgelostReden && !this.specificatieUrls.length) {
          return omschrijving.reden === parseInt(nietOpgelostReden)
        }
        return !nietOpgelost
      }
    )
    const standaardExterneOmschrijvingIdLijst = standaardExterneOmschrijvingLijst.map(
      (omschrijving) => omschrijving.id
    )

    Array.from(this.standardTextChoiceTarget.querySelectorAll('option')).map((elem) => {
      const show = standaardExterneOmschrijvingIdLijst.includes(parseInt(elem.value))
      if (elem.value) {
        elem.style.display = show ? 'block' : 'none'
        elem.disabled = !show
      } else {
        elem.style.display = 'block'
        elem.disabled = true
      }
    })

    this.standardTextChoiceTarget.value = ''
    this.aangepasteTekstOption.disabled = false
    this.standardTextChoiceTarget.disabled = false
    let externalText = ''
    if (standaardExterneOmschrijvingIdLijst.length) {
      if (standaardExterneOmschrijvingIdLijst.length === 1) {
        this.standardTextChoiceTarget.disabled = true
        this.standardTextChoiceTarget.value = standaardExterneOmschrijvingIdLijst[0]
        externalText = standaardExterneOmschrijvingLijst[0].tekst
      }
      this.standaardtekstOptionsContainerTarget.style.display = 'block'
      this.noStandaardtekstOptionsAlertTarget.style.display = 'none'
    } else {
      this.standaardtekstOptionsContainerTarget.style.display = 'none'
      this.noStandaardtekstOptionsAlertTarget.style.display = 'block'
    }
    if (this.heeftAangepastTekst) {
      this.aangepasteTekstOption.style.display = 'block'
      this.standardTextChoiceTarget.value = 'aangepasteTekst'
      this.standardTextChoiceTarget.disabled = false
      externalText = this.aangepastTekst
    }
    this.externalTextTarget.value = externalText
    this.updateCharacterCount(externalText.length)
  }
  onChangeHandler() {
    this.heeftAangepastTekst = false
    this.aangepastTekst = ''
    this.update()
  }
  update() {
    const nietOpgelost = this.resolutie === 'niet_opgelost'
    this.standardTextChoiceTarget.value = null
    Array.from(this.standardTextChoiceTarget.querySelectorAll('option')).map((elem) => {
      elem.style.display = 'none'
      elem.checked = false
      elem.disabled = true
    })
    Array.from(
      this.element.querySelectorAll(`input[name='${this.nietOpgelostRedenFieldTarget.name}']`)
    ).map((elem) => {
      const li = elem.closest('li')
      li.style.display = nietOpgelost ? 'block' : 'none'
      elem.checked = !nietOpgelost ? false : elem.checked
    })

    const nietOpgelostReden = this.element.querySelector(
      `input[name='${this.nietOpgelostRedenFieldTarget.name}']:checked`
    )?.value
    this.filterSpecificaties(nietOpgelostReden)
    const specificatieUrl = this.element.querySelector(
      `input[name='${this.specificatieFieldTarget.name}']:checked`
    )?.value
    this.filterStandaardExterneOmschrijvingLijst(specificatieUrl, nietOpgelostReden)

    this.redenContainerTarget.classList[nietOpgelost ? 'remove' : 'add']('hide')
    this.specificatieContainerTarget.classList[
      nietOpgelost && this.specificatieUrls.length ? 'remove' : 'add'
    ]('hide')
    this.standaardtekstContainerTarget.classList[
      (nietOpgelost && specificatieUrl && this.specificatieUrls.length) ||
      (nietOpgelost && nietOpgelostReden && !this.specificatieUrls.length) ||
      !nietOpgelost
        ? 'remove'
        : 'add'
    ]('hide')

    this.contentContainerTarget.scrollTop = this.contentContainerTarget.scrollHeight

    const showSubmitButton = this.externalTextTarget.value
    this.submitButtonTarget.disabled = !showSubmitButton
  }
}
