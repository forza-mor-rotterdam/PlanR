import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = [
    'zoeken',
    'afdeling',
    'taaktype',
    'afdelingTaaktypeContainer',
    'searchResultContainer',
    'geselecteerdeTaaktypesContainer',
    'geselecteerdTaaktype',
    'geselecteerdFormulierTaaktype',
    'geselecteerdFormulierTaaktypeContainer',
    'modalSluiten',
  ]
  static values = {
    afdelingen: String,
    taaktypes: String,
    meldingUuid: String,
    gebruiker: String,
  }

  connect() {
    console.log(`Connect: ${this.identifier}`)
    // this.element.controllers[this.identifier] = this
    this.afdelingen = JSON.parse(this.afdelingenValue)
    this.taaktypes = JSON.parse(this.taaktypesValue)
    this.taaktypeByUrl = this.taaktypes.reduce((o, v) => ((o[v[0]] = v), o), {})
    console.log(this.taaktypes)
    console.log(this.taaktypeByUrl)
    // console.log(this.taaktypes.length)
    // console.log(this.taaktypes)

    this.afdelingTargets.find((elem) => elem.dataset.value == 'Taak suggesties')?.click()
  }
  modalSluitenTargetConnected() {}
  afdelingTaaktypeContainerTargetConnected(elem) {
    this.afdelingTaaktypesVisibility(elem, false)
  }

  gotoNextStep() {
    this.element.classList.remove('stap1')
    this.element.classList.add('stap2')
  }
  searchChangeHandler(e) {
    this.searchResultContainerTarget.style.display = e.target.value.length > 0 ? 'block' : 'none'
  }
  afdelingChangeHandler(e) {
    this.afdelingTaaktypeContainerTargets.map((elem) => {
      this.afdelingTaaktypesVisibility(elem, elem.dataset.afdeling == e.params.afdeling)
    })
  }
  taaktypeChangeHandler(e) {
    this.taaktypeTargets
      .filter((elem) => {
        return elem.dataset.taaktypeUrl == e.params.taaktypeUrl && e.target != elem
      })
      .map((elem) => (elem.checked = e.target.checked))

    if (e.target.checked) {
      this.taaktypeToevoegen(e.params.taaktypeUrl)
    } else {
      this.taaktypeVerwijderen(e.params.taaktypeUrl)
    }
  }

  afdelingTaaktypesVisibility(elem, actief) {
    elem.style.display = actief ? 'flex' : 'none'
  }
  taaktypeToevoegen(taaktypeUrl) {
    this.geselecteerdFormulierTaaktypeContainerTarget.appendChild(
      this.geselecteerdTaaktypeFormulierElement(taaktypeUrl)
    )
    this.geselecteerdeTaaktypesContainerTarget.appendChild(
      this.geselecteerdTaaktypeElement(taaktypeUrl)
    )
    this.resetFormulierTaaktypeIndexes()
  }
  taaktypeVerwijderenHandler(e) {
    this.taaktypeVerwijderen(e.target.dataset.taaktypeUrl)
  }
  taaktypeVerwijderen(taaktypeUrl) {
    this.taaktypeTargets
      .filter((elem) => {
        return elem.dataset.taaktypeUrl == taaktypeUrl
      })
      .map((elem) => (elem.checked = false))

    this.geselecteerdFormulierTaaktypeTargets
      .find((elem) => elem.dataset.taaktypeUrl == taaktypeUrl)
      ?.remove()
    this.geselecteerdTaaktypeTargets
      .find((elem) => elem.dataset.taaktypeUrl == taaktypeUrl)
      ?.remove()
    this.resetFormulierTaaktypeIndexes()
  }
  resetFormulierTaaktypeIndexes() {
    this.element.querySelector("input[name='form-TOTAL_FORMS']").value =
      this.geselecteerdFormulierTaaktypeTargets.length
    this.geselecteerdFormulierTaaktypeTargets.map((elem, i) =>
      this.resetFormulierTaaktypeIndex(elem, i)
    )
  }
  resetFormulierTaaktypeIndex(elem, index) {
    const attributes = ['id', 'for', 'name']
    const fields = ['melding_uuid', 'titel', 'taakapplicatie_taaktype_url', 'bericht', 'gebruiker']
    fields.map((field) =>
      attributes.map((attr) => {
        const found = elem.querySelector(`[${attr}*=${field}]`)
        const newAttr =
          attr == attributes[2] ? `form-${index}-${field}` : `id_form-${index}-${field}`
        found?.setAttribute(attr, newAttr)
      })
    )
  }
  geselecteerdTaaktypeElement(taaktypeUrl) {
    const template = document.getElementById('template_geselecteerd_taaktype')
    const clone = template.content.cloneNode(true)
    let li = clone.querySelector('li')
    let a = clone.querySelector('a')
    li.dataset.taaktypeUrl = taaktypeUrl
    a.dataset.taaktypeUrl = taaktypeUrl
    let span = clone.querySelector('span')
    span.textContent = this.taaktypeByUrl[taaktypeUrl][1]
    return clone
  }
  geselecteerdTaaktypeFormulierElement(taaktypeUrl) {
    const template = document.getElementById('template_geselecteerd_formulier_taaktype')
    const clone = template.content.cloneNode(true)
    let li = clone.querySelector('li')
    let a = clone.querySelector('a')
    let taakapplicatieTaaktypeUrlInput = clone.querySelector(
      `input[name*='-taakapplicatie_taaktype_url']`
    )
    let titelInput = clone.querySelector(`input[name*='-titel']`)
    let meldingUuidInput = clone.querySelector(`input[name*='-melding_uuid']`)
    let gebruikerInput = clone.querySelector(`input[name*='-gebruiker']`)

    li.dataset.taaktypeUrl = taaktypeUrl
    a.dataset.taaktypeUrl = taaktypeUrl
    taakapplicatieTaaktypeUrlInput.value = taaktypeUrl
    titelInput.value = this.taaktypeByUrl[taaktypeUrl][1]
    meldingUuidInput.value = this.meldingUuidValue
    gebruikerInput.value = this.gebruikerValue
    return clone
  }
}
