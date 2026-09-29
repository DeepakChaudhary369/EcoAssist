/* =========================================================
   ECOASSIST
   AI Waste & Recycling Assistant
   Frontend JavaScript
========================================================= */


/* =========================================================
   CONFIGURATION
========================================================= */

const API_URL = "http://127.0.0.1:8000/chat";


/* =========================================================
   DOM ELEMENTS
========================================================= */

const promptInput = document.getElementById("prompt");

const submitButton = document.getElementById("submit");

const imageButton = document.getElementById("imageButton");

const imageInput = document.getElementById("imageInput");

const chatContainer = document.getElementById("chatContainer");

const imagePreviewContainer =
    document.getElementById("imagePreviewContainer");

const previewImage =
    document.getElementById("previewImage");

const removeImageButton =
    document.getElementById("removeImage");


/* =========================================================
   APPLICATION STATE
========================================================= */

let selectedImage = null;

let isProcessing = false;


/* =========================================================
   HELPER: ESCAPE HTML
========================================================= */

function escapeHTML(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}


/* =========================================================
   HELPER: FORMAT AI RESPONSE
========================================================= */

function formatAIResponse(text) {

    let safeText = escapeHTML(text);

    // Bold
    safeText = safeText.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

    // Convert Markdown headings
    safeText = safeText.replace(
        /^### (.*?)$/gm,
        "<h3>$1</h3>"
    );

    // Convert bullet points
    safeText = safeText.replace(
        /^\* (.*?)$/gm,
        "• $1"
    );

    // Convert numbered list line breaks
    safeText = safeText.replace(
        /\n/g,
        "<br>"
    );

    return safeText;
}


/* =========================================================
   SCROLL TO BOTTOM
========================================================= */

function scrollToBottom() {

    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: "smooth"
    });
}


/* =========================================================
   CREATE USER MESSAGE
========================================================= */

function createUserMessage(message, imageFile) {

    const chatBox =
        document.createElement("div");

    chatBox.className = "user-chat-box";


    const avatar =
        document.createElement("div");

    avatar.className = "avatar user-avatar";

    avatar.textContent = "👤";


    const wrapper =
        document.createElement("div");

    wrapper.className = "message-wrapper";


    const sender =
        document.createElement("div");

    sender.className = "sender-name";

    sender.textContent = "You";


    const messageArea =
        document.createElement("div");

    messageArea.className = "user-chat-area";


    if (message) {

        const text =
            document.createElement("div");

        text.textContent = message;

        messageArea.appendChild(text);
    }


    // Display uploaded image
    if (imageFile) {

        const image =
            document.createElement("img");

        image.className = "chat-image";

        image.alt = "Uploaded waste image";

        image.src =
            URL.createObjectURL(imageFile);

        messageArea.appendChild(image);
    }


    wrapper.appendChild(sender);

    wrapper.appendChild(messageArea);

    chatBox.appendChild(wrapper);

    chatBox.appendChild(avatar);

    chatContainer.appendChild(chatBox);

    scrollToBottom();
}


/* =========================================================
   CREATE AI MESSAGE
========================================================= */

function createAIMessage() {

    const chatBox =
        document.createElement("div");

    chatBox.className = "ai-chat-box";


    const avatar =
        document.createElement("div");

    avatar.className = "avatar ai-avatar";

    avatar.textContent = "🤖";


    const wrapper =
        document.createElement("div");

    wrapper.className = "message-wrapper";


    const sender =
        document.createElement("div");

    sender.className = "sender-name";

    sender.textContent = "EcoAssist";


    const messageArea =
        document.createElement("div");

    messageArea.className = "ai-chat-area";


    // Loading animation
    messageArea.innerHTML = `
        <div class="typing">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;


    wrapper.appendChild(sender);

    wrapper.appendChild(messageArea);

    chatBox.appendChild(avatar);

    chatBox.appendChild(wrapper);

    chatContainer.appendChild(chatBox);

    scrollToBottom();


    return messageArea;
}


/* =========================================================
   SHOW AI RESPONSE
========================================================= */

function showAIResponse(messageArea, response) {

    messageArea.innerHTML =
        formatAIResponse(response);

    scrollToBottom();
}


/* =========================================================
   SHOW ERROR
========================================================= */

function showError(messageArea, message) {

    messageArea.innerHTML = `
        <div class="error-message">
            ${escapeHTML(message)}
        </div>
    `;

    scrollToBottom();
}


/* =========================================================
   SEND MESSAGE TO BACKEND
========================================================= */

async function sendMessage() {

    if (isProcessing) {
        return;
    }


    const message =
        promptInput.value.trim();


    /*
       Don't allow completely empty requests.
    */

    if (!message && !selectedImage) {
        return;
    }


    isProcessing = true;

    submitButton.disabled = true;

    imageButton.disabled = true;


    /*
       Save selected image before clearing interface.
    */

    const imageToSend =
        selectedImage;


    /*
       Display user's message.
    */

    createUserMessage(
        message,
        imageToSend
    );


    /*
       Create AI loading message.
    */

    const aiMessageArea =
        createAIMessage();


    /*
       Clear input.
    */

    promptInput.value = "";

    promptInput.style.height = "auto";


    /*
       Create FormData.

       FastAPI receives:
       message
       image
    */

    const formData =
        new FormData();


    formData.append(
        "message",
        message
    );


    if (imageToSend) {

        formData.append(
            "image",
            imageToSend,
            imageToSend.name
        );
    }


    /*
       Clear selected image from preview.
    */

    clearSelectedImage();


    try {

        /*
           Send request to FastAPI.
        */

        console.log("Sending request to:", API_URL);

        console.log(
            "Image:",
            imageToSend
                ? `${imageToSend.name} (${imageToSend.type})`
                : "No image"
        );


        const response =
            await fetch(
                API_URL,
                {
                    method: "POST",
                    body: formData
                }
            );


        console.log(
            "Backend status:",
            response.status
        );


        /*
           Read response as text first.

           This makes debugging easier if the
           backend returns a non-JSON response.
        */

        const responseText =
            await response.text();


        console.log(
            "Backend response:",
            responseText
        );


        let data;

        try {

            data = JSON.parse(responseText);

        } catch (parseError) {

            throw new Error(
                `Invalid response from backend. HTTP ${response.status}`
            );
        }


        /*
           Handle HTTP errors.
        */

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to process your request."
            );
        }


        /*
           Display successful response.
        */

        if (
            data.success &&
            data.response
        ) {

            showAIResponse(
                aiMessageArea,
                data.response
            );

        } else {

            throw new Error(
                "The AI returned an unexpected response."
            );
        }


    } catch (error) {

        console.error(
            "EcoAssist error:",
            error
        );


        showError(
            aiMessageArea,
            error.message ||
            "Something went wrong. Please try again."
        );


    } finally {

        isProcessing = false;

        submitButton.disabled = false;

        imageButton.disabled = false;

        promptInput.focus();
    }
}


/* =========================================================
   IMAGE UPLOAD
========================================================= */

imageButton.addEventListener(
    "click",
    () => {

        imageInput.click();

    }
);


/* =========================================================
   IMAGE SELECTED
========================================================= */

imageInput.addEventListener(
    "change",
    (event) => {

        const file =
            event.target.files[0];


        if (!file) {
            return;
        }


        /*
           Validate file type.
        */

        const allowedTypes = [
            "image/jpeg",
            "image/png",
            "image/webp"
        ];


        if (!allowedTypes.includes(file.type)) {

            alert(
                "Please select a JPG, PNG, or WEBP image."
            );

            imageInput.value = "";

            return;
        }


        /*
           Maximum image size:
           5 MB
        */

        const maxSize =
            5 * 1024 * 1024;


        if (file.size > maxSize) {

            alert(
                "Image size must be smaller than 5 MB."
            );

            imageInput.value = "";

            return;
        }


        /*
           Store selected image.
        */

        selectedImage = file;


        /*
           Display preview.
        */

        previewImage.src =
            URL.createObjectURL(file);


        imagePreviewContainer.classList.add(
            "active"
        );
    }
);


/* =========================================================
   REMOVE SELECTED IMAGE
========================================================= */

removeImageButton.addEventListener(
    "click",
    () => {

        clearSelectedImage();

    }
);


/* =========================================================
   CLEAR IMAGE
========================================================= */

function clearSelectedImage() {

    selectedImage = null;

    imageInput.value = "";

    previewImage.src = "";

    imagePreviewContainer.classList.remove(
        "active"
    );
}


/* =========================================================
   SEND BUTTON
========================================================= */

submitButton.addEventListener(
    "click",
    () => {

        sendMessage();

    }
);


/* =========================================================
   ENTER KEY
========================================================= */

promptInput.addEventListener(
    "keydown",
    (event) => {

        /*
           Enter sends message.

           Shift + Enter creates a new line.
        */

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();
        }
    }
);


/* =========================================================
   AUTO-GROW TEXTAREA
========================================================= */

promptInput.addEventListener(
    "input",
    () => {

        promptInput.style.height =
            "auto";

        promptInput.style.height =
            Math.min(
                promptInput.scrollHeight,
                120
            ) + "px";
    }
);


/* =========================================================
   INITIALIZATION
========================================================= */

console.log(
    "EcoAssist frontend initialized."
);

console.log(
    "Backend:",
    API_URL
);