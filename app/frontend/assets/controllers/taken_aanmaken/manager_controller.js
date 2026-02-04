import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = [
    'afdeling',
    'taaktype',
    'searchInput',
    'afdelingTaaktypeContainer',
    'searchResultContainer',
    'geselecteerdeTaaktypesContainer',
    'geselecteerdTaaktype',
    'geselecteerdFormulierTaaktype',
    'geselecteerdFormulierTaaktypeContainer',
    'geselecteerdeTakenHeader',
    'geselecteerdeTakenError',
    'modalSluiten',
    'knopVolgende',
    'knopVorige',
    'knopAanmaken',
    'detail',
  ]
  static values = {
    taaktypes: String,
    openstaandeTaken: String,
    meldingUuid: String,
    gebruiker: String,
  }

  connect() {
    this.taaktypeMax = 10
    this.taaktypes = JSON.parse(this.taaktypesValue)
    const openstaandeTaken = JSON.parse(this.openstaandeTakenValue).map((taak) => {
      return {
        titel: taak.titel,
        uuid: taak._links.self,
        parents: taak.afhankelijkheid.map((afh) => afh.taakopdracht_url),
      }
    })
    const openstaandeTakenUrls = openstaandeTaken.map((elem) => elem.uuid)
    this.openstaandeTaken = openstaandeTaken.map((elem) => {
      return {
        titel: elem.titel,
        uuid: elem.uuid,
        parents: elem.parents.filter((url) => openstaandeTakenUrls.includes(url)),
      }
    })
    this.taaktypeByUrl = this.taaktypes.reduce(
      (o, v) => ((o[v._links.taakapplicatie_taaktype_url] = v), o),
      {}
    )

    window.setTimeout(() => {
      this.searchInputTarget.focus()
    }, 600)
  }
  uuidv4() {
    return '10000000-1000-4000-8000-100000000000'.replace(/[018]/g, (c) =>
      (+c ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (+c / 4)))).toString(16)
    )
  }

  modalSluitenTargetConnected() {}

  afdelingTaaktypeContainerTargetConnected(elem) {
    this.afdelingTaaktypesVisibility(
      elem,
      elem.parentNode.querySelector('label input').hasAttribute('checked')
    )
  }

  searchInputTargetConnected(elem) {
    this.addSearchListener(elem)
  }

  taaktypeTargetConnected(elem) {
    this.addSearchListener(elem)
  }

  searchInputTargetDisConnected(elem) {
    this.removeSearchListener(elem)
  }

  taaktypeTargetDisConnected(elem) {
    this.removeSearchListener(elem)
  }

  addSearchListener(elem) {
    elem.addEventListener('keypress', function (e) {
      if (e.keyCode === 13 || e.which === 13) {
        e.preventDefault()
        return false
      }
    })
  }

  removeSearchListener(elem) {
    elem.removeEventListener('keypress', function (e) {
      if (e.keyCode === 13 || e.which === 13) {
        e.preventDefault()
        return false
      }
    })
  }

  taaktypeBerichtHandler(e) {
    if (e) {
      const target = e.target.closest('details').querySelector('.cta--summary')
      if (e.target.value.length) target.textContent = e.target.value
      target.classList.toggle('has-text', e.target.value.length > 0)
    }
  }

  gotoNextStep() {
    this.element.classList.remove('stap1')
    this.element.classList.add('stap2')
    this.element.querySelector('.modal-body').scrollTop = 0

    if (this.geselecteerdFormulierTaaktypeTargets.length === 1) {
      this.geselecteerdFormulierTaaktypeTargets[0].querySelector('details').setAttribute('open', '')
    } else {
      // this.geselecteerdFormulierTaaktypeTargets[0].querySelector('details').removeAttribute('open')
    }
  }

  gotoPreviousStep() {
    this.element.classList.remove('stap2')
    this.element.classList.add('stap1')
    this.element.querySelector('.modal-body').scrollTop = 0
  }

  showHideSearchResult(e) {
    this.searchResultContainerTarget.style.display =
      e.target.closest('.container__search') != undefined &&
      this.searchInputTarget.value?.length > 0
        ? 'block'
        : 'none'
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
  getAllOptions() {
    const availableElements = this.geselecteerdFormulierTaaktypeTargets.map((elem) => {
      return {
        titel: elem.querySelector('[data-omschrijving]').textContent,
        uuid: elem.dataset.uuid,
        parents: JSON.parse(elem.dataset.parents),
      }
    })
    return [...availableElements, ...this.openstaandeTaken]
  }
  getAvailableParentElements(geselecteerdFormulierTaaktype) {
    const currentElem = {
      uuid: geselecteerdFormulierTaaktype.dataset.uuid,
      parents: JSON.parse(geselecteerdFormulierTaaktype.dataset.parents),
    }
    const allOptions = this.getAllOptions()
    const availableOptions = allOptions.filter((elem) => elem.uuid != currentElem.uuid)

    const geselecteerdFormulierTaaktypeAllParentUuids = this.getAllRelatedUuids(
      allOptions,
      currentElem,
      'parents'
    )
    const availableSelectedUuids = [
      ...availableOptions
        .filter((elem) => currentElem.parents.includes(elem.uuid))
        .map((elem) => elem.uuid),
    ]
    const availableTaken = availableOptions.map((elem) => {
      const elemAllParentUuids = this.getAllRelatedUuids(allOptions, elem, 'parents')
      const isSelected = currentElem.parents.includes(elem.uuid)
      const elemIsChildOfCurrent = elemAllParentUuids.includes(currentElem.uuid)
      const elemIsParentOfCurrent = geselecteerdFormulierTaaktypeAllParentUuids.includes(elem.uuid)
      const elemIsParentOfOthers =
        availableSelectedUuids.filter((value) => elemAllParentUuids.includes(value)).length > 0
      return [
        elem.titel,
        elem.uuid,
        isSelected,
        isSelected ||
          (!elemIsParentOfCurrent && !elemIsChildOfCurrent && !elemIsParentOfOthers && !isSelected),
      ]
    })

    return availableTaken
  }
  parentsSelectedHandler(e) {
    e.preventDefault()
    const geselecteerdFormulierTaaktype = e.target.closest(
      '[data-taken-aanmaken--manager-target="geselecteerdFormulierTaaktype"]'
    )
    const ul = e.target.closest('ul')
    const parentUUID = e.params.parentUuid
    const childUUID = e.params.childUuid
    const active = e.params.active
    const selectedChild = this.geselecteerdFormulierTaaktypeTargets.find(
      (elem) => elem.dataset.uuid === childUUID
    )
    let parents = JSON.parse(selectedChild.dataset.parents)
    !active ? parents.push(parentUUID) : parents.splice(parents.indexOf(parentUUID), 1)
    const parentsArray = [...new Set(parents)]
    parents = JSON.stringify([...new Set(parentsArray)])
    selectedChild.dataset.parents = parents

    // het li element heeft een uniek uuid, dit gebruiken als id voor de popover
    const titels = this.getAllOptions()
      .filter((elem) => parentsArray.includes(elem.uuid))
      .map((elem) => elem.titel)
    console.log('titels', titels)
    const tagElement = geselecteerdFormulierTaaktype.querySelector('[data-status-tag]')
    const popElement = geselecteerdFormulierTaaktype.querySelector('[data-status-pop]')
    if (titels.length) {
      // TODO id dynamisch maken obv uuid van het list-element
      tagElement.setAttribute('interestfor', 111)
      popElement.setAttribute('id', 111)
      popElement.textContent = `Wacht tot de ${
        titels.length == 1 ? 'taak' : 'taken'
      } "${titels.join('" en "')}" ${titels.length == 1 ? 'is' : 'zijn'} uitgevoerd`
    }

    tagElement.style.display = titels.length ? 'block' : 'none'

    let parentsInput = selectedChild.querySelector(`input[name*='-parents']`)
    parentsInput.value = parents
    this.renderParentOptions(selectedChild, ul)
    setTimeout(() => {
      this.removeCurrentParentOptions()
    }, 200)
  }
  getAllRelatedUuids(allOptions, elem, relation) {
    let allRelatedUuids = []
    const getRelatedUuids = (relatedElem) => {
      const uuids = relatedElem[relation]
      allRelatedUuids = [...allRelatedUuids, ...uuids]
      uuids.map((uuid) => {
        const relatedElem = allOptions.find((elem) => elem.uuid === uuid)
        relatedElem && getRelatedUuids(relatedElem)
      })
    }
    getRelatedUuids(elem)
    return [...new Set(allRelatedUuids)]
  }
  removeCurrentParentOptions() {
    Array.from(this.element.querySelectorAll('[data-parents-options-container]')).map(
      (elem) => (elem.innerHTML = '')
    )
  }
  showParentOptionsHandler(e) {
    this.removeCurrentParentOptions()
    const geselecteerdFormulierTaaktype = e.target.closest(
      '[data-taken-aanmaken--manager-target="geselecteerdFormulierTaaktype"]'
    )
    const parentOptionsContainer = geselecteerdFormulierTaaktype.querySelector(
      '[data-parents-options-container]'
    )
    this.renderParentOptions(geselecteerdFormulierTaaktype, parentOptionsContainer)
  }

  renderParentOptions(geselecteerdFormulierTaaktype, ul) {
    ul.innerHTML = ''
    const availableParentElements = this.getAvailableParentElements(geselecteerdFormulierTaaktype)
    availableParentElements.map(([titel, id, selected, active]) => {
      const li = document.createElement('LI')
      const input = document.createElement('INPUT')
      const label = document.createElement('LABEL')
      const span = document.createElement('SPAN')
      span.textContent = titel
      input.type = 'checkbox'
      input.checked = selected
      input.setAttribute('data-action', 'taken-aanmaken--manager#parentsSelectedHandler')
      input.setAttribute('data-taken-aanmaken--manager-parent-uuid-param', id)
      input.setAttribute(
        'data-taken-aanmaken--manager-child-uuid-param',
        geselecteerdFormulierTaaktype.dataset.uuid
      )
      input.setAttribute('data-taken-aanmaken--manager-active-param', selected)
      input.disabled = !active
      label.appendChild(input)
      label.appendChild(span)
      li.appendChild(label)
      ul.appendChild(li)
    })
  }
  taaktypeVerwijderenHandler(e) {
    this.taaktypeVerwijderen(e.target.closest('[data-taaktype-url]').dataset.taaktypeUrl)
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
  geselecteerdFormulierTaaktypeTargetDisconnected(elem) {
    const uuid = elem.dataset.uuid
    this.geselecteerdFormulierTaaktypeTargets.map((elem) => {
      let parents = JSON.parse(elem.dataset.parents)
      parents.includes(uuid) && parents.splice(parents.indexOf(uuid), 1)
      elem.dataset.parents = JSON.stringify(parents)
    })
  }
  resetFormulierTaaktypeIndexes() {
    const taaktypeAantal = this.geselecteerdFormulierTaaktypeTargets.length
    this.knopVolgendeTarget.disabled = taaktypeAantal <= 0
    this.knopAanmakenTarget.disabled = taaktypeAantal <= 0
    this.geselecteerdeTakenHeaderTarget.classList.toggle('hidden', taaktypeAantal <= 0)
    this.geselecteerdeTakenErrorTarget.classList.add('hidden')
    if (taaktypeAantal <= 0) {
      this.gotoPreviousStep()
    }
    this.geselecteerdeTakenErrorTarget.classList.toggle('hidden', taaktypeAantal < this.taaktypeMax)

    this.taaktypeTargets
      .filter((elem) => !elem.checked)
      .map((elem) => (elem.disabled = taaktypeAantal >= this.taaktypeMax))
    this.element.querySelector("input[name='form-TOTAL_FORMS']").value = taaktypeAantal
    this.geselecteerdFormulierTaaktypeTargets.map((elem, i) =>
      this.resetFormulierTaaktypeIndex(elem, i)
    )
  }
  resetFormulierTaaktypeIndex(elem, index) {
    const attributes = ['id', 'for', 'name']
    const fields = [
      'melding_uuid',
      'titel',
      'taakapplicatie_taaktype_url',
      'bericht',
      'gebruiker',
      'uuid',
      'parents',
    ]
    fields.map((field) =>
      attributes.map((attr) => {
        const found = elem.querySelector(`[${attr}*='-${field}']`)
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
    let button = clone.querySelector('button')
    li.dataset.taaktypeUrl = taaktypeUrl
    button.dataset.taaktypeUrl = taaktypeUrl
    let span = clone.querySelector('span')
    span.textContent = this.taaktypeByUrl[taaktypeUrl].omschrijving
    return clone
  }
  geselecteerdTaaktypeFormulierElement(taaktypeUrl) {
    const taaktypeData = this.taaktypeByUrl[taaktypeUrl]
    const uuid = this.uuidv4()
    const template = document.getElementById('template_geselecteerd_formulier_taaktype')
    const clone = template.content.cloneNode(true)
    let li = clone.querySelector('li')
    let taakapplicatieTaaktypeUrlInput = clone.querySelector(
      `input[name*='-taakapplicatie_taaktype_url']`
    )
    let titelInput = clone.querySelector(`input[name*='-titel']`)
    let meldingUuidInput = clone.querySelector(`input[name*='-melding_uuid']`)
    console.log('meldingUuidInput', meldingUuidInput)
    let gebruikerInput = clone.querySelector(`input[name*='-gebruiker']`)
    let uuidInput = clone.querySelector(`input[name*='-uuid']`)
    console.log('uuidInput', uuidInput)

    clone.querySelector('[data-afdelingen]').textContent = taaktypeData.afdelingen
      .map((afd) => afd.naam)
      .join(', ')
    clone.querySelector('[data-verantwoordelijke-afdeling]').textContent =
      taaktypeData.verantwoordelijke_afdeling?.naam
    clone.querySelector('[data-titel]').textContent = taaktypeData.omschrijving
    clone.querySelector('[data-toelichting]').textContent = taaktypeData.toelichting
    clone.querySelector('[data-omschrijving]').textContent = taaktypeData.omschrijving
    const infobutton = clone.querySelector('[data-infosheet-action-param]')
    const target = infobutton.getAttribute('data-infosheet-action-param')
    infobutton.setAttribute(
      'data-infosheet-action-param',
      `${target}${taaktypeData.taakapplicatie_taaktype_url}`
    )
    li.dataset.taaktypeUrl = taaktypeUrl
    taakapplicatieTaaktypeUrlInput.value = taaktypeUrl
    titelInput.value = taaktypeData.omschrijving
    meldingUuidInput.value = this.meldingUuidValue
    gebruikerInput.value = this.gebruikerValue
    uuidInput.value = uuid
    li.dataset.uuid = uuid
    return clone
  }

  smoothScrollTo(container, targetTop, duration = 500) {
    const start = container.scrollTop
    const distance = targetTop - start
    let startTime = null

    function animationStep(timestamp) {
      if (!startTime) startTime = timestamp
      const progress = Math.min((timestamp - startTime) / duration, 1)
      container.scrollTop = start + distance * progress
      if (progress < 1) {
        requestAnimationFrame(animationStep)
      }
    }

    requestAnimationFrame(animationStep)
  }

  openDetails(e) {
    const details = e.target.closest('details')
    details.open = true
    this.toggleDetailsHandler(e)
  }

  toggleDetailsHandler(e) {
    console.log('toggleDetailsHandler')
    if (e.target.closest('details').open) {
      setTimeout(() => {
        const container = e.target.closest('.modal-body')
        const details = e.target.closest('details')
        const containerRect = container.getBoundingClientRect()
        const detailsRect = details.getBoundingClientRect()
        const targetTop = container.scrollTop + (detailsRect.top - containerRect.top)
        this.smoothScrollTo(container, targetTop)

        e.target.closest('details').querySelector('textarea').focus()
      }, 100)
    }
  }
}
