import { Controller } from '@hotwired/stimulus'
import { renderStreamMessage } from '@hotwired/turbo'

export default class extends Controller {
  static targets = [
    'snackLijst',
    'snackOverzichtItem',
    'snackItem',
    'toastItem',
    'snackOverzichtLaadMeer',
  ]
  static values = {
    url: String,
    token: String,
    topicSnack: String,
    topicToast: String,
    snackOverzichtAantal: Number,
    snackOverzichtUrl: String,
  }

  connect() {
    this.element.controller = this
    this.snackOverzichtPagina = 0
    this.snackOverzichtFilter = 'alle'
    this.snackOverzichtPaginaItemsGeladen = []
    console.log(`${this.identifier} connected`)

    this.initMessages()
    this.watchedNotificaties = []
  }
  snackLijstTargetConnected() {
    this.snackLijstTarget.addEventListener('mouseover', () => {
      this.snackLijstTarget.classList.remove('collapsed')
      this.snackLijstTarget.classList.add('expanded')
    })
    this.snackLijstTarget.addEventListener('mouseleave', () => {
      this.snackLijstTarget.classList.remove('expanded')
      this.snackLijstTarget.classList.add('collapsed')
    })
    // setTimeout(() => {
    //   if (!this.snackLijstTarget.classList.contains('expanded')) {
    //     this.snackLijstTarget.classList.add('collapsed')
    //   }
    // }, 5000)
  }
  snackOverzichtLaadMeerTargetConnected() {
    if (this.snackOverzichtPaginaItemsGeladen.length) {
      const firstSnackFromBatch = this.snackOverzichtPaginaItemsGeladen.slice(0)[0]
      const scrollContainer = firstSnackFromBatch.parentElement.parentElement
      scrollContainer.scrollTop = firstSnackFromBatch.offsetTop
    }
    this.snackOverzichtPaginaItemsGeladen = []
  }
  snackItemTargetConnected(snackItem) {
    snackItem.controller.initializeManager(this)
  }
  toastItemTargetConnected(toastItem) {
    toastItem.controller.initializeManager(this)
  }
  snackOverzichtItemTargetConnected(snackOverzichtItem) {
    snackOverzichtItem.controller.initializeManager(this)
    this.snackOverzichtPaginaItemsGeladen.push(snackOverzichtItem)
  }
  snackItemController(notificatieId) {
    return this.snackItemTargets.find((elem) => elem.dataset.id === String(notificatieId))
      ?.controller
  }
  snackOverzichtItemController(notificatieId) {
    return this.snackOverzichtItemTargets.find((elem) => elem.dataset.id === String(notificatieId))
      ?.controller
  }
  async markeerSnackAlsGelezen(notificatieId) {
    const snackItemController = this.snackItemController(notificatieId)
    const snackOverzichtItemController = this.snackOverzichtItemController(notificatieId)
    this.laadSnackOverzicht(`markeer-snack-als-gelezen=${notificatieId}`)
    snackItemController.markeerAlsGelezen()
    snackOverzichtItemController?.markeerAlsGelezen()
  }
  overzichtTab(e) {
    e.preventDefault()
    this.snackOverzichtFilter = e.params.overzichtFilter
    this.snackOverzichtPagina = 0
    this.verwijderAlleSnackOverzichtItems()
    this.laadSnackOverzicht()
  }
  markeerAlleAlsGelezen(e) {
    e.preventDefault()
    this.snackOverzichtFilter = 'alle'
    this.verwijderAlleSnackItems()
    this.verwijderAlleSnackOverzichtItems()
    this.laadSnackOverzicht('markeer-alle-snacks-als-gelezen=true')
  }
  verwijderAlleSnackOverzichtItems() {
    this.snackOverzichtItemTargets.map((elem) => elem.remove())
  }
  verwijderAlleSnackItems() {
    this.snackItemTargets.map((elem) => elem.remove())
  }
  async laadMeerSnacks(e) {
    e.preventDefault()
    this.snackOverzichtPagina++
    this.laadSnackOverzicht()
  }
  async laadSnackOverzicht(paramStr = '') {
    const url = `${this.snackOverzichtUrlValue}?p=${this.snackOverzichtPagina}&filter=${
      this.snackOverzichtFilter
    }${paramStr ? '&' + paramStr : ''}`
    console.log(url)
    try {
      const response = await fetch(`${url}`)
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`)
      }
      const text = await response.text()
      console.log(text)
      renderStreamMessage(text)
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

  addNotificatieUrls() {
    this.profielNotificatieTargets.map((elem) => {
      if (!this.watchedNotificaties.includes(elem.dataset.verwijderUrl)) {
        this.watchedNotificaties.push(elem.dataset.verwijderUrl)
      }
    })
  }
  initMessages() {
    const url = new URL(this.urlValue)
    url.searchParams.append('topic', this.topicSnackValue)
    url.searchParams.append('authorization', this.tokenValue)

    this.es = new EventSource(url)

    this.es.onmessage = (e) => this.onMessage(e)
    this.es.onerror = (e) => this.onMessageError(e)
    this.es.onopen = (e) => this.onMessageOpen(e)
  }
  onMessage(e) {
    let data = JSON.parse(e.data)
    console.log(e)
    console.log('onMessage', data)
    renderStreamMessage(data)
    this.laadSnackOverzicht()
  }
  onMessageOpen(e) {
    console.info('Open mercure connection event', e)
  }
  onMessageError(e) {
    console.error(e, 'An error occurred while attempting to connect.')
    this.es.close()
    setTimeout(() => this.initMessages(), 5000)
  }
  disconnect() {
    this.es.close()
  }
}
