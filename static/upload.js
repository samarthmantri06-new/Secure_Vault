document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("fileInput");
    const display = document.getElementById("display");
    const editBtn = document.getElementById("edit");
    const saveBtn = document.getElementById("save");
    const submitBtn = document.getElementById("submit");

    // We use a DataTransfer object to manipulate the FileList 
    // because HTML input.files is read-only by default.
    let dataTransfer = new DataTransfer();
    let isEditing = false;

    // Listen for file selection
    fileInput.addEventListener("change", (e) => {
        const files = e.target.files;
        for (let i = 0; i < files.length; i++) {
            dataTransfer.items.add(files[i]);
        }
        updateFileInput();
        renderFiles();
    });

    // Edit button toggles the remove icons
    editBtn.addEventListener("click", () => {
        isEditing = true;
        renderFiles();
        editBtn.style.opacity = "0.5";
        saveBtn.style.opacity = "1";
    });

    // Save button hides the remove icons
    saveBtn.addEventListener("click", () => {
        isEditing = false;
        renderFiles();
        saveBtn.style.opacity = "0.5";
        editBtn.style.opacity = "1";
    });

    // Function to draw the files in the display box
    function renderFiles() {
        display.innerHTML = ""; // Clear current display
        
        Array.from(dataTransfer.files).forEach((file, index) => {
            const fileItem = document.createElement("div");
            fileItem.className = "file-item";
            if (isEditing) fileItem.classList.add("editable");

            // Assign icons based on file extension
            let iconClass = "fa-file";
            if (file.name.endsWith(".pdf")) iconClass = "fa-file-pdf";
            else if (file.name.endsWith(".jpg") || file.name.endsWith(".png")) iconClass = "fa-file-image";
            else if (file.name.endsWith(".zip")) iconClass = "fa-file-zipper";
            else if (file.name.endsWith(".enc")) iconClass = "fa-lock"; // Special icon for .enc files!

            fileItem.innerHTML = `
                <i class="fa-solid ${iconClass}"></i>
                <p>${file.name}</p>
                <div class="remove-btn" onclick="removeFile(${index})"><i class="fa-solid fa-xmark"></i></div>
            `;
            display.appendChild(fileItem);
        });
    }

    // Global function to remove a specific file from the queue
    window.removeFile = function(index) {
        if (!isEditing) return;
        
        const newDataTransfer = new DataTransfer();
        const currentFiles = Array.from(dataTransfer.files);
        
        // Add back all files EXCEPT the one clicked
        currentFiles.forEach((file, i) => {
            if (i !== index) newDataTransfer.items.add(file);
        });

        dataTransfer = newDataTransfer;
        updateFileInput();
        renderFiles();
    };

    // Sync our DataTransfer object back to the actual HTML input
    function updateFileInput() {
        fileInput.files = dataTransfer.files;
    }

    // Optional: Visual feedback when submitting
    document.querySelector('form').onsubmit = function() {
        if (dataTransfer.files.length === 0) {
            alert("Please select at least one file!");
            return false;
        }
        submitBtn.innerText = 'Processing...';
        submitBtn.style.opacity = '0.7';
        submitBtn.style.pointerEvents = 'none';
    };
});