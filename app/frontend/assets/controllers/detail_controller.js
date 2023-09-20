import { Controller } from '@hotwired/stimulus';

let lastFocussedItem = null
export default class extends Controller {

    static targets = ['selectedImage', 'thumbList', 'imageSliderContainer', 'turboActionModal']

    initialize() {
        if(this.hasThumbListTarget) {
            this.thumbListTarget.getElementsByTagName('li')[0].classList.add('selected')
        }

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
              this.closeModal()
            }
        })
    }

    openModal(event) {
        console.log("openModal, src: ", event.params.action)
        lastFocussedItem = event.target.closest('button')
        const modal = document.querySelector('.modal')
        const modalBackdrop = document.querySelector('.modal-backdrop')

        // NOT WORKING ?? this.turboActionModalTarget.setAttribute("src", event)

        const turboActionModal = document.querySelector('#melding_actie_form')
        turboActionModal.setAttribute("src", event.params.action)

        modal.classList.add('show')
        modalBackdrop.classList.add('show')
        document.body.classList.add('show-modal')
        setTimeout(function() {modal.querySelectorAll('.btn-close')[0].focus();}, 200)
    }

    closeModal() {
        const modal = document.querySelector('.modal');
        const modalBackdrop = document.querySelector('.modal-backdrop');
        modal.classList.remove('show');
        modalBackdrop.classList.remove('show');
        document.body.classList.remove('show-modal');
        if(lastFocussedItem) { lastFocussedItem.focus() }
    }

    onScrollSlider(e) {
        this.highlightThumb(Math.floor(this.imageSliderContainerTarget.scrollLeft / this.imageSliderContainerTarget.offsetWidth))
    }

    selectImage(e) {
        this.imageSliderContainerTarget.scrollTo({left: (Number(e.params.imageIndex) - 1) * this.imageSliderContainerTarget.offsetWidth, top: 0})
        this.deselectThumbs(e.target.closest('ul'));
        e.target.closest('li').classList.add('selected');
    }

    highlightThumb(index) {
        this.deselectThumbs(this.thumbListTarget)
        this.thumbListTarget.getElementsByTagName('li')[index].classList.add('selected')
    }

    deselectThumbs(list) {
        for (const item of list.querySelectorAll('li')) {
            item.classList.remove('selected');
        }
    }

    cancelInformatieToevoegen(e) {
        const form = e.target.closest("form")
        // form.find(input["type=file"]).value=null
        form.reset();
        e.target.closest('details').open = false;
    }

}
