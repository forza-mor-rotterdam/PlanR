import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  static targets = ['filterOverview']

  connect() {
    const inputList = document.getElementsByTagName('input')
    for (let i = 0; i < inputList.length; i++) {
      inputList[i].addEventListener('change', this.onInputChange)
    }

    //hide dropdowns on click anywhere
    document.addEventListener('click', this.toggleFilterElements)
  }

  disconnect() {
    document.removeEventListener('click', this.toggleFilterElements)
  }

  onInputChange() {
    document.getElementById('filterForm').requestSubmit()
  }

  toggleFilterElements(e) {
    const container = e.target.closest('div')
    if (e.target.classList.contains('js-toggle')) {
      container.classList.toggle('show')

      const elementsToHide = document.querySelectorAll('.show')
      elementsToHide.forEach((element) => {
        if (element !== container) {
          element.classList.remove('show')
        }
      })
    } else {
      const elementsToHide = document.querySelectorAll('.show')
      elementsToHide.forEach((element) => {
        element.classList.remove('show')
      })
    }
  }
}
