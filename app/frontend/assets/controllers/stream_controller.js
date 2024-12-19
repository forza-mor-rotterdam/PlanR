import { Controller } from '@hotwired/stimulus'
import { renderStreamMessage } from '@hotwired/turbo'

export default class extends Controller {
  static targets = []
  static values = {
    streamUrl: String,
  }
  laadStream(params = {}) {
    this.element.dispatchEvent(
      new CustomEvent('sessionCheck', {
        detail: { message: 'ok' },
        bubbles: true,
      })
    )
    const url = new URL(
      `${document.location.protocol}//${document.location.hostname}${
        window.location.port ? ':' + window.location.port : ''
      }${this.streamUrlValue}`
    )
    url.search = new URLSearchParams(params).toString()
    fetch(url)
      .then((response) => response.text())
      .then((text) => renderStreamMessage(text))
  }
}
