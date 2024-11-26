import { Controller } from '@hotwired/stimulus'
import { renderStreamMessage } from '@hotwired/turbo'

const snackOverzichtLijstTurboFrameID = 'tf_profiel_notificatie_lijst'

export default class extends Controller {
  static targets = ['snackLijst', 'snackOverzichtItem', 'snackItem', 'toastItem']
  static values = {
    url: String,
    token: String,
    topic: String,
    snackOverzichtAantal: Number,
    snackOverzichtUrl: String,
  }

  connect() {
    this.element.controller = this
    this.snackOverzichtPagina = 0
    this.snackOverzichtFilter = 'alle'
    console.log(`${this.identifier} connected`)

    // this.setList(this.element.classList.value.includes('toast'))
    this.element.addEventListener('notificatieVerwijderd', () => {
      // wacht tot notificatie echt is verwijderd
      setTimeout(() => {
        this.resetSnackLijst(this.element.classList.value.includes('toast'))
      }, 100)
      console.log(this.notificatieTargets.length)
    })

    this.initMessages()

    this.watchedNotificaties = []
    window.addEventListener('beforeunload', () => {
      console.log(`Connected: ${this.identifier}, beforeunload`)
      this.markNotificatiesAsWatched()
    })
  }
  snackOverzichtItemTargetConnected(snackOverzichtItem) {
    console.log(snackOverzichtItem)
  }

  overzichtTab(e) {
    e.preventDefault()
    this.snackOverzichtFilter = e.params.overzichtFilter
    this.snackOverzichtPagina = 0
    this.verwijderAlleSnackOverzichtItems()
    this.laadSnackOverzicht()
  }
  verwijderAlleSnackOverzichtItems() {
    this.snackOverzichtItemTargets.map((elem) => elem.remove())
  }
  async laadMeerSnacks(e) {
    e.preventDefault()
    this.snackOverzichtPagina++
    this.laadSnackOverzicht()
  }
  async laadSnackOverzicht() {
    const url = `${this.snackOverzichtUrlValue}?p=${this.snackOverzichtPagina}&filter=${this.snackOverzichtFilter}`
    console.log(url)
    try {
      const response = await fetch(`${url}`)
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`)
      }
      const text = await response.text()
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
  notificatieTargetConnected() {
    this.setList(this.element.classList.value.includes('toast'))
  }
  setList(isToast) {
    const list = this.notificatieItemTargets
    // eslint-disable-next-line for-direction
    for (let i = list.length - 1; i >= 0; i--) {
      setTimeout(
        () => {
          list[i].classList.add('init')
          if (i === 0) {
            this.element.classList.remove('busy')
          }
        },
        600 * (-i + list.length)
      )
    }

    if (!isToast) {
      this.element.classList.add('busy')
      // Alleen als het geen toast is achter elkaar tonen
      const timeToLeave = list.length > 5 ? list.length * 1000 : 5000
      for (let i = 0; i < list.length; i++) {
        setTimeout(
          () => {
            list[i].classList.replace('init', 'show')
            if (i === 0) {
              list[i].style.transform = `translateY(0) scale(1, 1)`
            } else {
              list[i].style.transform = `translateY(-${
                list[i].offsetTop - list[0].offsetHeight
              }px) translateY(-100%) translateY(${i * 8}px) scale(${1 - i * 0.02}, 1)`
            }
          },
          timeToLeave + 100 * i
        )
      }
    }
  }

  resetSnackLijst() {
    this.snackLijstItem.map((elem, i) => {
      elem.style.transform =
        i === 0
          ? 'translateY(0) scale(1, 1)'
          : `translateY(-${
              elem.offsetTop - this.snackLijstItem[0].offsetHeight
            }px) translateY(-100%) translateY(${i * 8}px) scale(${1 - i * 0.02}, 1)`
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
    const turboFrame = document.getElementById(snackOverzichtLijstTurboFrameID)
    if (turboFrame) {
      turboFrame.reload()
    }
  }
  onMessageOpen(e) {
    console.info('Open mercure connection event', e)
  }
  onMessageError(e) {
    console.error(e, 'An error occurred while attempting to connect.')
    this.es.close()
    this.esGebruiker.close()
    setTimeout(() => this.initMessages(), 5000)
  }
  disconnect() {
    // this.markNotificatiesAsWatched()
    // this.es.close()
    // this.esGebruiker.close()
  }
}
