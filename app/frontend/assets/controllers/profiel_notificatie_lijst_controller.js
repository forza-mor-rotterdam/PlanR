// turbo_stream_controller.js
import { Controller } from '@hotwired/stimulus'
import { renderStreamMessage } from '@hotwired/turbo'

export default class extends Controller {
  static targets = ['profielNotificatie']
  static values = {
    url: String,
    token: String,
    topic: String,
  }

  connect() {
    this.element.controller = this
    this.initMessages()
    this.watchedNotificaties = []
    window.addEventListener('beforeunload', () => {
      console.log(`Connected: ${this.identifier}, beforeunload`)
      this.markNotificatiesAsWatched()
    })
  }

  initMessages() {
    const url = new URL(this.urlValue)
    url.searchParams.append('topic', this.topicValue)
    url.searchParams.append('authorization', this.tokenValue)

    this.es = new EventSource(url)

    this.es.onmessage = (e) => this.onMessage(e)
    this.es.onerror = (e) => this.onMessageError(e)
    this.es.onopen = (e) => this.onMessageOpen(e)
  }
  onMessage(e) {
    let data = JSON.parse(e.data)
    console.log('onGenericMessage', data)

    renderStreamMessage(data)
    const turboFrame = document.getElementById('tf_profiel_notificatie_lijst')
    if (turboFrame) {
      turboFrame.reload()
    }
  }
  async notificatieSeen(notificatieUrl) {
    const url = notificatieUrl
    try {
      const response = await fetch(`${url}`)
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`)
      }
      return response
    } catch (error) {
      console.error('Error fetching address details:', error.message)
    }
  }
  markNotificatieAsWatched(profiel_notificatie_id) {
    const profiel_notificatie = this.profielNotificatieTargets.find(
      (elem) => elem.id == profiel_notificatie_id
    )
    if (profiel_notificatie) {
      profiel_notificatie.classList.add('is-watched')
    }
  }
  onMessageOpen(e) {
    console.info(e, 'Open')
  }
  onMessageError(e) {
    console.error(e)
    console.error(e, 'An error occurred while attempting to connect.')
    this.es.close()
    this.esGebruiker.close()
    setTimeout(() => this.initMessages(), 5000)
  }

  addNotificatieUrls() {
    this.profielNotificatieTargets.map((elem) => {
      if (!this.watchedNotificaties.includes(elem.dataset.verwijderUrl)) {
        this.watchedNotificaties.push(elem.dataset.verwijderUrl)
      }
    })
  }
  onClickVorige() {
    this.addNotificatieUrls()
  }
  onClickVolgende() {
    this.addNotificatieUrls()
  }
  markNotificatiesAsWatched() {
    this.watchedNotificaties.map((url) => {
      this.notificatieSeen(url)
    })
    this.watchedNotificaties = []
  }
  disconnect() {
    this.markNotificatiesAsWatched()
    this.es.close()
    this.esGebruiker.close()
  }
}
