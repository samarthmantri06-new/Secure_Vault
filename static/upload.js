document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("fileInput");
    const display = document.getElementById("display");
    const editBtn = document.getElementById("edit");
    const saveBtn = document.getElementById("save");
    const submitBtn = document.getElementById("submit");
    const form = document.querySelector("form");

    let dataTransfer = new DataTransfer();
    let isEditing = false;

    window.getVaultFileCount = function () {
        return dataTransfer.files.length;
    };
    window.getVaultFileList = function () {
        return Array.from(dataTransfer.files);
    };

    function notifyFilesChanged() {
        document.dispatchEvent(new CustomEvent("vaultfileschanged", { detail: { count: dataTransfer.files.length } }));
    }

    function updateVaultUI() {
        const n = dataTransfer.files.length;
        if (form) {
            form.classList.toggle("files-present", n > 0);
            form.classList.toggle("vault-scanning", n > 0);
        }
        const shardBox = document.getElementById("shard-assembly");
        if (shardBox && document.body.classList.contains("page-decrypt")) {
            shardBox.classList.toggle("shard-assembly--armed", n > 0);
        }
        notifyFilesChanged();
    }

    function bindDropZone() {
        const wrap = document.querySelector(".drop-zone-wrap");
        if (!wrap) return;
        ["dragenter", "dragover"].forEach((ev) => {
            wrap.addEventListener(ev, (e) => {
                e.preventDefault();
                e.stopPropagation();
                wrap.classList.add("drop-zone-wrap--drag");
            });
        });
        wrap.addEventListener("dragleave", (e) => {
            e.preventDefault();
            wrap.classList.remove("drop-zone-wrap--drag");
        });
        wrap.addEventListener("drop", (e) => {
            e.preventDefault();
            e.stopPropagation();
            wrap.classList.remove("drop-zone-wrap--drag");
            const files = e.dataTransfer.files;
            for (let i = 0; i < files.length; i++) {
                dataTransfer.items.add(files[i]);
            }
            updateFileInput();
            renderFiles();
        });
    }

    bindDropZone();

    fileInput.addEventListener("change", (e) => {
        const files = e.target.files;
        for (let i = 0; i < files.length; i++) {
            dataTransfer.items.add(files[i]);
        }
        updateFileInput();
        renderFiles();
    });

    editBtn.addEventListener("click", () => {
        isEditing = true;
        renderFiles();
        editBtn.style.opacity = "0.5";
        saveBtn.style.opacity = "1";
    });

    saveBtn.addEventListener("click", () => {
        isEditing = false;
        renderFiles();
        saveBtn.style.opacity = "0.5";
        editBtn.style.opacity = "1";
    });

    function renderFiles() {
        display.innerHTML = "";

        Array.from(dataTransfer.files).forEach((file, index) => {
            const fileItem = document.createElement("div");
            fileItem.className = "file-item file-item--redact";
            if (isEditing) fileItem.classList.add("editable");

            let iconClass = "fa-file";
            if (file.name.endsWith(".pdf")) iconClass = "fa-file-pdf";
            else if (file.name.endsWith(".jpg") || file.name.endsWith(".png")) iconClass = "fa-file-image";
            else if (file.name.endsWith(".zip")) iconClass = "fa-file-zipper";
            else if (file.name.endsWith(".enc")) iconClass = "fa-lock";

            fileItem.innerHTML = `
                <i class="fa-solid ${iconClass}"></i>
                <p class="file-item-name">${file.name}</p>
                <div class="remove-btn" onclick="removeFile(${index})"><i class="fa-solid fa-xmark"></i></div>
            `;
            display.appendChild(fileItem);
            requestAnimationFrame(() => {
                setTimeout(() => fileItem.classList.add("file-item--unredact"), 80 + index * 70);
            });
        });
        updateVaultUI();
    }

    window.removeFile = function (index) {
        if (!isEditing) return;

        const newDataTransfer = new DataTransfer();
        const currentFiles = Array.from(dataTransfer.files);

        currentFiles.forEach((file, i) => {
            if (i !== index) newDataTransfer.items.add(file);
        });

        dataTransfer = newDataTransfer;
        updateFileInput();
        renderFiles();
    };

    function updateFileInput() {
        fileInput.files = dataTransfer.files;
    }
});
