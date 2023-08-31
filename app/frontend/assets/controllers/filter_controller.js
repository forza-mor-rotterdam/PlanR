import { Controller } from '@hotwired/stimulus';
export default class extends Controller {

    static targets = ["filterOverview"]

    connect() {
        const inputList = document.getElementsByTagName("input")
        for (let i=0; i<inputList.length; i++){
            inputList[i].addEventListener('change', this.onInputChange)
        }

        //hide dropdowns on click anywhere
        document.addEventListener('click', this.toggleFilterElements)
    }

    disconnect(){
        console.log("disconnect")
        document.removeEventListener("click", this.toggleFilterElements)
    }

    onInputChange() {
        document.getElementById('filterForm').requestSubmit()
    }

    onShowNoAddress(e) {
        e.preventDefault()
        const elementsToShow = document.querySelectorAll(".js-has-no-address")
        const elementsToHide = document.querySelectorAll(".js-has-address")
        e.target.classList.toggle("show-no-address")
        elementsToShow.forEach((element) => {
            element.classList.toggle("show-no-address")
        })
        elementsToHide.forEach((element) => {
            element.classList.toggle("hide-address")
        })
    }

    toggleFilterElements(e) {
        const container = e.target.closest("div")
        if(e.target.classList.contains("js-toggle")){
            container.classList.toggle("show")

            const elementsToHide = document.querySelectorAll(".show")
            elementsToHide.forEach((element) => {
                if(element !== container){
                    element.classList.remove("show")
                }
            })
        } else {
            const elementsToHide = document.querySelectorAll(".show")
            elementsToHide.forEach((element) => {
                element.classList.remove("show")
            })
        }
    }

}
