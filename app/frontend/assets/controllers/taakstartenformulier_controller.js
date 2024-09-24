import { Controller } from '@hotwired/stimulus'
const defaultErrorMessage = 'Vul a.u.b. dit veld in.'

export default class extends Controller {
  static targets = [
    'formTaakStarten',
    'afdelingField',
    'taaktypeField',
    'taaktypeContainer',
    'onderwerpGerelateerdTaaktypeField',
    'taaktypeSearch',
    'submitButton',
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
    this.onderwerpGerelateerdTaaktypeFieldTargets.map((elem) => elem.setAttribute('tabindex', '-1'))
    this.afdelingFieldTargets.map((elem) => elem.setAttribute('tabindex', '-1'))

    this.selectedTaaktype =
      this.onderwerpGerelateerdTaaktypeFieldTargets.length > 0
        ? this.onderwerpGerelateerdTaaktypeFieldTargets[0].value
        : null
    this.handleTaaktypeChoices()
    this.handleOnderwerpGerelateerdTaaktypeChoices()
    this.handleSearch()

    if (this.onderwerpGerelateerdTaaktypeFieldTargets.length > 0) {
      setTimeout(() => this.element.querySelector("button[type='submit']").focus(), 1)
    } else {
      setTimeout(() => this.taaktypeSearchTarget.focus(), 1)
    }

    this.selectCorrespondingAfdeling()
    const selectedAfdeling = this.afdelingFieldTarget.querySelector('input:checked')
    if (selectedAfdeling) {
      this.filterTaaktypes(selectedAfdeling.value)
    }
    this.setSubmitButton()
  }

  handleTaaktypeChoices() {
    const self = this

    this.afdelingFieldTarget.addEventListener('change', (event) => {
      const selectedAfdeling = event.target.value
      self.clearSearch()

      self.filterTaaktypes(selectedAfdeling)
      this.onderwerpGerelateerdTaaktypeFieldTargets.map((elem) => (elem.checked = false))
    })
    this.taaktypeContainerTarget.addEventListener('change', (event) => {
      self.selectedTaaktype = event.target.value
      self.selectCorrespondingOnderwerpGerelateerdTaaktype()
      self.setSubmitButton()
    })
  }

  handleOnderwerpGerelateerdTaaktypeChoices() {
    const self = this
    this.afdelingFieldTarget.addEventListener('change', () => {
      const selectedAfdeling = event.target.value
      this.filterTaaktypes(selectedAfdeling)
    })
    this.onderwerpGerelateerdTaaktypeFieldTargets.forEach((radio) => {
      radio.addEventListener('change', (event) => {
        self.selectedTaaktype = event.target.value
        self.clearSearch()
        self.selectCorrespondingAfdeling()
        const selectedAfdeling = self.afdelingFieldTarget.querySelector('input:checked')
        if (selectedAfdeling) {
          self.filterTaaktypes(selectedAfdeling.value)
        }
        self.selectCorrespondingTaaktype()
        self.setSubmitButton()
      })
    })
  }

  clearFieldSelection(fieldTarget) {
    if (fieldTarget) {
      fieldTarget.querySelectorAll('input[type="radio"]').forEach((radio) => {
        radio.checked = false
        // radio.value = ''
      })
    }
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
      const correspondingRadios = this.taaktypeFieldTargets.filter(
        (elem) => elem.value == this.selectedTaaktype
      )
      if (correspondingRadios.length > 0) {
        correspondingRadios[0].checked = true
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
      const correspondingRadios = this.taaktypeFieldTargets.filter(
        (elem) => elem.value == this.selectedTaaktype
      )
      if (correspondingRadios.length > 0) {
        correspondingRadios[0].checked = true
      }
    }

    // Show all afdeling options
    this.afdelingFieldTarget.querySelectorAll('input[type="radio"]').forEach((radio) => {
      radio.closest('li').style.display = ''
    })
  }

  selectCorrespondingOnderwerpGerelateerdTaaktype() {
    const correspondingRadios = this.onderwerpGerelateerdTaaktypeFieldTargets.filter(
      (elem) => elem.value == this.selectedTaaktype
    )

    this.onderwerpGerelateerdTaaktypeFieldTargets.map((elem) => (elem.checked = false))

    if (correspondingRadios.length > 0) {
      correspondingRadios[0].checked = true
    }
  }

  selectCorrespondingTaaktype() {
    const correspondingRadios = this.taaktypeFieldTargets.filter(
      (elem) => elem.value == this.selectedTaaktype
    )
    if (correspondingRadios.length > 0) {
      correspondingRadios[0].checked = true
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
    const self = this
    let debounceTimer
    this.taaktypeSearchTarget.addEventListener('input', (event) => {
      clearTimeout(debounceTimer)
      debounceTimer = setTimeout(() => {
        const searchTerm = event.target.value.toLowerCase().trim()
        if (searchTerm.length >= 2) {
          self.showSearchResults(searchTerm)
        } else {
          self.resetToCurrentAfdeling()
          self.selectFirst()
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
      const correspondingRadios = this.taaktypeFieldTargets.filter(
        (elem) => elem.value == allTaaktypes[0]['taaktype'][0]
      )
      if (correspondingRadios.length > 0) {
        correspondingRadios[0].checked = true
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
    let correspondingRadios = this.taaktypeFieldTargets.filter(
      (elem) => elem.value == currentlySelectedTaaktype
    )
    if (matchingTaaktypes.length > 0 && correspondingRadios.length == 0) {
      currentlySelectedTaaktype = matchingTaaktypes[0]['taaktype'][0]
      correspondingRadios = this.taaktypeFieldTargets.filter(
        (elem) => elem.value == currentlySelectedTaaktype
      )
    }
    if (correspondingRadios.length > 0) {
      correspondingRadios[0].checked = true
      this.selectedTaaktype = currentlySelectedTaaktype
    }
    if (correspondingRadios.length == 0) {
      this.selectedTaaktype = null
    }
    this.afdelingFieldTarget.classList.add('inactive')
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
    this.afdelingFieldTarget.classList.remove('inactive')
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
