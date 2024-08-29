import { Controller } from '@hotwired/stimulus'
const defaultErrorMessage = 'Vul a.u.b. dit veld in.'

export default class extends Controller {
  static targets = [
    'formTaakStarten',
    'afdelingField',
    'taaktypeField',
    'onderwerpGerelateerdTaaktypeField',
    'taaktypeSearch',
  ]

  connect() {
    this.form = this.formTaakStartenTarget
    this.formData = new FormData(this.form)
    const initialAfdeling = this.formTaakStartenTarget.dataset.initialAfdeling
    this.taaktypes = JSON.parse(this.form.dataset.taakstartenformulierTaaktypes)
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

    if (initialAfdeling) {
      this.filterTaaktypes(initialAfdeling)
    }
    this.handleTaaktypeChoices()
    this.handleOnderwerpGerelateerdTaaktypeChoices()
    this.handleSearch()
  }

  handleTaaktypeChoices() {
    this.afdelingFieldTarget.addEventListener('change', () => {
      const selectedAfdeling = event.target.value
      this.clearSearch()

      this.filterTaaktypes(selectedAfdeling)
      this.clearFieldSelection(this.onderwerpGerelateerdTaaktypeFieldTarget)
    })

    this.taaktypeFieldTarget.addEventListener('change', (event) => {
      this.selectedTaaktype = event.target.value
      this.selectCorrespondingOnderwerpGerelateerdTaaktype()
    })
  }

  handleOnderwerpGerelateerdTaaktypeChoices() {
    this.afdelingFieldTarget.addEventListener('change', () => {
      const selectedAfdeling = event.target.value

      this.filterTaaktypes(selectedAfdeling)
    })
    this.onderwerpGerelateerdTaaktypeFieldTarget.addEventListener('change', (event) => {
      this.selectedTaaktype = event.target.value
      this.clearSearch()

      this.selectCorrespondingAfdeling()
      const selectedAfdeling = this.afdelingFieldTarget.querySelector('input:checked')
      if (selectedAfdeling) {
        this.filterTaaktypes(selectedAfdeling.value)
      }
      this.selectCorrespondingTaaktype()
    })
  }

  clearFieldSelection(fieldTarget) {
    fieldTarget.querySelectorAll('input[type="radio"]').forEach((radio) => {
      radio.checked = false
      // radio.value = ''
    })
  }

  filterTaaktypes(selectedAfdeling) {
    const selectedAfdelingTaaktypes = this.taaktypes.find(
      ([afdeling]) => afdeling === selectedAfdeling
    )

    if (selectedAfdelingTaaktypes) {
      const [afdeling, options] = selectedAfdelingTaaktypes
      const taaktypesToRender = options.map((taaktype) => ({ afdeling, taaktype }))
      this.renderTaaktypes(taaktypesToRender)
    } else {
      // If no matching afdeling is found, render an empty list
      this.renderTaaktypes([])
    }

    // Update the selected afdeling radio button
    const selectedAfdelingRadio = this.afdelingFieldTarget.querySelector(
      `input[value="${selectedAfdeling}"]`
    )
    if (selectedAfdelingRadio) {
      selectedAfdelingRadio.checked = true
    }

    // Maintain the selected taaktype if it belongs to the current afdeling
    if (this.selectedTaaktype) {
      const correspondingRadio = this.taaktypeFieldTarget.querySelector(
        `input[value="${this.selectedTaaktype}"]`
      )
      if (correspondingRadio) {
        correspondingRadio.checked = true
      } else {
        // If the selected taaktype is not in the current afdeling, clear the selection
        this.selectedTaaktype = null
      }
    }
  }

  renderTaaktypes(taaktypes) {
    const taaktypeField = this.taaktypeFieldTarget
    taaktypeField.innerHTML = ''

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
      label.innerHTML = `${text} ${
        afdeling ? '(<strong class="green">' + afdeling + '</strong>)' : ''
      }`

      li.appendChild(input)
      li.appendChild(label)
      ul.appendChild(li)
    })
    wrapper.appendChild(ul)
    div.appendChild(wrapper)
    taaktypeField.appendChild(div)
  }

  renderAllTaaktypes() {
    const allTaaktypes = this.taaktypes.flatMap(([afdeling, taaktypes]) =>
      taaktypes.map((taaktype) => ({ afdeling, taaktype }))
    )
    this.renderTaaktypes(allTaaktypes)

    // Restore the previously selected taaktype if it exists
    if (this.selectedTaaktype) {
      const correspondingRadio = this.taaktypeFieldTarget.querySelector(
        `ul input[value="${this.selectedTaaktype}"]`
      )
      if (correspondingRadio) {
        correspondingRadio.checked = true
      }
    }

    // Show all afdeling options
    this.afdelingFieldTarget.querySelectorAll('input[type="radio"]').forEach((radio) => {
      radio.closest('li').style.display = ''
    })
  }

  selectCorrespondingOnderwerpGerelateerdTaaktype() {
    const onderwerpGerelateerdTaaktypeField = this.onderwerpGerelateerdTaaktypeFieldTarget
    const correspondingRadio = onderwerpGerelateerdTaaktypeField.querySelector(
      `ul input[value="${this.selectedTaaktype}"]`
    )
    this.clearFieldSelection(onderwerpGerelateerdTaaktypeField)

    if (correspondingRadio) {
      correspondingRadio.checked = true
    }
  }

  selectCorrespondingTaaktype() {
    const taaktypeField = this.taaktypeFieldTarget
    const correspondingRadio = taaktypeField.querySelector(
      `input[value="${this.selectedTaaktype}"]`
    )
    if (correspondingRadio) {
      correspondingRadio.checked = true
    }

    this.selectCorrespondingAfdeling()
  }

  selectCorrespondingAfdeling() {
    const afdelingField = this.afdelingFieldTarget
    const currentlySelectedAfdeling = afdelingField.querySelector('input:checked')
    let taaktypeBelongsToCurrentAfdeling = false
    // this.clearSearch() // Add this line

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
          const correspondingRadio = afdelingField.querySelector(`input[value="${afdeling}"]`)
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
        }
      }, 300) // 300ms debounce
    })
  }

  showSearchResults(searchTerm) {
    const allTaaktypes = this.taaktypes.flatMap(([afdeling, taaktypes]) =>
      taaktypes.map((taaktype) => ({ afdeling, taaktype }))
    )

    const matchingTaaktypes = allTaaktypes.filter(({ taaktype }) =>
      taaktype[1].toLowerCase().includes(searchTerm)
    )

    // Store the currently selected taaktype before rendering
    const currentlySelectedTaaktype =
      this.selectedTaaktype || this.taaktypeFieldTarget.querySelector('input:checked')?.value

    this.renderTaaktypes(matchingTaaktypes)

    // After rendering, check if the previously selected taaktype is in the search results
    if (currentlySelectedTaaktype) {
      const correspondingRadio = this.taaktypeFieldTarget.querySelector(
        `ul input[value="${currentlySelectedTaaktype}"]`
      )
      if (correspondingRadio) {
        correspondingRadio.checked = true
        this.selectedTaaktype = currentlySelectedTaaktype
      }
    }

    this.afdelingFieldTarget.classList.add('inactive')
  }

  clearSearch() {
    this.taaktypeSearchTarget.value = ''
  }

  resetToCurrentAfdeling() {
    const selectedAfdeling = this.afdelingFieldTarget.querySelector('input:checked')?.value
    this.afdelingFieldTarget.classList.remove('inactive')
    if (selectedAfdeling) {
      this.filterTaaktypes(selectedAfdeling)
    }
  }

  checkValids() {
    let isValid = true
    const formFields = this.form.querySelectorAll(
      'input[type="radio"][required], textarea[required]'
    )

    formFields.forEach((field) => {
      const fieldSet = field.closest('.form-row')
      const errorElement = fieldSet.querySelector('.invalid-text')

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
    if (errorElement) errorElement.textContent = message
  }

  clearError(element, errorElement) {
    if (element) element.classList.remove('is-invalid')
    if (errorElement) errorElement.textContent = ''
  }
}
