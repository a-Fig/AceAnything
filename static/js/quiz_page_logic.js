// static/js/quiz_page_logic.js
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const elements = {
        quizCard: document.getElementById('quizCard'),
        scoreDisplay: document.getElementById('scoreDisplay'),
        loadingMessage: document.getElementById('loadingMessage'),
        quizArea: document.getElementById('quizArea'),
        questionText: document.getElementById('questionText'),
        answerOptionsMcq: document.getElementById('answerOptionsMcq'),
        answerOptionsTf: document.getElementById('answerOptionsTf'),
        shortAnswerContainer: document.getElementById('shortAnswerContainer'),
        shortAnswerInput: document.getElementById('shortAnswerInput'),
        submitAnswerBtn: document.getElementById('submitAnswerBtn'),
        postAnswerActions: document.getElementById('postAnswerActions'),
        nextQuestionBtn: document.getElementById('nextQuestionBtn'),
        reviewWithCoachBtn: document.getElementById('reviewWithCoachBtn'),
        tutorPanel: document.getElementById('aiTutorPanel'),
        chatMessages: document.getElementById('chatMessages'),
        chatInput: document.getElementById('chatInput'),
        sendChatBtn: document.getElementById('sendChatBtn'),
        closeTutorBtn: document.getElementById('closeTutorBtn')
    };

    console.log("DOM Elements initialized:", elements);

    if (!elements.nextQuestionBtn) {
        console.error("CRITICAL: nextQuestionBtn element NOT FOUND even after HTML changes! Check ID in quiz_interface.html.");
    }

    let currentQuestionType = null;
    let selectedAnswer = null;
    let activeAudio = null; // For managing single TTS audio instance
    let audioStates = {}; // To store play/pause state per message text
    let currentScoreData = { correct: 0, total: 0 }; // Store score locally

    // DOM Elements by ID for score display
    const questionProgressDisplay = document.getElementById('questionProgressDisplay');
    const scoreTextDisplay = document.getElementById('scoreTextDisplay');

    // UI Functions
    function showLoading() {
        elements.loadingMessage.classList.remove('hidden');
        elements.quizArea.classList.add('hidden');
        elements.postAnswerActions.classList.add('hidden');
        elements.submitAnswerBtn.classList.remove('hidden');
        elements.quizCard.classList.remove('correct', 'incorrect'); // Remove card highlight
    }

    function showQuizArea() {
        elements.loadingMessage.classList.add('hidden');
        elements.quizArea.classList.remove('hidden');
    }

    function updateScoreDisplay(score) {
        // score.total is the number of questions *answered*
        // score.correct is the number of questions *answered correctly*
        // totalQuizQuestions is the total questions in the quiz (from HTML)
        currentScoreData = score; // Update local score copy

        const questionsAnswered = score.total;
        const questionsCorrect = score.correct;
        
        if (questionProgressDisplay) {
            // If a question is currently loaded, current question number is answered + 1
            // If quiz just ended, current question number is total answered.
            const currentQuestionNumber = elements.quizArea.classList.contains('hidden') && questionsAnswered === totalQuizQuestions ? 
                                        questionsAnswered : // If quiz ended, show total answered
                                        questionsAnswered + 1; // If in progress, show next q number
            
            const displayQuestionNum = Math.min(currentQuestionNumber, totalQuizQuestions); // Cap at total questions

            questionProgressDisplay.textContent = `${displayQuestionNum} / ${totalQuizQuestions || '-'}`;
        }
        if (scoreTextDisplay) {
            scoreTextDisplay.textContent = `Score: ${questionsCorrect}`;
        }
    }

    function showTutorPanel() {
        if (elements.tutorPanel) {
            elements.tutorPanel.classList.add('active');
        } else {
            console.error("Tutor panel element not found.");
        }
    }

    function hideTutorPanel() {
        if (elements.tutorPanel) {
            elements.tutorPanel.classList.remove('active');
            if (activeAudio) { // Stop any playing audio when panel closes
                activeAudio.pause();
                activeAudio = null;
            }
        }
    }

    function clearAnswerOptions() {
        elements.answerOptionsMcq.innerHTML = '';
        elements.answerOptionsTf.innerHTML = '';
        elements.shortAnswerInput.value = '';
        selectedAnswer = null;
        document.querySelectorAll('.mcq-option.selected').forEach(btn => btn.classList.remove('selected'));
        document.querySelectorAll('.tf-option.selected').forEach(btn => btn.classList.remove('selected'));
    }

    // Visual feedback for correct/incorrect directly on quizCard
    function showCardFeedback(isCorrect) {
        elements.quizCard.classList.remove('correct', 'incorrect'); // Clear previous
        elements.quizCard.classList.add(isCorrect ? 'correct' : 'incorrect'); 
        // CSS in quiz_interface.html should define .correct and .incorrect for .quiz-card
        // e.g., .quiz-card.correct { border-left: 5px solid var(--accent-green); }
    }

    function addMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-bubble ${sender}`;
        
        const messageTextSpan = document.createElement('span');
        messageTextSpan.className = 'message-text';
        messageTextSpan.innerHTML = message.replace(/\n/g, '<br>');
        messageDiv.appendChild(messageTextSpan);

        if (sender === 'ai') {
            const speakButton = document.createElement('button');
            speakButton.className = 'tts-button-chat';
            speakButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5"><path d="M3 9v6h4l5 5V4L7 9H3zm7-.69v7.38L7.06 13H5V11h2.06L10 8.31zM16.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>';
            speakButton.setAttribute('aria-label', 'Speak this message');
            speakButton.onclick = () => {
                toggleSpeakMessage(message, speakButton);
            };
            messageDiv.appendChild(speakButton);
        }
        elements.chatMessages.appendChild(messageDiv);
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    }

    function clearChatMessages() { elements.chatMessages.innerHTML = ''; }

    async function handleChatSubmit() {
        const message = elements.chatInput.value.trim();
        if (!message) return;
        addMessage(message, 'user');
        elements.chatInput.value = '';

        const originalSendButtonContent = elements.sendChatBtn.innerHTML;
        elements.sendChatBtn.innerHTML = '<div class="spinner mx-auto" style="width:18px; height:18px; border-width:2px;"></div>';
        elements.sendChatBtn.disabled = true;

        try {
            const response = await fetch('/api/chat-with-tutor', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({ detail: "Error sending message to tutor."}));
                console.error("handleChatSubmit: Response not OK.", errData);
                addMessage(`⚠️ Error: ${errData.detail || response.statusText}`, 'ai');
                return;
            }
            const data = await response.json();

            if (data.ai_messages && data.ai_messages.length > 0) {
                data.ai_messages.forEach((msg, index) => {
                    addMessage(msg, 'ai');
                });
            } else {
                addMessage("I don't have a specific response for that right now.", 'ai');
            }
        } catch (error) {
            console.error("Error sending chat message:", error);
            addMessage("⚠️ Sorry, I couldn't connect to the AI coach.", 'ai');
        } finally {
            elements.sendChatBtn.innerHTML = originalSendButtonContent;
            elements.sendChatBtn.disabled = false;
        }
    }

    async function toggleSpeakMessage(textToSpeak, buttonElement) {
        const playIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5"><path d="M3 9v6h4l5 5V4L7 9H3zm7-.69v7.38L7.06 13H5V11h2.06L10 8.31zM16.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>';
        const pauseIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>';

        if (activeAudio && audioStates[textToSpeak] && audioStates[textToSpeak].isPlaying) {
            activeAudio.pause();
            audioStates[textToSpeak].isPlaying = false;
            buttonElement.innerHTML = playIcon;
        } else if (activeAudio && audioStates[textToSpeak] && !audioStates[textToSpeak].isPlaying) {
            activeAudio.play();
            audioStates[textToSpeak].isPlaying = true;
            buttonElement.innerHTML = pauseIcon;
        } else {
            if (activeAudio) activeAudio.pause(); // Stop any other playing audio
            // Reset states for other messages
            Object.keys(audioStates).forEach(key => audioStates[key].isPlaying = false);
            // Reset icons for other buttons
            document.querySelectorAll('.tts-button-chat').forEach(btn => btn.innerHTML = playIcon);

            buttonElement.innerHTML = '<div class="spinner" style="width:16px; height:16px; border-width:2px; margin: auto;"></div>';
            buttonElement.disabled = true;

            try {
                const response = await fetch('/api/tts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: textToSpeak })
                });
                if (!response.ok) {
                    const errData = await response.json().catch(() => ({ detail: "TTS error" }));
                    throw new Error(errData.detail || response.statusText);
                }
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                activeAudio = new Audio(audioUrl);
                audioStates[textToSpeak] = { audio: activeAudio, isPlaying: true };
                
                activeAudio.play();
                buttonElement.innerHTML = pauseIcon;

                activeAudio.onended = () => {
                    URL.revokeObjectURL(audioUrl);
                    audioStates[textToSpeak].isPlaying = false;
                    buttonElement.innerHTML = playIcon;
                    if (activeAudio === audioStates[textToSpeak].audio) activeAudio = null;
                };
                activeAudio.onerror = () => {
                    URL.revokeObjectURL(audioUrl);
                    audioStates[textToSpeak].isPlaying = false;
                    buttonElement.innerHTML = playIcon;
                    if (activeAudio === audioStates[textToSpeak].audio) activeAudio = null;
                    addMessage("Sorry, an error occurred playing this audio.", 'ai');
                    console.error("TTS playback error.");
                };
            } catch (error) {
                console.error('Error fetching or playing TTS audio:', error);
                addMessage(`Sorry, I couldn't play the audio: ${error.message}.`, 'ai');
                buttonElement.innerHTML = playIcon; 
            } finally {
                buttonElement.disabled = false;
            }
        }
    }

    async function displayQuestion() {
        showLoading();
        clearAnswerOptions();
        elements.submitAnswerBtn.disabled = false; // Re-enable submit button

        try {
            const response = await fetch('/api/question');
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: "Failed to parse error from server" }));
                elements.loadingMessage.textContent = `⚠️ Failed to load question: ${response.status} - ${errorData.error || response.statusText}. Please refresh or try returning to the main menu.`;
                return;
            }
            const data = await response.json();
            elements.questionText.textContent = data.text;
            currentQuestionType = data.type.toLowerCase();
            updateScoreDisplay(data.score); // Update score display with new data

            elements.answerOptionsMcq.classList.add('hidden');
            elements.answerOptionsTf.classList.add('hidden');
            elements.shortAnswerContainer.classList.add('hidden');

            if (currentQuestionType === 'mcq' && data.options) {
                elements.answerOptionsMcq.classList.remove('hidden');
                data.options.forEach((option, index) => {
                    const button = document.createElement('button');
                    button.classList.add('btn', 'mcq-option', 'w-full', 'text-left', 'mb-2');
                    button.textContent = `${String.fromCharCode(65 + index)}. ${option}`;
                    button.dataset.value = String.fromCharCode(65 + index);
                    button.addEventListener('click', () => {
                        selectedAnswer = button.dataset.value;
                        elements.answerOptionsMcq.querySelectorAll('.mcq-option').forEach(btn => btn.classList.remove('selected'));
                        button.classList.add('selected');
                    });
                    elements.answerOptionsMcq.appendChild(button);
                });
            } else if (currentQuestionType === 'tf' && data.options) {
                elements.answerOptionsTf.classList.remove('hidden');
                // Assuming T/F options are sent as an array e.g., ["True", "False"]
                // And backend expects 'A' for first option (True), 'B' for second (False)
                // This matches how questionclass.py's TrueFalseQuestion (subclass of MCQ) grades.
                const optionValues = ['A', 'B']; 
                data.options.forEach((optionText, index) => {
                    const button = document.createElement('button');
                    button.classList.add('btn', 'tf-option', 'w-full', 'sm:w-auto', 'flex-1', 'mb-2', 'sm:mb-0');
                    button.textContent = optionText;
                    button.dataset.value = optionValues[index]; // Send 'A' or 'B'
                    button.addEventListener('click', () => {
                        selectedAnswer = button.dataset.value;
                        elements.answerOptionsTf.querySelectorAll('.tf-option').forEach(btn => btn.classList.remove('selected'));
                        button.classList.add('selected');
                    });
                    elements.answerOptionsTf.appendChild(button);
                });
            } else if (currentQuestionType === 'short_answer') {
                elements.shortAnswerContainer.classList.remove('hidden');
                elements.shortAnswerInput.focus();
            } else {
                elements.questionText.textContent = "Error: Unknown question type or no options provided: " + currentQuestionType;
            }
            showQuizArea();
        } catch (error) {
            console.error("Error in displayQuestion function:", error);
            elements.loadingMessage.textContent = '⚠️ An error occurred loading the question. Please try refreshing.';
        }
        elements.submitAnswerBtn.disabled = false;
        elements.submitAnswerBtn.innerHTML = 'Submit Answer';
    }

    async function submitAnswer() {
        if (selectedAnswer === null && currentQuestionType !== 'short_answer') {
            alert('Please select an answer.');
            return;
        }

        let answerPayload;
        if (currentQuestionType === 'short_answer') {
            const shortAnswerText = elements.shortAnswerInput.value.trim();
            if (!shortAnswerText) {
                alert('Please enter your answer.');
                return;
            }
            answerPayload = { answer: shortAnswerText, type: 'short_answer' };
        } else {
            answerPayload = { answer: selectedAnswer, type: currentQuestionType };
        }

        // Disable submit button to prevent multiple submissions
        elements.submitAnswerBtn.disabled = true;

        try {
            const response = await fetch('/api/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(answerPayload)
            });
            const data = await response.json();
            updateScoreDisplay(data.score); // Update score display after submitting
            showCardFeedback(data.correct);

            elements.submitAnswerBtn.classList.add('hidden');
            elements.postAnswerActions.classList.remove('hidden');
            if (elements.nextQuestionBtn) elements.nextQuestionBtn.disabled = false;

            clearChatMessages();
            if (data.tutor_messages && data.tutor_messages.length > 0) {
                data.tutor_messages.forEach(msg => addMessage(msg, 'ai'));
            } else if (data.feedback) { // If no tutor messages, use the direct feedback
                addMessage(data.feedback, 'ai');
            }
            showTutorPanel();
        } catch (error) {
            console.error("Error in submitAnswer function:", error);
            showCardFeedback(false); // Visual feedback for error
            addMessage(`⚠️ Error submitting: ${error.message}`, 'ai'); // Show error in chat
            showTutorPanel(); // Show panel so user sees the error message
        } finally {
            elements.submitAnswerBtn.disabled = false; // Re-enable in case of non-HTTP error before fetch
            elements.submitAnswerBtn.innerHTML = 'Submit Answer'; // Restore text if not hidden
             if(elements.postAnswerActions.classList.contains('hidden')){
                elements.submitAnswerBtn.classList.remove('hidden');
            }
        }
    }

    if (elements.submitAnswerBtn) elements.submitAnswerBtn.addEventListener('click', submitAnswer);
    if (elements.nextQuestionBtn) {
        elements.nextQuestionBtn.addEventListener('click', () => {
            hideTutorPanel(); // Auto-close tutor panel
            displayQuestion();
            elements.submitAnswerBtn.classList.remove('hidden');
            elements.postAnswerActions.classList.add('hidden');
        });
    }
    if (elements.reviewWithCoachBtn) elements.reviewWithCoachBtn.addEventListener('click', showTutorPanel);
    if (elements.closeTutorBtn) elements.closeTutorBtn.addEventListener('click', hideTutorPanel);
    if (elements.sendChatBtn) elements.sendChatBtn.addEventListener('click', handleChatSubmit);
    if (elements.chatInput) elements.chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleChatSubmit(); });

    console.log("Initializing quiz page logic...");
    displayQuestion();
});

