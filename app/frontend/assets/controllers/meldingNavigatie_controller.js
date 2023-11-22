import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static values = {
    meldingUuid: String,
    url: String,
  }

  static targets = ['teller', 'vorige', 'volgende']

  initialize() {
    const meldingIdList = sessionStorage.getItem('meldingIdList').split(',')
    const meldingId = this.meldingUuidValue
    const isCurrentTask = (id) => id === meldingId
    const index = meldingIdList.findIndex(isCurrentTask)
    const url = this.urlValue
    let previousId = 0
    let nextId = 0

    this.tellerTarget.innerHTML = `${index + 1} van ${meldingIdList.length}`

    previousId = meldingIdList[index - 1]
    nextId = meldingIdList[index + 1]

    if (previousId) {
      this.vorigeTarget.setAttribute('href', `${url}${previousId}`)
      this.vorigeTarget.classList.remove('disabled')
    } else {
      this.vorigeTarget.classList.add('disabled')
    }
    if (nextId) {
      this.volgendeTarget.setAttribute('href', `${url}${nextId}`)
      this.volgendeTarget.classList.remove('disabled')
    } else {
      this.volgendeTarget.classList.add('disabled')
    }
  }
}
