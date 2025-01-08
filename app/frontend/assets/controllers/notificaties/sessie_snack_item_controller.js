import SnackItemController from './snack_item_controller'
import { renderStreamMessage } from '@hotwired/turbo'

export default class extends SnackItemController {
  static targets = ['link', 'sluitKnop']

  connect() {
    this.element.controllers = this.element.controllers || {}
    this.element.controllers[this.identifier] = this
    this.classList = ['warning', 'error', 'info', 'debug', 'success']
    this.resterendeTijd = ''
    this.status = null
    this.sessieStatus = {
      verlengbaar: {
        titel: 'Verlengbaar',
        content: () => `Vernieuw de pagina binnen ${this.resterendeTijd}`,
        toonSluitKnop: false,
        toonLink: true,
        linkTekst: 'sessie&nbsp;verlengen',
        cssClass: 'info',
      },
      nietVerlengbaar: {
        titel: 'Niet verlengbaar',
        content: () => `Je wordt uitgelogd over ${this.resterendeTijd}`,
        toonSluitKnop: true,
        toonLink: false,
        linkTekst: '',
        cssClass: 'warning',
      },
      bijnaUitgelogd: {
        titel: 'Bijna uitgelogd',
        content: () => `Je wordt uitgelogd over ${this.resterendeTijd}`,
        cssClass: 'error',
      },
      uitgelogd: {
        titel: 'Uitgelogd',
        content: () => `Je bent uitgelogd!`,
        toonSluitKnop: false,
        toonLink: true,
        linkTekst: 'opnieuw&nbsp;inloggen',
        cssClass: 'error',
      },
    }
  }
  getContent(tekst) {
    return tekst
  }
  setStatus(status, resterendeTijd) {
    this.status = status
    const minuten = Math.floor((resterendeTijd / 60) % 60)
    this.resterendeTijd =
      status != 'bijnaUitgelogd'
        ? minuten > 1
          ? `${minuten} minuten`
          : '1 minuut'
        : `${resterendeTijd} seconden`

    this.titelTarget.innerHTML = this.sessieStatus[status].titel
    this.sluitKnopTarget.style.display = this.sessieStatus[status].toonSluitKnop ? 'block' : 'none'
    this.linkTarget.style.display = this.sessieStatus[status].toonLink ? 'block' : 'none'
    this.linkTarget.querySelector('a').innerHTML = this.sessieStatus[status].linkTekst
    this.contentTarget.innerHTML = this.sessieStatus[status].content()
    this.element.classList.remove(...this.classList)
    this.element.classList.add(this.sessieStatus[status].cssClass)
  }
  verlengSessieHandler(e) {
    if (this.status != 'uitgelogd') {
      e.preventDefault()
      fetch('/gebruiker/stream/')
        .then((response) => response.text())
        .then((text) => renderStreamMessage(text))
    }
  }
  sluitSnack() {
    this.markeerAlsGelezen()
  }
}
