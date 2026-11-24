// document.addEventListener("DOMContentLoaded", () => {
//     const MAX_FILES = 5;
//     const fileInput = document.getElementById("report-images");
//     const triggerButton = document.getElementById("pick-images-btn");
//     const previewGrid = document.getElementById("image-preview-grid");
//     const countLabel = document.getElementById("image-count-label");
//     const warningBanner = document.getElementById("image-limit-warning");

//     if (!fileInput || !triggerButton || !previewGrid || !countLabel) {
//         return;
//     }

//     let selectedFiles = [];
//     let objectUrls = [];

//     triggerButton.addEventListener("click", () => {
//         fileInput.click();
//     });

//     fileInput.addEventListener("change", () => {
//         const incoming = Array.from(fileInput.files || []).filter((file) =>
//             file.type.startsWith("image/")
//         );

//         if (!incoming.length) {
//             return;
//         }

//         const availableSlots = MAX_FILES - selectedFiles.length;
//         let hitLimit = false;

//         if (incoming.length > availableSlots) {
//             hitLimit = true;
//         }

//         const accepted = incoming.slice(0, Math.max(0, availableSlots));
//         selectedFiles = selectedFiles.concat(accepted);

//         syncInputFiles();
//         renderPreviews();

//         if (warningBanner) {
//             if (hitLimit) {
//                 warningBanner.textContent = `Maximum ${MAX_FILES} photos allowed. Extra photos were not added.`;
//                 warningBanner.hidden = false;
//             } else {
//                 warningBanner.textContent = "";
//                 warningBanner.hidden = true;
//             }
//         }
//     });

//     function syncInputFiles() {
//         const dataTransfer = new DataTransfer();
//         selectedFiles.forEach((file) => dataTransfer.items.add(file));
//         fileInput.files = dataTransfer.files;
//     }

//     function revokeUrls() {
//         objectUrls.forEach((url) => URL.revokeObjectURL(url));
//         objectUrls = [];
//     }

//     function renderPreviews() {
//         revokeUrls();
//         previewGrid.innerHTML = "";

//         countLabel.textContent = `${selectedFiles.length} / ${MAX_FILES} selected`;
//         triggerButton.disabled = selectedFiles.length >= MAX_FILES;

//         if (selectedFiles.length === 0) {
//             previewGrid.classList.add("hidden");
//             return;
//         }

//         previewGrid.classList.remove("hidden");

//         selectedFiles.forEach((file, index) => {
//             const url = URL.createObjectURL(file);
//             objectUrls.push(url);

//             const wrapper = document.createElement("div");
//             wrapper.className = "relative overflow-hidden rounded-xl border border-border bg-page aspect-square";

//             const img = document.createElement("img");
//             img.src = url;
//             img.alt = `Selected photo ${index + 1}`;
//             img.className = "h-full w-full object-cover";

//             const removeBtn = document.createElement("button");
//             removeBtn.type = "button";
//             removeBtn.setAttribute("aria-label", `Remove photo ${index + 1}`);
//             removeBtn.className =
//                 "absolute top-1.5 right-1.5 inline-flex h-7 w-7 items-center justify-center rounded-full bg-ink/80 text-white hover:bg-error transition-colors";
//             removeBtn.innerHTML =
//                 '<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>';

//             removeBtn.addEventListener("click", () => {
//                 selectedFiles.splice(index, 1);
//                 syncInputFiles();
//                 renderPreviews();
//                 if (warningBanner) {
//                     warningBanner.hidden = true;
//                 }
//             });

//             wrapper.appendChild(img);
//             wrapper.appendChild(removeBtn);
//             previewGrid.appendChild(wrapper);
//         });
//     }
// });


document.addEventListener("DOMContentLoaded", () => {
    const MAX_FILES = 5;
    const fileInput = document.getElementById("report-images");
    const dropArea = document.getElementById("drop-area");
    const previewGrid = document.getElementById("image-preview-grid");
    const countLabel = document.getElementById("image-count-label");
    const warningBanner = document.getElementById("image-limit-warning");

    if (!fileInput || !dropArea || !previewGrid || !countLabel) {
        return;
    }

    let selectedFiles = [];
    let objectUrls = [];

    function formatSize(bytes) {
        if (bytes < 1024 * 1024) {
            return `${Math.max(1, Math.round(bytes / 1024))} KB`;
        }
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }

    function addFiles(fileList) {
        const incoming = Array.from(fileList || []).filter((file) =>
            file.type.startsWith("image/")
        );

        if (!incoming.length) {
            return;
        }

        const availableSlots = MAX_FILES - selectedFiles.length;
        const hitLimit = incoming.length > availableSlots;
        const accepted = incoming.slice(0, Math.max(0, availableSlots));

        selectedFiles = selectedFiles.concat(accepted);
        syncInputFiles();
        renderPreviews();

        if (warningBanner) {
            if (hitLimit) {
                warningBanner.textContent = `Maximum ${MAX_FILES} photos allowed. Extra photos were not added.`;
                warningBanner.hidden = false;
            } else {
                warningBanner.textContent = "";
                warningBanner.hidden = true;
            }
        }
    }

    // Native file picker change
    fileInput.addEventListener("change", () => {
        addFiles(fileInput.files);
    });

    // Drag-and-drop support
    ["dragenter", "dragover"].forEach((eventName) => {
        dropArea.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropArea.classList.add("bg-surface-container", "ring-2", "ring-primary");
        });
    });

    ["dragleave", "drop"].forEach((eventName) => {
        dropArea.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropArea.classList.remove("bg-surface-container", "ring-2", "ring-primary");
        });
    });

    dropArea.addEventListener("drop", (event) => {
        if (event.dataTransfer && event.dataTransfer.files) {
            addFiles(event.dataTransfer.files);
        }
    });

    function syncInputFiles() {
        const dataTransfer = new DataTransfer();
        selectedFiles.forEach((file) => dataTransfer.items.add(file));
        fileInput.files = dataTransfer.files;
    }

    function revokeUrls() {
        objectUrls.forEach((url) => URL.revokeObjectURL(url));
        objectUrls = [];
    }

    function renderPreviews() {
        revokeUrls();
        previewGrid.innerHTML = "";

        countLabel.textContent = `Attached Files (${selectedFiles.length}/${MAX_FILES})`;

        if (selectedFiles.length === 0) {
            previewGrid.classList.add("hidden");
            return;
        }

        previewGrid.classList.remove("hidden");

        selectedFiles.forEach((file, index) => {
            const url = URL.createObjectURL(file);
            objectUrls.push(url);

            const card = document.createElement("div");
            card.className =
                "relative flex items-center gap-3 overflow-hidden rounded-xl bg-surface-container-low p-2.5 shadow-sm";

            const thumbBox = document.createElement("div");
            thumbBox.className = "h-16 w-16 shrink-0 overflow-hidden rounded-lg bg-surface-container-high shadow-inner";

            const img = document.createElement("img");
            img.src = url;
            img.alt = `Selected photo ${index + 1}`;
            img.className = "h-full w-full object-cover";
            thumbBox.appendChild(img);

            const meta = document.createElement("div");
            meta.className = "flex min-w-0 flex-1 flex-col";

            const nameEl = document.createElement("span");
            nameEl.className = "truncate text-xs font-bold text-on-surface";
            nameEl.textContent = file.name;

            const sizeEl = document.createElement("span");
            sizeEl.className = "text-[11px] text-on-surface-variant";
            sizeEl.textContent = formatSize(file.size);

            const readyEl = document.createElement("span");
            readyEl.className = "mt-0.5 inline-flex items-center gap-1 text-[11px] font-bold text-secondary";
            readyEl.innerHTML =
                '<svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg><span>Ready to attach</span>';

            meta.appendChild(nameEl);
            meta.appendChild(sizeEl);
            meta.appendChild(readyEl);

            const removeBtn = document.createElement("button");
            removeBtn.type = "button";
            removeBtn.setAttribute("aria-label", `Remove ${file.name}`);
            removeBtn.className =
                "inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-on-surface-variant transition-colors hover:bg-surface-container hover:text-error cursor-pointer";
            removeBtn.innerHTML =
                '<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>';

            removeBtn.addEventListener("click", () => {
                selectedFiles.splice(index, 1);
                syncInputFiles();
                renderPreviews();
                if (warningBanner) {
                    warningBanner.hidden = true;
                }
            });

            card.appendChild(thumbBox);
            card.appendChild(meta);
            card.appendChild(removeBtn);
            previewGrid.appendChild(card);
        });
    }
});