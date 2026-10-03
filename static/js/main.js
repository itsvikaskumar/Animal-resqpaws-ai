<<<<<<< HEAD
/* =========================================================
   ResQPaws AI - MAIN JAVASCRIPT
   Voice Assistant + AI Chat + Shared UI
   ========================================================= */

'use strict';

console.log('[ResQPaws] Main JavaScript loaded.');


/* =========================================================
   GLOBAL STATE
   ========================================================= */

let voiceEnabled = true;
let voiceSpeaking = false;
let chatSending = false;
let chatHistory = [];

const CHAT_STORAGE_KEY = 'resqpaws_chat_history';


/* =========================================================
   DOM READY
   ========================================================= */

document.addEventListener('DOMContentLoaded', function () {

    console.log('[ResQPaws] DOM loaded.');

    initializeVoiceAssistant();
    initializeAIChat();
    initializeCommonButtons();
    loadChatHistory();

    console.log('[ResQPaws] Main initialization completed.');
});


/* =========================================================
   HELPER - FIND ELEMENT
   ========================================================= */

function findElement(...ids) {

    for (const id of ids) {

        const element = document.getElementById(id);

        if (element) {
            return element;
        }
    }

    return null;
}


/* =========================================================
   VOICE ASSISTANT INITIALIZATION
   ========================================================= */

function initializeVoiceAssistant() {

    console.log('[ResQPaws Voice] Initializing...');

    if ('speechSynthesis' in window) {

        console.log(
            '[ResQPaws Voice] Browser speech synthesis available.'
        );

        window.speechSynthesis.onvoiceschanged = function () {

            const voices =
                window.speechSynthesis.getVoices();

            console.log(
                '[ResQPaws Voice] Available voices:',
                voices.length
            );
        };

    } else {

        console.warn(
            '[ResQPaws Voice] Speech synthesis is not supported.'
        );

        voiceEnabled = false;
    }

    updateVoiceUI();
}


/* =========================================================
   VOICE ASSISTANT TOGGLE
   ========================================================= */

function toggleVoiceAssistant() {

    console.log(
        '[ResQPaws Voice] toggleVoiceAssistant()'
    );

    const panel = findElement(
        'voiceAssistantPanel',
        'voicePanel',
        'voiceAssistant',
        'voice-assistant-panel'
    );

    if (panel) {

        panel.classList.toggle('d-none');

        if (!panel.classList.contains('d-none')) {

            announceVoice(
                'Voice assistant is ready. How can I help you?'
            );
        }

        return;
    }

    console.warn(
        '[ResQPaws Voice] Voice panel element not found.'
    );

    announceVoice(
        'Voice assistant is ready.'
    );
}


/* =========================================================
   VOICE ENABLE / DISABLE
   ========================================================= */

function toggleVoice() {

    voiceEnabled = !voiceEnabled;

    console.log(
        '[ResQPaws Voice] Voice enabled:',
        voiceEnabled
    );

    if (!voiceEnabled) {

        stopVoice();

    } else {

        announceVoice(
            'Voice assistant enabled.'
        );
    }

    updateVoiceUI();
}


/* =========================================================
   ALTERNATIVE VOICE TOGGLE
   ========================================================= */

function toggleVoiceAssistantSound() {

    toggleVoice();
}


/* =========================================================
   UPDATE VOICE UI
   ========================================================= */

function updateVoiceUI() {

    const buttons = [
        findElement('voiceToggleBtn'),
        findElement('voiceMuteBtn'),
        findElement('muteVoiceBtn'),
        findElement('voiceButton')
    ];

    buttons.forEach(function (button) {

        if (!button) {
            return;
        }

        if (voiceEnabled) {

            button.innerHTML =
                '<i class="fa-solid fa-volume-high"></i>';

            button.setAttribute(
                'title',
                'Mute Voice Assistant'
            );

        } else {

            button.innerHTML =
                '<i class="fa-solid fa-volume-xmark"></i>';

            button.setAttribute(
                'title',
                'Enable Voice Assistant'
            );
        }
    });
}


/* =========================================================
   MAIN VOICE ENGINE
   ========================================================= */

function announceVoice(message) {

    if (!message) {
        return;
    }

    if (!voiceEnabled) {

        console.log(
            '[ResQPaws Voice] Voice disabled.'
        );

        return;
    }

    if (!('speechSynthesis' in window)) {

        console.error(
            '[ResQPaws Voice] Speech synthesis not supported.'
        );

        return;
    }

    console.log(
        '[ResQPaws Voice] Speaking:',
        message
    );

    try {

        /*
         * Stop previous speech so messages
         * do not stack on top of each other.
         */

        window.speechSynthesis.cancel();

        const utterance =
            new SpeechSynthesisUtterance(
                String(message)
            );

        utterance.lang = 'en-US';
        utterance.rate = 0.95;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;


        /*
         * Select an English voice if available.
         */

        const voices =
            window.speechSynthesis.getVoices();

        const englishVoice =
            voices.find(function (voice) {

                return voice.lang &&
                    voice.lang
                        .toLowerCase()
                        .startsWith('en');
            });

        if (englishVoice) {

            utterance.voice =
                englishVoice;
        }


        /* Speech started */

        utterance.onstart = function () {

            voiceSpeaking = true;

            console.log(
                '[ResQPaws Voice] Speech started.'
            );
        };


        /* Speech finished */

        utterance.onend = function () {

            voiceSpeaking = false;

            console.log(
                '[ResQPaws Voice] Speech finished.'
            );
        };


        /* Speech error */

        utterance.onerror = function (event) {

            voiceSpeaking = false;

            /*
             * Chrome may report "interrupted"
             * when cancel() stops previous speech.
             *
             * This is not treated as a serious error.
             */

            if (
                event.error === 'interrupted'
            ) {

                console.log(
                    '[ResQPaws Voice] Previous speech was interrupted.'
                );

                return;
            }

            console.error(
                '[ResQPaws Voice] Speech error:',
                event.error
            );
        };


        /*
         * Small delay after cancel()
         * improves Chrome reliability.
         */

        setTimeout(function () {

            if (voiceEnabled) {

                window.speechSynthesis.speak(
                    utterance
                );
            }

        }, 50);

    } catch (error) {

        voiceSpeaking = false;

        console.error(
            '[ResQPaws Voice] Voice engine error:',
            error
        );
    }
}


/* =========================================================
   STOP VOICE
   ========================================================= */

function stopVoice() {

    if ('speechSynthesis' in window) {

        window.speechSynthesis.cancel();

        voiceSpeaking = false;

        console.log(
            '[ResQPaws Voice] Speech stopped.'
        );
    }
}


/* =========================================================
   TEST VOICE
   ========================================================= */

function testVoiceAssistant() {

    announceVoice(
        'Hello. This is the ResQPaws AI voice assistant. The voice system is working correctly.'
    );
}


/* =========================================================
   RESCUE EVENT VOICE ANNOUNCER
   ========================================================= */

function announceRescueEvent(
    eventName,
    data = {}
) {

    console.log(
        '[ResQPaws Voice] Rescue event:',
        eventName,
        data
    );

    let message = '';


    switch (eventName) {


        /* -----------------------------------------
           REPORT EVENTS
           ----------------------------------------- */

        case 'report_started':

            message =
                'Emergency animal rescue reporting has started.';

            break;


        case 'image_selected':

            message =
                'Animal image selected. Starting AI analysis.';

            break;


        case 'image_analysis_started':

            message =
                'AI is analyzing the animal image.';

            break;


        case 'image_analyzed':

            message =
                'AI image analysis has completed.';

            break;


        case 'animal_not_confirmed':

            message =
                'The image could not be confirmed as an animal.';

            break;


        /* -----------------------------------------
           LOCATION EVENTS
           ----------------------------------------- */

        case 'location_detected':

            message =
                'Your location has been detected.';

            break;


        case 'searching_rescue_center':

            message =
                'Searching for the nearest available rescue center.';

            break;


        case 'rescue_center_found':

            message =
                'A nearby rescue center has been found.';

            break;


        /* -----------------------------------------
           REPORT SUBMISSION
           ----------------------------------------- */

        case 'report_submitting':

            message =
                'Submitting your emergency rescue report.';

            break;


        case 'report_submitted':

            message =
                'Your rescue report has been submitted successfully.';

            break;


        /* -----------------------------------------
           AMBULANCE EVENTS
           ----------------------------------------- */

        case 'ambulance_assigned':

            message =
                'A rescue ambulance has been assigned to your case.';

            break;


        case 'ambulance_en_route':

            message =
                'The rescue ambulance is now on the way.';

            break;


        case 'ambulance_distance_update':

            if (
                data &&
                data.eta !== undefined &&
                data.eta !== null
            ) {

                message =
                    'The rescue ambulance is approximately ' +
                    data.eta +
                    ' minutes away.';
            }

            break;


        /* -----------------------------------------
           RESCUE TEAM
           ----------------------------------------- */

        case 'rescue_team_arrived':

            message =
                'The rescue team has arrived at the reported location.';

            break;


        case 'rescue_arrived':

            message =
                'The rescue team has arrived at the reported location.';

            break;


        /* -----------------------------------------
           HOSPITAL
           ----------------------------------------- */

        case 'hospital_transfer':

            message =
                'The animal is being transferred for treatment.';

            break;


        /* -----------------------------------------
           CASE COMPLETION
           ----------------------------------------- */

        case 'case_resolved':

            message =
                'The rescue case has been completed.';

            break;


        /* -----------------------------------------
           UNKNOWN EVENT
           ----------------------------------------- */

        default:

            console.log(
                '[ResQPaws Voice] Unknown rescue event:',
                eventName
            );

            return;
    }


    /*
     * Only speak when a valid message exists.
     */

    if (message) {

        announceVoice(message);
    }
}


/* =========================================================
   RESQPaws VOICE EVENT COMPATIBILITY FUNCTION
   ========================================================= */

function triggerResqpawsVoice(
    eventName,
    data = {}
) {

    console.log(
        '[ResQPaws] triggerResqpawsVoice():',
        eventName,
        data
    );

    announceRescueEvent(
        eventName,
        data
    );
}


/* =========================================================
   AI CHAT INITIALIZATION
   ========================================================= */

function initializeAIChat() {

    console.log(
        '[ResQPaws Chat] Initializing AI chat...'
    );

    const input = findElement(
        'chatInput',
        'aiChatInput',
        'chatMessage',
        'userMessage'
    );

    if (input) {

        input.addEventListener(
            'keydown',
            function (event) {

                if (
                    event.key === 'Enter' &&
                    !event.shiftKey
                ) {

                    event.preventDefault();

                    sendChatMessage();
                }
            }
        );
    }


    const sendButton = findElement(
        'sendChatBtn',
        'chatSendBtn',
        'btnSendChat',
        'sendMessageBtn'
    );

    if (sendButton) {

        sendButton.addEventListener(
            'click',
            function (event) {

                event.preventDefault();

                sendChatMessage();
            }
        );
    }


    const clearButton = findElement(
        'clearChatBtn',
        'chatClearBtn',
        'btnClearChat'
    );

    if (clearButton) {

        clearButton.addEventListener(
            'click',
            function (event) {

                event.preventDefault();

                clearChat();
            }
        );
    }


    console.log(
        '[ResQPaws Chat] AI chat initialized.'
    );
}


/* =========================================================
   TOGGLE AI CHAT
   ========================================================= */

function toggleAIChat() {

    console.log(
        '[ResQPaws Chat] toggleAIChat()'
    );

    const panel = findElement(
        'aiChatPanel',
        'chatPanel',
        'aiChat',
        'chatAssistantPanel',
        'ai-chat-panel'
    );

    if (!panel) {

        console.error(
            '[ResQPaws Chat] Chat panel not found.'
        );

        return;
    }

    panel.classList.toggle('d-none');


    if (!panel.classList.contains('d-none')) {

        const input = findElement(
            'chatInput',
            'aiChatInput',
            'chatMessage',
            'userMessage'
        );

        if (input) {

            setTimeout(
                function () {

                    input.focus();

                },
                100
            );
        }
    }
}


/* =========================================================
   ALTERNATIVE CHAT TOGGLE
   ========================================================= */

function toggleChat() {

    toggleAIChat();
}


/* =========================================================
   CHAT MESSAGE CONTAINER
   ========================================================= */

function getChatMessagesContainer() {

    return findElement(
        'chatMessages',
        'aiChatMessages',
        'chatHistory',
        'messagesContainer',
        'chatBody'
    );
}


/* =========================================================
   ADD CHAT MESSAGE
   ========================================================= */

function addChatMessage(
    message,
    sender = 'assistant'
) {

    const container =
        getChatMessagesContainer();

    if (!container) {

        console.warn(
            '[ResQPaws Chat] Messages container not found.'
        );

        return;
    }


    const wrapper =
        document.createElement('div');

    wrapper.className =
        sender === 'user'
            ? 'chat-message user-message'
            : 'chat-message assistant-message';


    const bubble =
        document.createElement('div');

    bubble.className =
        'chat-bubble';

    bubble.textContent =
        message;


    wrapper.appendChild(
        bubble
    );

    container.appendChild(
        wrapper
    );


    container.scrollTop =
        container.scrollHeight;
}


/* =========================================================
   CHAT LOADING
   ========================================================= */

function showChatLoading() {

    const container =
        getChatMessagesContainer();

    if (!container) {
        return;
    }

    removeChatLoading();


    const loading =
        document.createElement('div');

    loading.id =
        'resqpawsChatLoading';

    loading.className =
        'chat-message assistant-message';


    loading.innerHTML =
        '<div class="chat-bubble">' +
        '<span class="spinner-border spinner-border-sm me-2"></span>' +
        'Thinking...' +
        '</div>';


    container.appendChild(
        loading
    );

    container.scrollTop =
        container.scrollHeight;
}


/* =========================================================
   REMOVE CHAT LOADING
   ========================================================= */

function removeChatLoading() {

    const loading =
        document.getElementById(
            'resqpawsChatLoading'
        );

    if (loading) {

        loading.remove();
    }
}


/* =========================================================
   SEND CHAT MESSAGE
   ========================================================= */

async function sendChatMessage() {

    if (chatSending) {

        return;
    }


    const input =
        findElement(
            'chatInput',
            'aiChatInput',
            'chatMessage',
            'userMessage'
        );


    if (!input) {

        console.error(
            '[ResQPaws Chat] Chat input not found.'
        );

        return;
    }


    const message =
        input.value.trim();


    if (!message) {

        return;
    }


    chatSending = true;


    addChatMessage(
        message,
        'user'
    );


    input.value = '';


    showChatLoading();


    const sendButton =
        findElement(
            'sendChatBtn',
            'chatSendBtn',
            'btnSendChat',
            'sendMessageBtn'
        );


    if (sendButton) {

        sendButton.disabled = true;
    }


    try {

        console.log(
            '[ResQPaws Chat] Sending:',
            message
        );


        const response =
            await fetch(
                '/api/chat/',
                {
                    method: 'POST',

                    headers: {

                        'Content-Type':
                            'application/json',

                        'Accept':
                            'application/json',

                        'X-CSRFToken':
                            getCSRFToken()
                    },

                    credentials:
                        'same-origin',

                    body:
                        JSON.stringify({
                            message: message
                        })
                }
            );


        console.log(
            '[ResQPaws Chat] HTTP status:',
            response.status
        );


        const contentType =
            response.headers.get(
                'content-type'
            ) || '';


        let data;


        if (
            contentType.includes(
                'application/json'
            )
        ) {

            data =
                await response.json();

        } else {

            const text =
                await response.text();

            console.error(
                '[ResQPaws Chat] Non-JSON response:',
                text
            );

            throw new Error(
                `Server returned ${response.status}`
            );
        }


        removeChatLoading();


        if (!response.ok) {

            throw new Error(
                data.error ||
                `Chat request failed with ${response.status}`
            );
        }


        if (data.success === false) {

            throw new Error(
                data.error ||
                'AI chat request failed.'
            );
        }


        const reply =
            data.reply ||
            data.message ||
            data.response;


        if (!reply) {

            throw new Error(
                'The server returned no AI response.'
            );
        }


        console.log(
            '[ResQPaws Chat] AI reply:',
            reply
        );


        addChatMessage(
            reply,
            'assistant'
        );


        saveChatMessage(
            message,
            reply
        );


        announceVoice(
            reply
        );


    } catch (error) {

        removeChatLoading();


        console.error(
            '[ResQPaws Chat] Error:',
            error
        );


        addChatMessage(
            'Sorry, I could not connect to the AI assistant. Please try again.',
            'assistant'
        );


    } finally {

        chatSending = false;


        if (sendButton) {

            sendButton.disabled = false;
        }


        input.focus();
    }
}


/* =========================================================
   CSRF TOKEN
   ========================================================= */

function getCSRFToken() {

    const cookieName =
        'csrftoken';


    const cookies =
        document.cookie.split(';');


    for (
        let cookie of cookies
    ) {

        cookie =
            cookie.trim();


        if (
            cookie.startsWith(
                cookieName + '='
            )
        ) {

            return decodeURIComponent(
                cookie.substring(
                    cookieName.length + 1
                )
            );
        }
    }


    return '';
}


/* =========================================================
   SAVE CHAT HISTORY
   ========================================================= */

function saveChatMessage(
    userMessage,
    assistantMessage
) {

    chatHistory.push({

        user:
            userMessage,

        assistant:
            assistantMessage,

        timestamp:
            new Date().toISOString()
    });


    try {

        localStorage.setItem(
            CHAT_STORAGE_KEY,
            JSON.stringify(chatHistory)
        );

    } catch (error) {

        console.warn(
            '[ResQPaws Chat] Could not save chat history:',
            error
        );
    }
}


/* =========================================================
   LOAD CHAT HISTORY
   ========================================================= */

function loadChatHistory() {

    try {

        const stored =
            localStorage.getItem(
                CHAT_STORAGE_KEY
            );


        if (!stored) {

            return;
        }


        chatHistory =
            JSON.parse(stored);


        if (!Array.isArray(chatHistory)) {

            chatHistory = [];

            return;
        }


        console.log(
            '[ResQPaws Chat] Saved messages:',
            chatHistory.length
        );


    } catch (error) {

        console.warn(
            '[ResQPaws Chat] Failed to load history:',
            error
        );


        chatHistory = [];
    }
}


/* =========================================================
   CLEAR CHAT
   ========================================================= */

async function clearChat() {

    console.log(
        '[ResQPaws Chat] Clearing chat...'
    );


    try {

        const response =
            await fetch(
                '/api/chat/clear/',
                {
                    method: 'POST',

                    headers: {

                        'X-CSRFToken':
                            getCSRFToken(),

                        'Accept':
                            'application/json'
                    },

                    credentials:
                        'same-origin'
                }
            );


        console.log(
            '[ResQPaws Chat] Clear status:',
            response.status
        );


    } catch (error) {

        console.warn(
            '[ResQPaws Chat] Server clear failed:',
            error
        );
    }


    chatHistory = [];


    try {

        localStorage.removeItem(
            CHAT_STORAGE_KEY
        );

    } catch (error) {

        console.warn(
            '[ResQPaws Chat] Local history clear failed:',
            error
        );
    }


    const container =
        getChatMessagesContainer();


    if (container) {

        container.innerHTML = '';


        addChatMessage(
            'Hello! I am the ResQPaws AI assistant. How can I help you?',
            'assistant'
        );
    }
}


/* =========================================================
   COMMON BUTTON INITIALIZATION
   ========================================================= */

function initializeCommonButtons() {


    /* -----------------------------------------
       Voice mute button
       ----------------------------------------- */

    const voiceButton =
        findElement(
            'voiceToggleBtn',
            'voiceMuteBtn',
            'muteVoiceBtn'
        );


    if (
        voiceButton &&
        !voiceButton.hasAttribute(
            'data-resqpaws-bound'
        )
    ) {

        voiceButton.setAttribute(
            'data-resqpaws-bound',
            'true'
        );


        voiceButton.addEventListener(
            'click',
            function (event) {

                event.preventDefault();

                toggleVoice();
            }
        );
    }


    /* -----------------------------------------
       Chat send button
       ----------------------------------------- */

    const sendButton =
        findElement(
            'sendChatBtn',
            'chatSendBtn',
            'btnSendChat',
            'sendMessageBtn'
        );


    if (
        sendButton &&
        !sendButton.hasAttribute(
            'data-resqpaws-bound'
        )
    ) {

        sendButton.setAttribute(
            'data-resqpaws-bound',
            'true'
        );


        sendButton.addEventListener(
            'click',
            function (event) {

                event.preventDefault();

                sendChatMessage();
            }
        );
    }


    /* -----------------------------------------
       Clear chat button
       ----------------------------------------- */

    const clearButton =
        findElement(
            'clearChatBtn',
            'chatClearBtn',
            'btnClearChat'
        );


    if (
        clearButton &&
        !clearButton.hasAttribute(
            'data-resqpaws-bound'
        )
    ) {

        clearButton.setAttribute(
            'data-resqpaws-bound',
            'true'
        );


        clearButton.addEventListener(
            'click',
            function (event) {

                event.preventDefault();

                clearChat();
            }
        );
    }
}


/* =========================================================
   GLOBAL WINDOW EXPORTS
   ========================================================= */

window.toggleVoiceAssistant =
    toggleVoiceAssistant;

window.toggleVoice =
    toggleVoice;

window.toggleVoiceAssistantSound =
    toggleVoiceAssistantSound;

window.testVoiceAssistant =
    testVoiceAssistant;

window.announceVoice =
    announceVoice;

window.stopVoice =
    stopVoice;

window.announceRescueEvent =
    announceRescueEvent;

window.triggerResqpawsVoice =
    triggerResqpawsVoice;

window.toggleAIChat =
    toggleAIChat;

window.toggleChat =
    toggleChat;

window.sendChatMessage =
    sendChatMessage;

window.clearChat =
    clearChat;


/* =========================================================
   DEBUG
   ========================================================= */

window.resqpawsDebug = function () {

    console.log(
        '======================================'
    );

    console.log(
        '[ResQPaws Debug]'
    );

    console.log(
        'toggleVoiceAssistant:',
        typeof toggleVoiceAssistant
    );

    console.log(
        'toggleAIChat:',
        typeof toggleAIChat
    );

    console.log(
        'announceVoice:',
        typeof announceVoice
    );

    console.log(
        'announceRescueEvent:',
        typeof announceRescueEvent
    );

    console.log(
        'triggerResqpawsVoice:',
        typeof triggerResqpawsVoice
    );

    console.log(
        'sendChatMessage:',
        typeof sendChatMessage
    );

    console.log(
        'Speech synthesis:',
        'speechSynthesis' in window
    );

    console.log(
        'Voice enabled:',
        voiceEnabled
    );

    console.log(
        'Chat sending:',
        chatSending
    );

    console.log(
        '======================================'
    );
};


/* =========================================================
   END
   ========================================================= */

console.log(
    '[ResQPaws] main.js functions registered successfully.'
);

console.log(
    '[ResQPaws] Run resqpawsDebug() in browser console to test.'
);
=======
/**
 * ResQPaws AI - Main Interactive JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss bootstrap alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 6000);
    });

    // Image Upload Preview handler
    const imageInput = document.getElementById('id_image');
    const imagePreview = document.getElementById('image-preview');
    const previewContainer = document.getElementById('image-preview-container');

    if (imageInput && imagePreview && previewContainer) {
        imageInput.addEventListener('change', function(e) {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    imagePreview.src = event.target.result;
                    previewContainer.classList.remove('d-none');
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Camera capture module via HTML5 WebRTC
    const startCamBtn = document.getElementById('btn-start-camera');
    const snapBtn = document.getElementById('btn-snap-photo');
    const camVideo = document.getElementById('camera-stream');
    const camModal = document.getElementById('cameraModal');
    let streamObj = null;

    if (startCamBtn && camVideo) {
        startCamBtn.addEventListener('click', async () => {
            try {
                streamObj = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
                camVideo.srcObject = streamObj;
                camVideo.play();
            } catch (err) {
                alert('Camera access could not be established. Please upload a saved image instead: ' + err.message);
            }
        });

        if (snapBtn) {
            snapBtn.addEventListener('click', () => {
                const canvas = document.createElement('canvas');
                canvas.width = camVideo.videoWidth || 640;
                canvas.height = camVideo.videoHeight || 480;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(camVideo, 0, 0, canvas.width, canvas.height);

                canvas.toBlob((blob) => {
                    const file = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    if (imageInput) {
                        imageInput.files = dataTransfer.files;
                        imagePreview.src = canvas.toDataURL('image/jpeg');
                        previewContainer.classList.remove('d-none');
                    }
                    // Stop tracks
                    if (streamObj) {
                        streamObj.getTracks().forEach(track => track.stop());
                    }
                    const modalInstance = bootstrap.Modal.getInstance(camModal);
                    if (modalInstance) modalInstance.hide();
                }, 'image/jpeg', 0.9);
            });
        }

        if (camModal) {
            camModal.addEventListener('hidden.bs.modal', () => {
                if (streamObj) {
                    streamObj.getTracks().forEach(track => track.stop());
                }
            });
        }
    }
});
>>>>>>> d21fd6e5790317efbed53e24688055aae0303c50
