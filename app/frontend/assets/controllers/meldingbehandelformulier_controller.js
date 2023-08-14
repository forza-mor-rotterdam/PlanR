import { Controller } from '@hotwired/stimulus';

let form = null
let inputList = null
let formData = null
const defaultErrorMessage = "Vul a.u.b. dit veld in."

export default class extends Controller {
    static values = {
        formIsSubmitted: Boolean,
        parentContext: String,
        standaardafhandelteksten: String,
    }
    static targets = ["externalText", "internalText"]

    connect() {
        if(this.hasExternalTextTarget) {
            if(this.externalTextTarget.textContent.length > 0) {
                this.externalMessage = this.externalTextTarget.textContent
            }
        }

        form = document.querySelector("#afhandelForm");
        inputList = document.querySelectorAll('.js-validation textarea')
        formData = new FormData(form)

        for (let i=0; i<inputList.length; i++){
            const input = inputList[i]
            const error = input.closest('.form-row').getElementsByClassName('invalid-text')[0]
            input.addEventListener("input", (event) => {
                if (input.validity.valid) {
                    input.closest('.form-row').classList.remove('is-invalid')
                    error.textContent = "";
                } else {
                    error.textContent = defaultErrorMessage;
                    input.closest('.form-row').classList.add('is-invalid')
                }
            })
        };

        form.addEventListener("submit", (event) => {
            const allFieldsValid = this.checkValids()

            if(!(allFieldsValid)){
                const errorList = document.querySelectorAll('div.is-invalid')
                errorList[0].scrollIntoView({ behavior: "smooth"})
                event.preventDefault();
            }
        });
    }

    checkValids() {
        //check all inputfields (except checkboxes) for validity
        // if 1 or more fields is invalid, don't send the form (return false)
        inputList = document.querySelectorAll('textarea')
        let count = 0
        for (let i=0; i<inputList.length; i++){
            const input = inputList[i]
            const error = input.closest('.form-row').getElementsByClassName('invalid-text')[0]
            if (input.validity.valid) {
                error.textContent = "";
                input.closest('.form-row').classList.remove('is-invalid')
            } else {
                error.textContent = defaultErrorMessage;
                input.closest('.form-row').classList.add('is-invalid')
                count++
            }
        }
        if (count > 0) {
            return false
        }else {
            return true
        }
    }

    cancelHandle() {
        this.element.dispatchEvent(new CustomEvent("cancelHandle", {
            detail: JSON.parse(this.parentContextValue),
            bubbles: true
        }));
    }

    setExternalMessage(evt){
        if(this.hasExternalTextTarget) {
            this.choice =  evt.params.index
            this.externalMessage = JSON.parse(this.standaardafhandeltekstenValue)[evt.target.value]
            this.externalTextTarget.value = this.externalMessage
        }
    }

    defaultExternalMessage(){
        if(this.externalMessage.length === 0) return

        this.externalTextTarget.value = this.externalMessage
    }

    clearExternalMessage() {
        this.externalTextTarget.value = ""
    }
}
