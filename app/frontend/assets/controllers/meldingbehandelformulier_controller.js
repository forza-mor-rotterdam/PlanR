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
    'submitButton',
  ]

  connect() {
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

    this.aangepasteTekstOption = this.standardTextChoiceTarget.querySelector('option')
    console.log('this.aangepasteTekstOption')
    console.log(this.aangepasteTekstOption)
    // this.aangepasteTekstOption.value = 'aangepasteTekst'
    // this.aangepasteTekstOption.textContent = '- Aangepaste tekst -'
    // this.standardTextChoiceTarget.insertBefore(this.aangepasteTekstOption, this.standardTextChoiceTarget.firstChild)

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
    if (this.aangepastTekst === '') {
      this.heeftAangepastTekst = false
    }
    this.resolutie = this.element.querySelector(
      `input[name='${this.resolutieFieldTarget.name}']:checked`
    )?.value
    this.standaardExterneOmschrijvingen = this.standaardExterneOmschrijvingLijst.filter(
      (omschrijving) => ['altijd', this.resolutie].includes(omschrijving.zichtbaarheid)
    )
    console.log(
      this.standaardExterneOmschrijvingen.map((omschrijving) => omschrijving.zichtbaarheid)
    )
    this.update()
  }
  onChangeRedenHandler() {
    if (this.aangepastTekst === '') {
      this.heeftAangepastTekst = false
    }
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
    this.updateCharacterCount(e.target.value.length)
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
    console.log(standaardExterneOmschrijving)
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
    this.specificatieUrls = reden?.specificatie_opties ?? []
    Array.from(
      this.element.querySelectorAll(`input[name='${this.specificatieFieldTarget.name}']`)
    ).map((elem) => {
      const show = this.specificatieUrls.includes(elem.value)
      elem.disabled = !show
      elem.closest('li').style.display = show ? 'block' : 'none'
    })
  }
  filterStandaardExterneOmschrijvingLijst(specificatieUrl, nietOpgelostReden) {
    const nietOpgelost = this.resolutie === 'niet_opgelost'
    this.externalTextTarget.value = ''
    this.updateCharacterCount(0)
    const reden = this.meldingAfhandelredenLijst.find(
      (reden) => reden.id === parseInt(nietOpgelostReden)
    )
    this.specificatieUrls = reden?.specificatie_opties ?? []
    console.log('specificatieUrls')
    console.log(this.specificatieUrls)
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

    console.log('standaardExterneOmschrijvingLijst')
    console.log(standaardExterneOmschrijvingLijst.map((omschrijving) => omschrijving.titel))

    Array.from(this.standardTextChoiceTarget.querySelectorAll('option')).map((elem) => {
      const show = standaardExterneOmschrijvingIdLijst.includes(parseInt(elem.value))
      elem.style.display = show ? 'block' : 'none'
    })
    if (standaardExterneOmschrijvingIdLijst.length) {
      let externalText = standaardExterneOmschrijvingLijst[0].tekst
      if (this.heeftAangepastTekst) {
        this.aangepasteTekstOption.style.display = 'block'
      }
      this.externalTextTarget.value = this.heeftAangepastTekst
        ? this.aangepastTekst
        : standaardExterneOmschrijvingLijst[0].tekst
      this.standardTextChoiceTarget.value = this.heeftAangepastTekst
        ? 'aangepasteTekst'
        : standaardExterneOmschrijvingIdLijst[0]
      this.updateCharacterCount(externalText.length)
    }
  }
  onChangeHandler() {
    if (this.aangepastTekst === '') {
      this.heeftAangepastTekst = false
    }
    this.update()
  }
  update() {
    const nietOpgelost = this.resolutie === 'niet_opgelost'
    this.standardTextChoiceTarget.value = null
    Array.from(this.standardTextChoiceTarget.querySelectorAll('option')).map((elem) => {
      elem.style.display = 'none'
      elem.checked = false
    })
    Array.from(
      this.element.querySelectorAll(`input[name='${this.nietOpgelostRedenFieldTarget.name}']`)
    ).map((elem) => {
      const li = elem.closest('li')
      li.style.display = nietOpgelost ? 'block' : 'none'
      elem.checked = !nietOpgelost ? false : elem.checked
      console.log(elem.value)
    })

    const nietOpgelostReden = this.element.querySelector(
      `input[name='${this.nietOpgelostRedenFieldTarget.name}']:checked`
    )?.value
    this.filterSpecificaties(nietOpgelostReden)
    const specificatieUrl = this.element.querySelector(
      `input[name='${this.specificatieFieldTarget.name}']:checked`
    )?.value
    console.log(specificatieUrl)
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
