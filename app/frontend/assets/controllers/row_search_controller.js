import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['row', 'searchable', 'resultCount']
  static values = {
    disableResultHighlight: String,
  }

  connect() {
    this.searchableTargets.forEach((searchable) => {
      searchable.dataset.value = searchable.textContent
    })
    this.displayTypes = {
      LI: 'list-item',
      TR: 'table-row',
    }
    let formElem = this.element.querySelector('form')
    if (formElem) {
      formElem.addEventListener('submit', (e) => {
        e.preventDefault()
        return false
      })
    }
  }
  escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  }

  search(e) {
    if (e.target.value.trim().length != 0) {
      this.rowTargets.forEach((searchableContainer) => {
        searchableContainer.style.display = 'none'
      })

      if (this.hasResultCountTarget) {
        this.resultCountTarget.textContent = ''
      }

      this.searchableTargets.forEach((searchable) => {
        const value = this.escapeRegExp(e.target.value.trim())
        const re = new RegExp(value, 'gi')
        if (!this.hasDisableResultHighlightValue) {
          searchable.innerHTML = ''
        }
        if (re.test(searchable.dataset.value)) {
          if (!this.hasDisableResultHighlightValue) {
            const reg = new RegExp(value, 'gi')
            let execResult
            let index = 0
            let lastIndex
            let previousText = ''
            while ((execResult = reg.exec(searchable.dataset.value)) !== null) {
              lastIndex = reg.lastIndex
              if (execResult.index != 0) {
                previousText = searchable.dataset.value.substring(index, execResult.index)
              }
              searchable.appendChild(document.createTextNode(previousText))
              const markElem = document.createElement('MARK')
              markElem.textContent = execResult[0]
              searchable.appendChild(markElem)
              index = lastIndex
            }
            const endText = searchable.dataset.value.substring(
              lastIndex,
              searchable.dataset.value.length
            )
            searchable.appendChild(document.createTextNode(endText))
          }

          let container = searchable.closest("[data-row-search-target='row']")
          container.style.display = this.displayTypes[container.nodeName]
        } else if (!this.hasDisableResultHighlightValue) {
          searchable.textContent = searchable.dataset.value
        }
      })
      if (this.hasResultCountTarget) {
        const foundCount = this.rowTargets.filter(
          (searchableContainer) => searchableContainer.style.display != 'none'
        ).length
        this.resultCountTarget.textContent = `${foundCount} / ${this.rowTargets.length}`
      }
    } else {
      this.rowTargets.forEach((searchableContainer) => {
        searchableContainer.style.display = this.displayTypes[searchableContainer.nodeName]
      })
      this.searchableTargets.forEach((searchable) => {
        searchable.textContent = searchable.dataset.value
      })
      if (this.hasResultCountTarget) {
        this.resultCountTarget.textContent = `${this.rowTargets.length} / ${this.rowTargets.length}`
      }
    }
  }
}
