import { Controller } from '@hotwired/stimulus'

let maxCharacterElement = null
const maxCharacterPrefix = 'Aantal karakters: '

export default class extends Controller {
  connect() {
    if (this.element.maxLength >= 0) {
      maxCharacterElement = document.createElement('small')
      maxCharacterElement.classList.add('help-block', 'no-margin')
      maxCharacterElement.innerHTML = `${maxCharacterPrefix}${this.element.value.length}/${this.element.maxLength}`
      this.element.parentNode.insertBefore(maxCharacterElement, this.element.nextSibling)
    }
  }

  updateCharacterCount(count) {
    if (maxCharacterElement) {
      maxCharacterElement.innerHTML = `${maxCharacterPrefix}${count}/${this.element.maxLength}`
    }
  }

  onChangeText() {
    this.updateCharacterCount(this.element.value.length)
  }
}
