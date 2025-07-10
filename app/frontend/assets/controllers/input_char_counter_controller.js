import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  connect() {
    this.externalTextMaxCharacterPrefix = 'Aantal karakters: '
    this.externalTextMaxCharacter = document.createElement('small')
    this.element.parentNode.insertBefore(this.externalTextMaxCharacter, this.element.nextSibling)
    this.externalTextMaxCharacter.classList.add('help-block', 'no-margin')
    this.updateCharacterCount()
  }
  onTextChangeHandler() {
    this.updateCharacterCount()
  }
  updateCharacterCount() {
    this.externalTextMaxCharacter.innerHTML = `${this.externalTextMaxCharacterPrefix}${this.element.value.length}/${this.element.maxLength}`
  }
}
