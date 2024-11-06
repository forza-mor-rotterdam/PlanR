import { Controller } from '@hotwired/stimulus'

const rowsPerPage = 20 // Let op, data gaat per 2 rows. Eén voor de getallen en één voor de gekleurde balk

export default class extends Controller {
  static targets = [
    'container',
    'tablebody',
    'tablehead',
    'pagination',
    'pageDisplay',
    'prevButton',
    'nextButton',
  ]

  connect() {
    let self = this
    self.element[self.identifier] = self
    self.table = this.tablebodyTarget
    self.rows = self.table.getElementsByTagName('tr')
    self.totalRows = self.rows.length
    self.currentPage = 1

    self.totalPages = Math.ceil(self.totalRows / rowsPerPage)

    this.showPage(self.currentPage)
    if (self.totalRows <= rowsPerPage) {
      this.hidePagination()
    }

    this.containerTarget.style.minHeight =
      self.table.parentElement.getBoundingClientRect().height + 'px'
  }

  showPage(page) {
    let self = this
    for (let i = 0; i < self.totalRows; i++) {
      self.rows[i].style.display = 'none'
    }

    const start = (page - 1) * rowsPerPage
    const end = Math.min(start + rowsPerPage, self.totalRows)

    for (let i = start; i < end; i++) {
      self.rows[i].style.display = 'table-row'
    }

    const startNum = start / 2 + 1
    const endNum =
      page * (rowsPerPage / 2) <= self.totalRows / 2 ? page * (rowsPerPage / 2) : self.totalRows / 2
    this.pageDisplayTarget.textContent =
      startNum < endNum
        ? `${
            this.tableheadTarget.getElementsByTagName('th')[1].textContent
          } ${startNum} t/m ${endNum} van ${self.totalRows / 2}`
        : `${this.tableheadTarget.getElementsByTagName('th')[1].textContent} ${endNum} van ${
            self.totalRows / 2
          }`

    this.prevButtonTarget.disabled = page === 1
    this.nextButtonTarget.disabled = page === self.totalPages
  }

  hidePagination() {
    this.paginationTarget.style.display = 'none'
  }

  showPreviousPage() {
    let self = this
    if (self.currentPage > 1) {
      self.currentPage--
      this.showPage(self.currentPage)
    }
  }

  showNextPage() {
    let self = this
    if (self.currentPage < self.totalPages) {
      self.currentPage++
      this.showPage(self.currentPage)
    }
  }
}
