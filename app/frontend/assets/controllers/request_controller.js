import { Controller } from '@hotwired/stimulus';

let specifiek_graf = 1
let form = null
let inputList = null
let checkboxList = null
let formData = null
const defaultErrorMessage = "Vul a.u.b. dit veld in."
let temp_files = {}
let temp_filesArr = []
export default class extends Controller {

    static targets = ["aannemerField", "specifiekGrafField", "emailField", "phoneField"]
    static values = {
        medewerkers: String,
        categorie_andere_oorzaak: String,
        specifiek_graf_categorieen: String,
        session_expiry_timestamp: String,
        session_expiry_max_timestamp: String,
    }

    connect() {
        this.aannemerFieldTarget.setAttribute("disabled", "disabled")
        this.emailFieldTarget.setAttribute("required", true)

        const labelEmail = document.querySelector("label[for='id_email_melder']");
        const labelEmailTextClean = labelEmail.innerHTML.split("<small>")[0]
        labelEmail.innerHTML = `${labelEmailTextClean}`

        form = document.querySelector("form");
        inputList = document.querySelectorAll('[type="text"], [type="radio"], select, textarea')
        checkboxList = document.querySelectorAll('[type="checkbox"]')

        formData = new FormData(form)

        //check radiobutton
        document.getElementById('id_specifiek_graf_0').click()

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

        for (let i=0; i<checkboxList.length; i++){
            const cb = checkboxList[i]

            cb.addEventListener("input", () => {
                this.checkCheckBoxes()
            })
        };

        form.addEventListener("submit", (event) => {

            const allFieldsValid = this.checkValids()
            const checkBoxesValid = this.checkCheckBoxes()

            if(!(checkBoxesValid && allFieldsValid)){
                const errorList = document.querySelectorAll('div.is-invalid')
                errorList[0].scrollIntoView({ behavior: "smooth"})
                event.preventDefault();
            }
            //clear the filelist
            temp_files = {}
            temp_filesArr = []
        });


    }

    openModal(event) {
        const modal = document.querySelector('.modal');
        const modalBackdrop = document.querySelector('.modal-backdrop');

        modal.classList.add('show');
        modalBackdrop.classList.add('show');
        document.body.classList.add('show-modal');
    }

    closeModal() {
        window.location.reload(true);
        const modal = document.querySelector('.modal');
        const modalBackdrop = document.querySelector('.modal-backdrop');
        modal.classList.remove('show');
        modalBackdrop.classList.remove('show');
        document.body.classList.remove('show-modal');
    }

    sessionTimer(){
    }

    checkValids() {
        //check all inputfields (except checkboxes) for validity
        // if 1 or more fields is invalid, don't send the form (return false)
        inputList = document.querySelectorAll('[type="text"], [type="radio"], select, textarea')
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
    checkCheckBoxes() {
        const cbRequired = document.getElementsByClassName('form-row cb-required')[0]
        if(cbRequired){
            const error = cbRequired.getElementsByClassName('invalid-text')[0]
            const form_data = new FormData(document.querySelector("form"));
            if(!form_data.has(cbRequired.querySelector("input").getAttribute("name"))){
                error.textContent = `Selecteer een ${cbRequired.querySelector("input").getAttribute("name")}`;
                cbRequired.classList.add('is-invalid')
                return false;
            }
            else{
                cbRequired.classList.remove('is-invalid')
                error.textContent = "";
                return true;
            }
        }

    }

    removeDuplicates(arr) {
        var unique = [];
        arr.forEach(element => {
            if (!unique.includes(element)) {
                unique.push(element);
            }
        })
        return unique
    }

    toggleInputNoEmail(e) {}
    onSpecifiekGrafChange(e){

    }

    hideCheckbox(cbToHide){
        cbToHide.checked = false
        cbToHide.setAttribute("disabled", "disabled")
        cbToHide.closest('li').style.display="none";
    }

    showCheckbox(cbToShow){
        cbToShow.removeAttribute("disabled")
        cbToShow.closest('li').style.display="block";
    }

    hideField(fieldId) {

        const field = document.getElementById(fieldId)
        field.closest('.form-row').classList.add('hidden')
        field.value = ''
        if(field.nodeName.toLowerCase() === 'input') {
            field.removeAttribute('required')
        } else {
            //find nested inputs
            const inputList = field.getElementsByTagName('input')
            for (let i=0; i<inputList.length; i++){
                inputList[i].removeAttribute('required')
            }

        }
    }

    showField(field) {
        document.getElementById(field).closest('.form-row').classList.remove('hidden')
        document.getElementById(field).setAttribute('required', true)
    }

    onBegraafplaatsChange(e) {

    }

    showFileInput() {
        const inputContainer = document.getElementById('id_fotos').parentElement;
        inputContainer.classList.remove('hidden');
    }

    removeFile (e) {

        const index = e.params.index;
        const input = document.getElementById('id_fotos')
        temp_filesArr = [...temp_files]
        temp_filesArr.splice(index, 1)

        /** Code from: https://stackoverflow.com/a/47172409/8145428 */
        const dT = new ClipboardEvent('').clipboardData || // Firefox < 62 workaround exploiting https://bugzilla.mozilla.org/show_bug.cgi?id=1422655
        new DataTransfer(); // specs compliant (as of March 2018 only Chrome)

        for (let file of temp_filesArr) {
            dT.items.add(file);
        }
        temp_files = dT.files;
        input.files = dT.files;

        this.updateImageDisplay(false);
    }

    addFiles(newFiles) {

        if (temp_filesArr.length === 0){
            temp_filesArr = [...newFiles]
        }else {
            temp_filesArr.push(...newFiles)
        }

        const dT = new ClipboardEvent('').clipboardData || // Firefox < 62 workaround exploiting https://bugzilla.mozilla.org/show_bug.cgi?id=1422655
        new DataTransfer(); // specs compliant (as of March 2018 only Chrome)

        for (let file of temp_filesArr) { dT.items.add(file); }
        temp_files = dT.files;
    }

    updateImageDisplay(adding = true) {
        const input = document.getElementById('id_bijlagen')
        const preview = document.getElementById('imagesPreview');
        const newFiles = input.files; //contains only new file(s)

        if(adding) {this.addFiles(newFiles)}


        const fileTypes = [
            "image/apng",
            "image/bmp",
            "image/heic",
            "image/gif",
            "image/jpeg",
            "image/pjpeg",
            "image/png",
            "image/svg+xml",
            "image/tiff",
            "image/webp",
            "image/x-icon"
        ];

        function validFileType(file) {
            return fileTypes.includes(file.type);
        }

        function returnFileSize(number) {
            if (number < 1024) {
              return `${number} bytes`;
            } else if (number >= 1024 && number < 1048576) {
              return `${(number / 1024).toFixed(1)} KB`;
            } else if (number >= 1048576) {
              return `${(number / 1048576).toFixed(1)} MB`;
            }
        }

        while(preview.firstChild) {
            preview.removeChild(preview.firstChild);
        }
        if (temp_files.length > 0) {
            const list = document.createElement('ul');
            list.classList.add('list-clean')
            preview.appendChild(list);

            for (const [index, file] of [...temp_files].entries()) {
                const listItem = document.createElement('li');
                const content = document.createElement('span');
                const remove = document.createElement('button');
                const span = document.createElement("span")
                span.classList.add('container__image')

                remove.setAttribute('type', "button")
                remove.setAttribute('data-action', "request#removeFile")
                remove.setAttribute('data-request-index-param', index)
                remove.classList.add('btn-close')

                if (validFileType(file)) {
                    content.innerHTML = `${file.name} <small>${returnFileSize(file.size)}</small>`;
                    if(file.type !== "image/heic"){
                        const image = document.createElement('img');
                        image.src = URL.createObjectURL(file);
                        image.onload = () => {
                            URL.revokeObjectURL(image.src);
                        };
                        span.appendChild(image);
                        listItem.appendChild(span)

                    } else {
                        const placeholder = document.createElement("div")
                        placeholder.classList.add("placeholder")
                        span.textContent = "Van dit bestandstype kan geen preview getoond worden."
                        placeholder.appendChild(span)
                        listItem.appendChild(placeholder)
                    }
                    listItem.appendChild(content);
                    listItem.appendChild(remove);
                } else {
                    content.textContent = `Het bestand "${file.name}" is geen geldig bestandstype. Selecteer alleen bestanden van het type "jpg, jpeg of png"`;
                    listItem.appendChild(content);
                }

                list.appendChild(listItem);
            }
        }
    }
}
