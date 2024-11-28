import { Controller } from '@hotwired/stimulus'

const MAX_CHARACTERS = 100
export default class extends Controller {
  static targets = ['content']

  connect() {
    this.element.controller = this
    this.contentString = null
    this.manager = null
    let truncatedString = null
    console.log(`${this.identifier} connected`)
    if (this.hasContentTarget) {
      this.contentString = this.contentTarget.innerText
      if (this.contentString.length > MAX_CHARACTERS) {
        truncatedString = `${this.contentString.slice(
          0,
          MAX_CHARACTERS - 13
        )}... <a href="" data-action="notificaties--snack-overzicht-item#readMore">Lees meer</a>`
        this.contentTarget.innerHTML = truncatedString
        this.contentTarget.style.height = `${this.contentTarget.clientHeight}px`
      }
    }
  }
  initializeManager(manager) {
    this.manager = manager
  }
  markeerAlsGelezen() {
    this.element.classList.add('is-watched')
  }
  readMore(e = null) {
    e?.preventDefault()
    this.contentTarget.innerText = this.contentString
    this.contentTarget.style.height = `${this.contentTarget.scrollHeight}px`
  }
}
