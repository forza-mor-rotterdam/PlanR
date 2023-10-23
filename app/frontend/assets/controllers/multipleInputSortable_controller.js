import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['selectedItems', 'unSelectedItems']
  connect() {
    console.log('multiple input sortable')
    var dragging = null
    var self = this
    console.log(this)
    console.log(this.element)
    const draggableContainerElement = this.selectedItemsTarget
    draggableContainerElement.addEventListener('dragstart', function (event) {
      var target = self.getLI(event.target)
      dragging = target
    })

    draggableContainerElement.addEventListener('dragover', function (event) {
      event.preventDefault()
      var target = self.getLI(event.target)
      if (target) {
        var bounding = target.getBoundingClientRect()
        var offset = bounding.y + bounding.height / 2
        if (event.clientY - offset > 0) {
          target.style['border-bottom'] = 'solid 4px blue'
          target.style['border-top'] = ''
        } else {
          target.style['border-top'] = 'solid 4px blue'
          target.style['border-bottom'] = ''
        }
      }
    })
    draggableContainerElement.addEventListener('dragleave', function (event) {
      var target = self.getLI(event.target)
      if (target) {
        target.style['border-bottom'] = ''
        target.style['border-top'] = ''
      }
    })

    draggableContainerElement.addEventListener('drop', function (event) {
      event.preventDefault()
      var target = self.getLI(event.target)
      if (target) {
        if (target.style['border-bottom'] !== '') {
          target.style['border-bottom'] = ''
          draggableContainerElement.insertBefore(dragging, target.nextSibling)
        } else {
          target.style['border-top'] = ''
          draggableContainerElement.insertBefore(dragging, target)
        }
      }
    })
  }
  getLI(target) {
    while (target.nodeName.toLowerCase() != 'li' && target.nodeName.toLowerCase() != 'body') {
      target = target.parentNode
    }
    if (target.nodeName.toLowerCase() == 'body') {
      return false
    } else {
      return target
    }
  }
  getUL(target) {
    while (target.nodeName.toLowerCase() != 'ul' && target.nodeName.toLowerCase() != 'body') {
      target = target.parentNode
    }
    if (target.nodeName.toLowerCase() == 'body') {
      return false
    } else {
      return target
    }
  }
  checkboxClickEventHandler(event) {
    console.log(event.target)
    console.log(event)
    const liElem = this.getLI(event.target)
    const containerElem = this.getUL(event.target)
    const selected = liElem.querySelector('input').checked
    console.log(selected.checked)
    const selectedContainerElement = this.selectedItemsTarget
    const notSelectedContainerElement = this.unSelectedItemsTarget
    if (selected) {
      notSelectedContainerElement.appendChild(containerElem.removeChild(liElem))
    } else {
      selectedContainerElement.appendChild(containerElem.removeChild(liElem))
    }
  }
}
