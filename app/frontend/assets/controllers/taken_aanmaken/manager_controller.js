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
    meldingUuid: String,
    gebruiker: String,
  }

  connect() {
    this.taaktypeMax = 10
    this.taaktypes = JSON.parse(this.taaktypesValue)
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
      target.textContent = e.target.value.length ? e.target.value : 'Opmerking toevoegen'
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
  getAvailableParentElements(geselecteerdFormulierTaaktype) {
    const geselecteerdFormulierTaaktypeParents = JSON.parse(
      geselecteerdFormulierTaaktype.dataset.parents
    )
    const geselecteerdFormulierTaaktypeChildren = JSON.parse(
      geselecteerdFormulierTaaktype.dataset.children
    )
    console.log('geselecteerdFormulierTaaktypeParents', geselecteerdFormulierTaaktypeParents)
    return this.geselecteerdFormulierTaaktypeTargets
      .filter((elem) => elem != geselecteerdFormulierTaaktype)
      .filter((elem) => {
        // const children = JSON.parse(elem.dataset.children)
        return (
          !geselecteerdFormulierTaaktypeParents.includes(elem.dataset.uuid) &&
          !geselecteerdFormulierTaaktypeChildren.includes(elem.dataset.uuid)
        )
      })
  }
  parentsSelectedHandler(e) {
    e.preventDefault()
    const uuid = this.removeCurrentParentList()
    console.log(e.params.uuid)
    const selectedChild = this.geselecteerdFormulierTaaktypeTargets.find(
      (elem) => elem.dataset.uuid === uuid
    )
    const selectedParent = this.geselecteerdFormulierTaaktypeTargets.find(
      (elem) => elem.dataset.uuid === e.params.uuid
    )
    console.log(selectedParent)

    const parents = JSON.parse(selectedChild.dataset.parents)
    !parents.includes(e.params.uuid) && parents.push(e.params.uuid)
    selectedChild.dataset.parents = JSON.stringify(parents)

    const addChildToParent = (parent, uuidParent, childUuid) => {
      console.log('addChildToParent', parent, childUuid)
      const children = JSON.parse(parent.dataset.children)
      !children.includes(childUuid) && children.push(childUuid)
      parent.dataset.children = JSON.stringify(children)
      const parentParentUuids = JSON.parse(uuidParent.dataset.children)
      parentParentUuids.map((uuid) => {
        console.log('parent uuids', uuid)
        const parentParent = this.geselecteerdFormulierTaaktypeTargets.find(
          (elem) => elem.dataset.uuid === uuid
        )
        addChildToParent(selectedParent, parentParent, uuid)
      })
    }
    addChildToParent(selectedParent, selectedParent, uuid)
  }
  removeCurrentParentList() {
    const parentsList = this.element.querySelector('[data-parents-list]')
    const uuid = parentsList?.dataset.parentsList
    parentsList && parentsList.remove()
    return uuid
  }
  taaktypeAfhankelijkheidHandler(e) {
    this.removeCurrentParentList()
    const geselecteerdFormulierTaaktype = e.target.closest(
      '[data-taken-aanmaken--manager-target="geselecteerdFormulierTaaktype"]'
    )
    const summary = e.target.closest('summary')
    const right = summary.getBoundingClientRect().right - e.target.getBoundingClientRect().right
    const ul = document.createElement('UL')
    ul.dataset.parentsList = geselecteerdFormulierTaaktype.dataset.uuid
    ul.style.background = 'white'
    ul.style.position = 'absolute'
    ul.style.top = '0px'
    ul.style.right = right + 'px'

    const availableParentElements = this.getAvailableParentElements(geselecteerdFormulierTaaktype)
    availableParentElements.map((elem) => {
      const li = document.createElement('LI')
      const a = document.createElement('A')
      const input = document.createElement('INPUT')
      const label = document.createElement('LABEL')
      input.type = 'checkbox'
      label.textContent = elem.dataset.uuid
      label.appendChild(input)
      ul.appendChild(li)
      li.appendChild(a)
      a.href = '#'
      a.setAttribute('data-action', 'taken-aanmaken--manager#parentsSelectedHandler')
      a.setAttribute('data-taken-aanmaken--manager-uuid-param', elem.dataset.uuid)
      a.textContent = elem.dataset.uuid
      summary.appendChild(ul)
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
    li.dataset.uuid = uuid
    li.dataset.children = '[]'
    li.dataset.parents = '[]'

    let taakapplicatieTaaktypeUrlInput = clone.querySelector(
      `input[name*='-taakapplicatie_taaktype_url']`
    )
    let titelInput = clone.querySelector(`input[name*='-titel']`)
    let meldingUuidInput = clone.querySelector(`input[name*='-melding_uuid']`)
    let gebruikerInput = clone.querySelector(`input[name*='-gebruiker']`)
    let uuidInput = clone.querySelector(`input[name*='-gebruiker']`)

    clone.querySelector('[data-afdelingen]').textContent = taaktypeData.afdelingen
      .map((afd) => afd.naam)
      .join(', ')
    clone.querySelector('[data-verantwoordelijke-afdeling]').textContent = uuid
    // clone.querySelector('[data-verantwoordelijke-afdeling]').textContent =
    // taaktypeData.verantwoordelijke_afdeling?.naam
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

  toggleDetailsHandler(e) {
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
