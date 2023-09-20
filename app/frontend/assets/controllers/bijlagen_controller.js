import { Controller } from '@hotwired/stimulus';

let temp_files = {}
let temp_filesArr = []
let input = null
export default class extends Controller {

    static targets = ['bijlagenExtra', 'bijlagenAfronden', 'bijlagenNieuw']
    connect() {
        //clear the filelist
        temp_files = {}
        temp_filesArr = []
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


    showFileInput() {
        const inputContainer = document.getElementById('id_bijlagen').parentElement;
        inputContainer.classList.remove('hidden');
    }

    removeFile (e) {

        const index = e.params.index;
        if(this.hasBijlagenExtraTarget) {
            input = this.bijlagenExtraTarget
        }
        if(this.hasBijlagenAfrondenTarget) {
            input = this.bijlagenAfrondenTarget
        }
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
        if(this.hasBijlagenExtraTarget) {
            input = this.bijlagenExtraTarget
        }
        if(this.hasBijlagenAfrondenTarget) {
            input = this.bijlagenAfrondenTarget
        }
        if(this.hasBijlagenNieuwTarget) {
            input = this.bijlagenNieuwTarget
        }
        const preview = input.nextElementSibling
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
                remove.setAttribute('data-action', "bijlagen#removeFile")
                remove.setAttribute('data-bijlagen-index-param', index)
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
