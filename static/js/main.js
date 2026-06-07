let selectedImages = [];

// ======================================================
// change 3.3.3
// REQUEST LOCK
// ======================================================
let isGenerating = false;

// ======================================
// ELEMENTS
// ======================================
const imageInput = document.getElementById("images");
const fileList = document.getElementById("fileList");
const generateBtn = document.querySelector(
    '#reportForm button[type=\"submit\"]'
);

// ======================================
// IMAGE PICKER
// ======================================
imageInput.onchange = function () {

    for (let i = 0; i < this.files.length; i++) {
        selectedImages.push(this.files[i]);
    }

    renderFileList();

    // reset input so same file can be chosen again later
    imageInput.value = "";
};

// ======================================
// RENDER FILE LIST
// ======================================
function renderFileList() {

    fileList.innerHTML = "";

    if (selectedImages.length === 0) {
        return;
    }

    selectedImages.forEach((file, index) => {

        const div = document.createElement("div");
        div.className = "file-item";

        div.innerHTML = `
            <span>${file.name}</span>
            <button type="button" class="remove-btn" onclick="removeImage(${index})">
                Remove
            </button>
        `;

        fileList.appendChild(div);
    });
}

// ======================================
// REMOVE IMAGE
// ======================================
function removeImage(index) {
    selectedImages.splice(index, 1);
    renderFileList();
}

// ======================================
// FORM SUBMIT
// ======================================
document.getElementById("reportForm").onsubmit = async function (e) {

    e.preventDefault();

    // ======================================================
    // change 3.3.3
    // BLOCK MULTIPLE CLICKS
    // ======================================================
    if (isGenerating) {
        return;
    }

    isGenerating = true;

    const status = document.getElementById("status");

    // ======================================================
    // change 3.3.3
    // START LOADING STATE
    // ======================================================
    generateBtn.disabled = true;
    generateBtn.classList.add("disabled-btn");
    generateBtn.innerText = "Generating PDF...";


    const formData = new FormData();

    const studentData = {
        exp_no: document.getElementById("exp_no").value,
        year: document.getElementById("year").value,
        sem: document.getElementById("sem").value,
        class: document.getElementById("class").value,
        subject: document.getElementById("subject").value,
        instructor: document.getElementById("instructor").value,
        p_date: document.getElementById("p_date").value
            ? document.getElementById("p_date").value.split("-").reverse().join("/")
            : "",
        s_date: document.getElementById("s_date").value
            ? document.getElementById("s_date").value.split("-").reverse().join("/")
            : "",
        name: document.getElementById("name").value,
        id: document.getElementById("id").value,
        roll: document.getElementById("roll").value,
        aim: document.getElementById("aim").value,
        outcomes: document.getElementById("outcomes").value,
        conclusion: document.getElementById("conclusion").value
    };

    formData.append("student_data", JSON.stringify(studentData));

    // PDF Upload
    const pdfFile = document.getElementById("pdf_file").files[0];

    if (!pdfFile) {

        status.innerText = "Please upload an APSIT template PDF.";

        resetGenerateButton();
        return;
    }

    // ======================================================
    // change 3.1 updated
    // FILE SIZE VALIDATION
    // ======================================================
    const MAX_PDF_SIZE = 20 * 1024 * 1024; // 20 MB
    const MAX_IMAGE_SIZE = 10 * 1024 * 1024; // 10 MB

    if (pdfFile.size > MAX_PDF_SIZE) {

        status.innerText = "📄 PDF size exceeds the 20 MB limit.";

        resetGenerateButton();
        return;
    }

    for (const image of selectedImages) {

        if (image.size > MAX_IMAGE_SIZE) {

            status.innerText = `🖼 "${image.name}" exceeds the 10 MB limit.`;

            resetGenerateButton();
            return;
        }
    }

    formData.append("pdf_file", pdfFile);

    // Add all selected images
    selectedImages.forEach(file => {
        formData.append("images", file);
    });

    try {

        const response = await fetch("/generate-report", {
            method: "POST",
            body: formData
        });

        if (response.ok) {

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            const a = document.createElement("a");
            a.href = url;
            a.download = "APSIT_Experiment.pdf";
            document.body.appendChild(a);
            a.click();
            a.remove();

            status.innerHTML = "✅ PDF generated successfully.<br><small>Your download has started.</small>";

        } else {

            const err = await response.json();
            status.innerText = err.detail || "Failed to generate PDF.";
        }

    } catch (error) {

        status.innerText = "⚠️ Something went wrong. Please try again."; 

    } finally {

        // ======================================================
        // change 3.3.3
        // ALWAYS RESTORE BUTTON
        // ======================================================
        resetGenerateButton();
    }
};

// ======================================================
// change 3.3.3
// RESET BUTTON FUNCTION
// ======================================================
function resetGenerateButton() {

    isGenerating = false;

    generateBtn.disabled = false;
    generateBtn.classList.remove("disabled-btn");
    generateBtn.innerText = "⏳ Generating PDF...";
}