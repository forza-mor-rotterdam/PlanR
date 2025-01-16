import { Controller } from '@hotwired/stimulus'
const defaultErrorMessage = 'Vul a.u.b. dit veld in.'

export default class extends Controller {
  static values = {
    initialAfdeling: String,
    taaktypes: String,
  }
  static targets = [
    'formTaakStarten',
    'afdelingField',
    'taaktypeField',
    'taaktypeContainer',
    'afdelingContainer',
    'onderwerpGerelateerdTaaktypeField',
    'onderwerpGerelateerdTaaktypeContainer',
    'taaktypeSearch',
    'submitButton',
  ]

  connect() {
    this.form = this.formTaakStartenTarget
    this.formData = new FormData(this.form)
    this.taaktypes = JSON.parse(this.taaktypesValue)
    this.selectedTaaktype = null

    this.form.addEventListener('submit', (event) => {
      if (!this.checkValids()) {
        event.preventDefault()
        const firstError = this.element.querySelector('.is-invalid')
        if (firstError) {
          firstError.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      }
    })
    this.selectedTaaktype =
      this.onderwerpGerelateerdTaaktypeFieldTargets.length > 0
        ? this.onderwerpGerelateerdTaaktypeFieldTargets[0].value
        : null

    this.handleTaaktypeChoices()
    this.handleAfdelingChoices()
    this.handleOnderwerpGerelateerdTaaktypeChoices()
    this.handleSearch()

    if (this.onderwerpGerelateerdTaaktypeFieldTargets.length > 0) {
      setTimeout(() => this.element.querySelector("button[type='submit']").focus(), 1)
    } else {
      setTimeout(() => this.taaktypeSearchTarget.focus(), 1)
    }

    let selectedAfdeling = null //this.initialAfdelingValue // enable for initial afdeling select
    if (!selectedAfdeling) {
      selectedAfdeling = this.afdelingFieldTargets.find((elem) => elem.checked)
      selectedAfdeling = selectedAfdeling && selectedAfdeling.value
    }
    this.selectCorrespondingAfdeling()
    if (selectedAfdeling) {
      this.filterTaaktypes(selectedAfdeling)
    }
    this.setSubmitButton()
  }

  handleTaaktypeChoices() {
    this.taaktypeContainerTarget.addEventListener('change', (event) => {
      this.selectedTaaktype = event.target.value
      this.selectCorrespondingOnderwerpGerelateerdTaaktype()
      this.setSubmitButton()
    })
  }
  handleAfdelingChoices() {
    this.afdelingContainerTarget.addEventListener('change', (e) => {
      const selectedAfdeling = e.target
      this.afdelingFieldTargets.map((elem) => elem.parentNode.classList.remove('checked'))
      e.target.parentNode.classList.add('checked')
      this.clearSearch()
      this.filterTaaktypes(selectedAfdeling.value)
      this.onderwerpGerelateerdTaaktypeFieldTargets.map((elem) => (elem.checked = false))
      this.selectCorrespondingOnderwerpGerelateerdTaaktype()
      this.setSubmitButton()
    })
  }
  handleOnderwerpGerelateerdTaaktypeChoices() {
    this.onderwerpGerelateerdTaaktypeContainerTarget.addEventListener('change', (event) => {
      this.selectedTaaktype = event.target.value
      this.clearSearch()
      this.selectCorrespondingAfdeling()
      const selectedAfdeling = this.afdelingFieldTargets.find((elem) => elem.checked)
      if (selectedAfdeling) {
        this.filterTaaktypes(selectedAfdeling.value)
      }
      this.setSubmitButton()
    })
  }
  filterTaaktypes(selectedAfdeling) {
    const selectedAfdelingTaaktypes = this.taaktypes.find(([afdeling]) => {
      return afdeling === selectedAfdeling
    })
    if (selectedAfdelingTaaktypes) {
      const [afdeling, options] = selectedAfdelingTaaktypes
      const taaktypesToRender = options.map((taaktype) => ({ afdeling, taaktype }))
      this.renderTaaktypes(taaktypesToRender)
    } else {
      // If no matching afdeling is found, render an empty list
      this.renderTaaktypes([])
    }

    // Update the selected afdeling radio button
    const selectedAfdelingRadio = this.afdelingFieldTargets.find(
      (elem) => elem.value == selectedAfdeling
    )
    if (selectedAfdelingRadio) {
      selectedAfdelingRadio.checked = true
      this.afdelingFieldTargets.map((elem) => elem.parentNode.classList.remove('checked'))
      selectedAfdelingRadio.parentNode.classList.add('checked')
    }

    // Maintain the selected taaktype if it belongs to the current afdeling
    if (this.selectedTaaktype) {
      const correspondingRadios = this.taaktypeFieldTargets.find(
        (elem) => elem.value == this.selectedTaaktype
      )
      if (correspondingRadios) {
        correspondingRadios.checked = true
      } else {
        this.selectedTaaktype = null
      }
    }
    this.selectCorrespondingOnderwerpGerelateerdTaaktype()
    this.setSubmitButton()
  }

  renderTaaktypes(taaktypes, attach_afdeling = false) {
    const taaktypeField = this.taaktypeContainerTarget
    taaktypeField.textContent = ''

    const ul = document.createElement('ul')
    const div = document.createElement('div')
    const wrapper = document.createElement('div')
    div.className = 'form-row'
    wrapper.className = 'wrapper__columns'

    ul.id = 'id_taaktype'
    ul.className = 'form-check-input'

    taaktypes.forEach(({ afdeling, taaktype }, index) => {
      const [value, text] = taaktype
      const li = document.createElement('li')

      const input = document.createElement('input')
      input.type = 'radio'
      input.name = 'taaktype'
      input.value = value
      input.id = `id_taaktype_${index}`
      input.className = 'form-check-input'
      input.required = true
      input.setAttribute('data-taakstartenformulier-target', 'taaktypeField')

      const label = document.createElement('label')
      label.htmlFor = `id_taaktype_${index}`
      label.className = 'form-check-label'
      label.textContent = `${text}`
      if (afdeling && attach_afdeling) {
        const strong = document.createElement('strong')
        strong.className = 'green'
        strong.textContent = ` ${afdeling}`
        label.appendChild(strong)
      }
      li.appendChild(input)
      li.appendChild(label)

      ul.appendChild(li)
    })
    wrapper.appendChild(ul)
    div.appendChild(wrapper)

    // Add error message element
    const errorElement = document.createElement('p')
    errorElement.className = 'help-block invalid-text'
    errorElement.setAttribute('data-error-for', 'taaktype')
    errorElement.style.display = 'none' // Initially hidden
    div.appendChild(errorElement)

    taaktypeField.appendChild(div)
  }

  renderAllTaaktypes() {
    const allTaaktypes = this.taaktypes.flatMap(([afdeling, taaktypes]) =>
      taaktypes.map((taaktype) => ({ afdeling, taaktype }))
    )
    this.renderTaaktypes(allTaaktypes)

    // Restore the previously selected taaktype if it exists
    if (this.selectedTaaktype) {
      const correspondingRadio = this.taaktypeFieldTargets.find(
        (elem) => elem.value == this.selectedTaaktype
      )
      if (correspondingRadio) {
        correspondingRadio.checked = true
      }
    }

    // Show all afdeling options
    this.afdelingContainerTarget.querySelectorAll('input[type="radio"]').forEach((radio) => {
      radio.closest('li').style.display = ''
    })
  }

  selectCorrespondingOnderwerpGerelateerdTaaktype() {
    const correspondingRadio = this.onderwerpGerelateerdTaaktypeFieldTargets.find(
      (elem) => elem.value == this.selectedTaaktype
    )

    this.onderwerpGerelateerdTaaktypeFieldTargets.map((elem) => (elem.checked = false))

    if (correspondingRadio) {
      correspondingRadio.checked = true
    }
  }
  selectCorrespondingAfdeling() {
    const currentlySelectedAfdeling = this.afdelingFieldTargets.find((elem) => elem.checked)
    let taaktypeBelongsToCurrentAfdeling = false

    if (currentlySelectedAfdeling) {
      const currentAfdelingValue = currentlySelectedAfdeling.value
      taaktypeBelongsToCurrentAfdeling = this.taaktypes.some(
        ([afdeling, options]) =>
          afdeling === currentAfdelingValue &&
          options.some((option) => option[0] === this.selectedTaaktype)
      )
    }

    if (!taaktypeBelongsToCurrentAfdeling) {
      for (const [afdeling, options] of this.taaktypes) {
        if (options.some((option) => option[0] === this.selectedTaaktype)) {
          const correspondingRadio = this.afdelingFieldTargets.find(
            (elem) => elem.value == afdeling
          )
          if (correspondingRadio) {
            correspondingRadio.checked = true
          }
          break
        }
      }
    }
  }
  handleSearch() {
    let debounceTimer
    this.taaktypeSearchTarget.addEventListener('input', (event) => {
      clearTimeout(debounceTimer)
      debounceTimer = setTimeout(() => {
        const searchTerm = event.target.value.toLowerCase().trim()
        if (searchTerm.length >= 2) {
          this.showSearchResults(searchTerm)
        } else {
          this.resetToCurrentAfdeling()
          this.selectFirst()
        }
        this.setSubmitButton()
      }, 300) // 300ms debounce
    })
  }
  selectFirst() {
    const allTaaktypes = this.taaktypes.flatMap(([afdeling, taaktypes]) =>
      taaktypes.map((taaktype) => ({ afdeling, taaktype }))
    )
    if (allTaaktypes.length > 0) {
      const correspondingRadio = this.taaktypeFieldTargets.find(
        (elem) => elem.value == allTaaktypes[0]['taaktype'][0]
      )
      if (correspondingRadio) {
        correspondingRadio.checked = true
        this.selectedTaaktype = allTaaktypes[0]['taaktype'][0]
      }
    }
    this.selectCorrespondingOnderwerpGerelateerdTaaktype()
  }
  showSearchResults(searchTerm) {
    const allTaaktypes = this.taaktypes.flatMap(([afdeling, taaktypes]) =>
      taaktypes.map((taaktype) => ({ afdeling, taaktype }))
    )

    const allMatchingTaaktypes = allTaaktypes.filter(({ taaktype }) =>
      taaktype[1].toLowerCase().includes(searchTerm)
    )
    const matchingTaaktypes = [
      ...new Map(allMatchingTaaktypes.map((item) => [item['taaktype'][0], item])).values(),
    ]
    // Store the currently selected taaktype before rendering
    let currentlySelectedTaaktype =
      this.selectedTaaktype ||
      this.element.querySelector("input[type='radio'][name='taaktype']:checked")?.value

    this.renderTaaktypes(matchingTaaktypes)

    // After rendering, check if the previously selected taaktype is in the search results
    let correspondingRadio = this.taaktypeFieldTargets.find(
      (elem) => elem.value == currentlySelectedTaaktype
    )
    if (matchingTaaktypes.length > 0 && !correspondingRadio) {
      currentlySelectedTaaktype = matchingTaaktypes[0]['taaktype'][0]
      correspondingRadio = this.taaktypeFieldTargets.find(
        (elem) => elem.value == currentlySelectedTaaktype
      )
    }
    if (correspondingRadio) {
      correspondingRadio.checked = true
      this.selectedTaaktype = currentlySelectedTaaktype
    }
    if (!correspondingRadio) {
      this.selectedTaaktype = null
    }
    this.afdelingContainerTargets.map((elem) => elem.classList.add('inactive'))
    this.selectCorrespondingOnderwerpGerelateerdTaaktype()
  }
  setSubmitButton() {
    const taaktypeElements = this.element.querySelector(
      "input[type='radio'][name='taaktype']:checked"
    )
    const hasTaaktype = taaktypeElements && taaktypeElements.value
    if (this.hasSubmitButtonTarget && !hasTaaktype) {
      this.submitButtonTarget.setAttribute('disabled', 'true')
    } else if (this.hasSubmitButtonTarget && !!hasTaaktype) {
      this.submitButtonTarget.removeAttribute('disabled')
    }
  }
  clearSearch() {
    this.taaktypeSearchTarget.value = ''
    this.afdelingContainerTargets.map((elem) => elem.classList.remove('inactive'))
  }

  resetToCurrentAfdeling() {
    const selectedAfdeling = this.afdelingFieldTargets.find((elem) => elem.checked)
    this.afdelingContainerTargets.map((elem) => elem.classList.remove('inactive'))
    if (selectedAfdeling) {
      this.filterTaaktypes(selectedAfdeling.value)
    }
  }

  checkValids() {
    let isValid = true
    const formFields = this.form.querySelectorAll(
      'input[type="radio"][required], textarea[required]'
    )
    formFields.forEach((field) => {
      const fieldSet = field.closest('.form-row')
      const errorElement = fieldSet.querySelector('.help-block.invalid-text')

      if (field.type === 'radio') {
        const fieldName = field.name
        const isChecked = this.form.querySelector(`input[name="${fieldName}"]:checked`)
        if (!isChecked) {
          this.showError(fieldSet, errorElement, defaultErrorMessage)
          isValid = false
        } else {
          this.clearError(fieldSet, errorElement)
        }
      } else if (field.type === 'textarea' && !field.value.trim()) {
        this.showError(fieldSet, errorElement, defaultErrorMessage)
        isValid = false
      } else {
        this.clearError(fieldSet, errorElement)
      }
    })

    return isValid
  }

  showError(element, errorElement, message) {
    if (element) element.classList.add('is-invalid')
    if (errorElement) {
      errorElement.textContent = message
      errorElement.style.display = 'block'
    }
  }

  clearError(element, errorElement) {
    if (element) element.classList.remove('is-invalid')
    if (errorElement) {
      errorElement.textContent = ''
      errorElement.style.display = 'none'
    }
  }
}
