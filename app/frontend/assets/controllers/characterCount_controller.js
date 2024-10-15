import { Controller } from '@hotwired/stimulus'

let maxCharacterElement = null
let maxCharactersNum = 0
const maxCharacterPrefix = 'Aantal karakters: '

export default class extends Controller {
  connect() {
    if (this.element.maxLength >= 0) {
      maxCharactersNum = this.element.maxLength
      maxCharacterElement = document.createElement('small')
      maxCharacterElement.classList.add('help-block', 'no-margin')
      maxCharacterElement.innerHTML = `${maxCharacterPrefix}${this.element.value.length}/${maxCharactersNum}`
      this.element.parentNode.insertBefore(maxCharacterElement, this.element.nextSibling)
    }
  }

  updateCharacterCount(count) {
    if (maxCharacterElement) {
      if (maxCharactersNum - count >= 0) {
        maxCharacterElement.classList.remove('error')
        if (maxCharactersNum - count <= 10) {
          maxCharacterElement.classList.add('warning')
        } else {
          maxCharacterElement.classList.remove('warning', 'error')
        }
      } else {
        maxCharacterElement.classList.remove('warning')
        maxCharacterElement.classList.add('error')
      }
      maxCharacterElement.innerHTML = `${maxCharacterPrefix}${count}/${maxCharactersNum}`
    }
  }

  onChangeText() {
    this.updateCharacterCount(this.element.value.length)
  }
}
