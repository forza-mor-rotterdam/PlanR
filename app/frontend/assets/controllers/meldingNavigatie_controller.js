import { Controller } from '@hotwired/stimulus'

// let meldingIdList = []
// let previousId = 0
// let nextId = 0
export default class extends Controller {
  static values = {
    meldingUuid: String,
    url: String,
  }

  static targets = ['navigatie', 'teller', 'vorige', 'volgende']

  initialize() {
    const meldingIdString = sessionStorage.getItem('meldingIdList') || ''
    const meldingIdList = meldingIdString.split(',')
    if (meldingIdList.length > 1) {
      const meldingId = this.meldingUuidValue
      const isCurrentTask = (id) => id === meldingId
      const index = meldingIdList.findIndex(isCurrentTask)
      const url = this.urlValue

      this.tellerTarget.innerHTML = `${index + 1} van ${meldingIdList.length}`

      const previousId = meldingIdList[index - 1]
      const nextId = meldingIdList[index + 1]

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
    } else {
      this.navigatieTarget.classList.add('hidden')
    }
  }
}
