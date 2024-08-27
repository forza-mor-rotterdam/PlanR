import { Controller } from '@hotwired/stimulus'
// eslint-disable-next-line no-unused-vars
import Select2 from 'select2'

let form = null
// eslint-disable-next-line no-unused-vars
let inputList = null
// eslint-disable-next-line no-unused-vars
let formData = null
const defaultErrorMessage = 'Vul a.u.b. dit veld in.'

export default class extends Controller {
  static targets = [
    'formTaakStarten',
    'afdelingField',
    'taaktypeField',
    'onderwerpGerelateerdTaaktypeField',
  ]

  connect() {
    form = this.formTaakStartenTarget
    formData = new FormData(form)

    form.addEventListener('submit', (event) => {
      if (!this.checkValids()) {
        event.preventDefault()
        const firstError = this.element.querySelector('.is-invalid')
        if (firstError) {
          firstError.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      }
    })
    this.handleTaaktypeChoices()
    this.handleOnderwerpGerelateerdTaaktypeChoices()
  }

  handleTaaktypeChoices() {
    this.afdelingFieldTarget.addEventListener('change', () => {
      const selectedAfdeling = event.target.value
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
    const taaktypes = JSON.parse(this.formTaakStartenTarget.dataset.taakstartenformulierTaaktypes)
    const taaktypeField = this.taaktypeFieldTarget

    // Clear the current taaktype selection and content
    this.clearFieldSelection(taaktypeField)
    taaktypeField.innerHTML = ''

    const ul = document.createElement('ul')
    ul.id = 'id_taaktype'

    const selectedAfdelingTaaktypes = taaktypes.find(([afdeling]) => afdeling === selectedAfdeling)
    if (selectedAfdelingTaaktypes) {
      const [, options] = selectedAfdelingTaaktypes
      options.forEach((taaktype, index) => {
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
        label.textContent = text

        li.appendChild(input)
        li.appendChild(label)
        ul.appendChild(li)
      })
    }

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
    const taaktypes = JSON.parse(this.formTaakStartenTarget.dataset.taakstartenformulierTaaktypes)
    const afdelingField = this.afdelingFieldTarget
    const currentlySelectedAfdeling = afdelingField.querySelector('input:checked')

    let taaktypeBelongsToCurrentAfdeling = false

    if (currentlySelectedAfdeling) {
      const currentAfdelingValue = currentlySelectedAfdeling.value
      taaktypeBelongsToCurrentAfdeling = taaktypes.some(
        ([afdeling, options]) =>
          afdeling === currentAfdelingValue &&
          options.some((option) => option[0] === selectedTaaktype)
      )
    }

    if (!taaktypeBelongsToCurrentAfdeling) {
      for (const [afdeling, options] of taaktypes) {
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
