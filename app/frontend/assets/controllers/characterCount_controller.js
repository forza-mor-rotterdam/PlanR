import { Controller } from '@hotwired/stimulus'

const maxCharacterPrefix = 'Aantal karakters: '

export default class extends Controller {
  connect() {
    if (this.element.maxLength >= 0) {
      const maxCharacterElement = document.createElement('small')
      maxCharacterElement.classList.add('help-block', 'no-margin')
      maxCharacterElement.innerHTML = `${maxCharacterPrefix}${this.element.value.length}/${this.element.maxLength}`

      this.element.parentNode.insertBefore(maxCharacterElement, this.element.nextSibling)
      this.updateCharacterCount()
    }
  }

  updateCharacterCount() {
    const count = this.element.value.length
    const maxCount = this.element.maxLength
    const targetElement = this.element.parentNode.querySelector('small')
    if (targetElement) {
      if (maxCount - count >= 0) {
        targetElement.classList.remove('error')
        if (maxCount - count <= 10) {
          targetElement.classList.add('warning')
        } else {
          targetElement.classList.remove('warning', 'error')
        }
      } else {
        targetElement.classList.remove('warning')
        targetElement.classList.add('error')
      }
      targetElement.innerHTML = `${maxCharacterPrefix}${count}/${this.element.maxLength}`
    }
  }

  onChangeText() {
    this.updateCharacterCount()
  }
}
