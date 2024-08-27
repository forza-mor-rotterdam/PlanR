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

    this.form.addEventListener('submit', (event) => {
      if (!this.checkValids()) {
        event.preventDefault()
        const firstError = this.element.querySelector('.is-invalid')
        if (firstError) {
          firstError.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      }
    })
    this.taaktypes = JSON.parse(this.form.dataset.taakstartenformulierTaaktypes)
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
      const selectedTaaktype = event.target.value
      this.selectCorrespondingOnderwerpGerelateerdTaaktype(selectedTaaktype)
    })
  }

  handleOnderwerpGerelateerdTaaktypeChoices() {
    this.afdelingFieldTarget.addEventListener('change', () => {
      const selectedAfdeling = event.target.value

      this.filterTaaktypes(selectedAfdeling)
    })
    this.onderwerpGerelateerdTaaktypeFieldTarget.addEventListener('change', (event) => {
      const selectedTaaktype = event.target.value
      this.clearSearch()

      this.selectCorrespondingAfdeling(selectedTaaktype)
      const selectedAfdeling = this.afdelingFieldTarget.querySelector('input:checked')
      if (selectedAfdeling) {
        this.filterTaaktypes(selectedAfdeling.value)
      }
      this.selectCorrespondingTaaktype(selectedTaaktype)
    })
  }

  clearFieldSelection(fieldTarget) {
    fieldTarget.querySelectorAll('input[type="radio"]').forEach((radio) => {
      radio.checked = false
      // radio.value = ''
    })
  }

  filterTaaktypes(selectedAfdeling) {
    const taaktypeField = this.taaktypeFieldTarget

    // Clear the current taaktype selection and content
    this.clearFieldSelection(taaktypeField)
    taaktypeField.innerHTML = ''

    const ul = document.createElement('ul')
    ul.id = 'id_taaktype'

    const selectedAfdelingTaaktypes = this.taaktypes.find(
      ([afdeling]) => afdeling === selectedAfdeling
    )
    if (selectedAfdelingTaaktypes) {
      const [, options] = selectedAfdelingTaaktypes
      this.renderTaaktypes(options.map((taaktype) => ({ afdeling: null, taaktype })))
    }
  }

  renderTaaktypes(taaktypes) {
    const taaktypeField = this.taaktypeFieldTarget
    taaktypeField.innerHTML = ''

    const ul = document.createElement('ul')
    ul.id = 'id_taaktype'

    taaktypes.forEach(({ afdeling, taaktype }, index) => {
      const [value, text] = taaktype
      const li = document.createElement('li')

      const input = document.createElement('input')
      input.type = 'radio'
      input.name = 'taaktype'
      input.value = value
      input.id = `id_taaktype_${index}`
      input.className = ''
      input.required = true
      input.setAttribute('data-taakstartenformulier-target', 'taaktypeField')

      const label = document.createElement('label')
      label.htmlFor = `id_taaktype_${index}`
      label.className = 'form-check-label ms-1'
      label.textContent = `${text} ${afdeling ? '(' + afdeling + ')' : ''}`

      li.appendChild(input)
      li.appendChild(label)
      ul.appendChild(li)
    })

    taaktypeField.appendChild(ul)
  }

  selectCorrespondingOnderwerpGerelateerdTaaktype(selectedTaaktype) {
    const onderwerpGerelateerdTaaktypeField = this.onderwerpGerelateerdTaaktypeFieldTarget
    const correspondingRadio = onderwerpGerelateerdTaaktypeField.querySelector(
      `ul input[value="${selectedTaaktype}"]`
    )
    this.clearFieldSelection(onderwerpGerelateerdTaaktypeField)

    if (correspondingRadio) {
      correspondingRadio.checked = true
    }
  }

  selectCorrespondingTaaktype(selectedTaaktype) {
    const taaktypeField = this.taaktypeFieldTarget
    const correspondingRadio = taaktypeField.querySelector(`input[value="${selectedTaaktype}"]`)
    if (correspondingRadio) {
      correspondingRadio.checked = true
    }

    this.selectCorrespondingAfdeling(selectedTaaktype)
  }

  selectCorrespondingAfdeling(selectedTaaktype) {
    const afdelingField = this.afdelingFieldTarget
    const currentlySelectedAfdeling = afdelingField.querySelector('input:checked')
    let taaktypeBelongsToCurrentAfdeling = false
    // this.clearSearch() // Add this line

    if (currentlySelectedAfdeling) {
      const currentAfdelingValue = currentlySelectedAfdeling.value
      taaktypeBelongsToCurrentAfdeling = this.taaktypes.some(
        ([afdeling, options]) =>
          afdeling === currentAfdelingValue &&
          options.some((option) => option[0] === selectedTaaktype)
      )
    }

    if (!taaktypeBelongsToCurrentAfdeling) {
      for (const [afdeling, options] of this.taaktypes) {
        if (options.some((option) => option[0] === selectedTaaktype)) {
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
    this.taaktypeSearchTarget.addEventListener('input', (event) => {
      const searchTerm = event.target.value.toLowerCase()
      if (searchTerm.length >= 2) {
        this.showSearchResults(searchTerm)
      } else {
        this.resetToCurrentAfdeling()
      }
    })
  }

  showSearchResults(searchTerm) {
    const allTaaktypes = this.taaktypes.flatMap(([afdeling, taaktypes]) =>
      taaktypes.map((taaktype) => ({ afdeling, taaktype }))
    )

    const matchingTaaktypes = allTaaktypes.filter(({ taaktype }) =>
      taaktype[1].toLowerCase().includes(searchTerm)
    )

    this.renderTaaktypes(matchingTaaktypes)

    // Maintain the selected taaktype if it exists in the search results
    const selectedTaaktype = this.taaktypeFieldTarget.querySelector('input:checked')?.value
    if (selectedTaaktype) {
      const correspondingRadio = this.taaktypeFieldTarget.querySelector(
        `ul input[value="${selectedTaaktype}"]`
      )
      if (correspondingRadio) {
        correspondingRadio.checked = true
      }
    }
  }

  clearSearch() {
    this.taaktypeSearchTarget.value = ''
  }

  resetToCurrentAfdeling() {
    const selectedAfdeling = this.afdelingFieldTarget.querySelector('input:checked')?.value
    if (selectedAfdeling) {
      this.filterTaaktypes(selectedAfdeling)
    }
  }

  checkValids() {
    let isValid = true
    const formFields = this.formTaakStartenTarget.querySelectorAll(
      'input[type="radio"][required], textarea[required]'
    )

    formFields.forEach((field) => {
      const fieldSet = field.closest('.form-row')
      const errorElement = fieldSet.querySelector('.invalid-text')

      if (field.type === 'radio') {
        const fieldName = field.name
        const isChecked = this.formTaakStartenTarget.querySelector(
          `input[name="${fieldName}"]:checked`
        )
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
