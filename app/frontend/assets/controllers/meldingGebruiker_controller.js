import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  static values = {
    mercurePublicUrl: String,
    mercureSubscriberToken: String,
    meldingId: String,
    gebruiker: String,
  }
  static targets = ['gebruikerLijst']

  initialize() {
    let self = this
    self.gebruiker = self.hasGebruikerValue ? JSON.parse(self.gebruikerValue) : {}
    self.lastEventId = null
    this.initMessages()
    this.publiceerTopic(self.meldingIdValue)
    window.addEventListener('beforeunload', () => {
      self.eventSource.close()
      self.publiceerTopic(self.meldingIdValue)
    })
    this.element.style.display = 'none'
  }
  isValidHttpUrl(string) {
    let url

    try {
      url = new URL(string)
    } catch (_) {
      return false
    }

    return url.protocol === 'http:' || url.protocol === 'https:'
  }
  initMessages() {
    let self = this
    console.log(self.mercurePublicUrlValue)
    if (self.hasMercurePublicUrlValue && self.isValidHttpUrl(self.mercurePublicUrlValue)) {
      const url = new URL(self.mercurePublicUrlValue)
      url.searchParams.append('topic', window.location.pathname)
      if (self.lastEventId) {
        url.searchParams.append('lastEventId', self.lastEventId)
      }
      if (self.hasMercureSubscriberTokenValue) {
        url.searchParams.append('authorization', self.mercureSubscriberTokenValue)
      }
      self.eventSource = new EventSource(url)
      self.eventSource.onmessage = (e) => self.onMessage(e)
      self.eventSource.onerror = (e) => self.onMessageError(e)
    }
  }
  onMessage(e) {
    this.lastEventId = e.lastEventId
    let data = JSON.parse(e.data)
    console.log('mercure message', data, new Date().toString())
    this.mercureSubscriptions = data
    this.updateGebruikerActiviteit()
  }
  onMessageError(e) {
    let self = this
    console.error(e)
    console.error('An error occurred while attempting to connect.')
    self.eventSource.close()
    setTimeout(() => self.initMessages(), 5000)
  }
  async publiceerTopic(topic) {
    const url = `/publiceer-topic/${topic}/`
    try {
      const response = await fetch(`${url}`, { redirect: 'manual' })
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`)
      }
      const json_resp = await response.json()
      return json_resp
    } catch (error) {
      console.error('Error fetching address details:', await error)
    }
  }

  updateGebruikerActiviteit() {
    const self = this
    if (
      this.gebruikerLijstTarget &&
      self.mercureSubscriptions !== null &&
      Array.isArray(self.mercureSubscriptions)
    ) {
      self.gebruikerLijstTarget.innerHTML = ''
      const subscriptions = this.mercureSubscriptions.filter(
        (sub) => self.gebruiker.email != sub.payload.gebruiker.email
      )
      if (subscriptions.length > 0) {
        this.element.style.display = 'block'
        for (const subscription of subscriptions) {
          let liElem = document.createElement('li')
          let aElem = document.createElement('a')
          aElem.href = ''
          aElem.dataset.action = 'detail#openModal'
          aElem.dataset.detailActionParam = `/gebruiker/gebruiker_info/${subscription.payload.gebruiker.email}`
          aElem.textContent = `${subscription.payload.gebruiker.naam}, ${subscription.payload.gebruiker.email}`
          liElem.appendChild(aElem)
          self.gebruikerLijstTarget.appendChild(liElem)
        }
      } else {
        this.element.style.display = 'none'
      }
    }
  }

  disconnect() {
    if (this.eventSource) {
      this.eventSource.close()
    }
    this.publiceerTopic(this.meldingIdValue)
  }
}
