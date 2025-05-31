// static/js/main_page_logic.js
document.addEventListener('DOMContentLoaded', () => {
    const quizSelectionGrid = document.getElementById('quizSelectionGrid');
    const uploadCardTrigger = document.getElementById('uploadCardTrigger');
    const pdfUploadInput = document.getElementById('pdfUpload'); // Hidden input triggered by card
    const uploadModal = document.getElementById('uploadModal');
    const closeUploadModalBtn = document.getElementById('closeUploadModalBtn');
    const uploadForm = document.getElementById('uploadForm');
    const pdfFileInputModal = document.getElementById('pdfFileInputModal'); // Input inside modal
    const quizTitleInput = document.getElementById('quizTitleInput');
    const submitUploadBtn = document.getElementById('submitUploadBtn');
    const uploadStatus = document.getElementById('uploadStatus');
    const globalLoadingOverlay = document.getElementById('globalLoadingOverlay');
    const loadingMessageDetail = document.getElementById('loadingMessageDetail');

    document.getElementById('currentYear').textContent = new Date().getFullYear();

    // Override quiz titles with updated ones
    const updatedQuizTitles = {
        'world_war_2': 'World War II: Major Events & Impacts',
        'nuclear_energy': 'Nuclear Science & Applications',
        'california_driving': 'DMV Test Prep: Road Rules & Signs',
        'ap_us_history': 'AP US History Challenge',
        'us_citizenship_test': 'US Citizenship Test Practice'
    };

    const updatedQuizDescriptions = {
        'world_war_2': 'Learn about the causes, key events, and aftermath of World War II.',
        'nuclear_energy': 'Explore nuclear energy sources, safety, waste management, and comparisons with other energy types.',
        'california_driving': 'Practice for your driver\'s license test with questions about road rules, traffic signs, and safe driving.',
        'ap_us_history': 'Test your knowledge of key events, figures, and concepts in American History from 1491 to the present.',
        'us_citizenship_test': 'Prepare for the U.S. Naturalization Test with questions on American government, history, and civics.'
    };

    // Update any quiz titles on the page
    document.querySelectorAll('.quiz-card-item').forEach(card => {
        const titleElement = card.querySelector('h2');
        const startButton = card.querySelector('.select-quiz-btn');

        if (startButton && titleElement) {
            const quizKey = startButton.dataset.quizName;
            if (quizKey && updatedQuizTitles[quizKey]) {
                titleElement.textContent = updatedQuizTitles[quizKey];

                // Also update descriptions
                const descElement = card.querySelector('p.text-sm');
                if (descElement && updatedQuizDescriptions[quizKey]) {
                    descElement.textContent = updatedQuizDescriptions[quizKey];
                }
            }
        }
    });

    function showGlobalLoader(message = "Processing...") {
        if (loadingMessageDetail) loadingMessageDetail.textContent = message;
        if (globalLoadingOverlay) globalLoadingOverlay.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // Prevent scrolling when loader is active
    }

    function hideGlobalLoader() {
        if (globalLoadingOverlay) globalLoadingOverlay.classList.add('hidden');
        document.body.style.overflow = '';
    }

    function displayGeneratingQuizCard(quizId, quizTitle) {
        if (!quizSelectionGrid) return;

        const card = document.createElement('div');
        card.className = 'quiz-card-item generating-quiz-card'; // Add a specific class for styling/identification
        card.id = `quiz-card-${quizId}`; // So we can potentially update it later if needed

        let descriptionText = "Your custom quiz is being generated. It will be ready soon!";
        // Attempt to get source material from the form if available, or use a generic message
        const file = pdfFileInputModal.files[0];
        if (file) {
            descriptionText = `Generating quiz from '${file.name}'. This may take a minute or two.`;
        }


        card.innerHTML = `
            <div>
                <h2 class="text-xl font-semibold mb-2">${quizTitle}</h2>
                <p class="text-sm text-text-secondary mb-4">${descriptionText}</p>
                <p class="text-xs text-accent-blue mb-3">Custom Quiz - Processing</p>
                <div class="flex items-center text-sm text-text-secondary">
                    <div class="spinner-small-dark mr-2" style="width: 16px; height: 16px; border: 2px solid var(--border-color); border-radius: 50%; border-top-color: var(--accent-blue);"></div>
                    <span>Generating... Please wait. You can navigate away or create another quiz.</span>
                </div>
            </div>
            <button class="btn btn-primary w-full select-quiz-btn mt-4" data-quiz-name="${quizId}" data-quiz-title="${quizTitle}" disabled style="opacity: 0.5; cursor: not-allowed;">
                Start Quiz (Generating)
            </button>
        `;
        // Add a spinner style for the card
        const style = document.createElement('style');
        style.textContent = `
            @keyframes spin-dark { to { transform: rotate(360deg); } }
            .spinner-small-dark { animation: spin-dark 0.7s linear infinite; }
        `;
        document.head.appendChild(style);


        // Add the new card to the top of the grid, or after the upload card trigger if it exists
        const uploadCard = document.getElementById('uploadCardTrigger');
        if (uploadCard && uploadCard.parentElement === quizSelectionGrid) {
            quizSelectionGrid.insertBefore(card, uploadCard.nextSibling);
        } else {
            quizSelectionGrid.prepend(card);
        }
    }


    // Event listeners for selecting default quizzes
    quizSelectionGrid.addEventListener('click', async (event) => {
        const button = event.target.closest('.select-quiz-btn');
        if (button) {
            const quizName = button.dataset.quizName;
            if (quizName) {
                const quizTitle = button.dataset.quizTitle || quizName.replace(/_/g, ' ');
                showGlobalLoader(`Starting ${quizTitle} quiz...`);
                try {
                    const response = await fetch(`/api/start-quiz/${quizName}`, { method: 'POST' });
                    const data = await response.json();
                    if (response.ok && data.status === 'success') {
                        // Redirect to the quiz interface page
                        window.location.href = `/quiz/${data.quiz_name}`;
                    } else {
                        uploadStatus.textContent = `Error: ${data.detail || 'Could not start quiz.'}`;
                        uploadStatus.className = 'status-error';
                        hideGlobalLoader();
                    }
                } catch (error) {
                    console.error('Failed to start quiz:', error);
                    uploadStatus.textContent = 'Error starting quiz. Please try again.';
                    uploadStatus.className = 'status-error';
                    hideGlobalLoader();
                }
            }
        }
    });

    // --- RENAME QUIZ LOGIC ---
    quizSelectionGrid.addEventListener('click', async (event) => {
        const target = event.target;
        const quizCard = target.closest('.quiz-card-item');
        if (!quizCard) return;

        // Elements specific to the clicked card
        const titleTextElement = quizCard.querySelector('.quiz-title-text');
        const customActionsDiv = quizCard.querySelector('.custom-quiz-actions'); // Container for edit/delete icons
        const renameControlsDiv = quizCard.querySelector('.rename-quiz-controls');
        const renameInput = renameControlsDiv ? renameControlsDiv.querySelector('.quiz-rename-input') : null;
        
        const editButton = target.closest('.edit-quiz-btn'); // The actual edit icon button clicked
        const saveButton = target.closest('.btn-save-rename');
        const cancelButton = target.closest('.btn-cancel-rename');

        // Function to switch to view mode (show title, hide input)
        function switchToViewMode(currentTitle) {
            if (titleTextElement) {
                titleTextElement.textContent = currentTitle;
                titleTextElement.classList.remove('hidden');
            }
            if (customActionsDiv) customActionsDiv.classList.remove('hidden'); // Show edit/delete icons
            if (renameControlsDiv) renameControlsDiv.classList.add('hidden'); // Hide input form
            
            // Update data attributes for consistency
            const currentEditBtn = quizCard.querySelector('.edit-quiz-btn');
            if (currentEditBtn) currentEditBtn.dataset.currentTitle = currentTitle;

            const startQuizButton = quizCard.querySelector('.select-quiz-btn');
            const deleteQuizIconButton = quizCard.querySelector('.delete-quiz-btn');
            if(startQuizButton) startQuizButton.dataset.quizTitle = currentTitle;
            if(deleteQuizIconButton) deleteQuizIconButton.dataset.quizTitle = currentTitle;
        }

        // Function to switch to edit mode (hide title, show input)
        function switchToEditMode() {
            const currentEditBtn = quizCard.querySelector('.edit-quiz-btn');
            const currentTitle = currentEditBtn ? currentEditBtn.dataset.currentTitle : (titleTextElement ? titleTextElement.textContent : '');

            if (titleTextElement) titleTextElement.classList.add('hidden');
            if (customActionsDiv) customActionsDiv.classList.add('hidden'); // Hide edit/delete icons
            if (renameControlsDiv) renameControlsDiv.classList.remove('hidden'); // Show input form
            
            if (renameInput) {
                renameInput.value = currentTitle;
                renameInput.focus();
                renameInput.select();
            }
        }

        if (editButton) { // Clicked on the edit icon
            event.preventDefault();
            switchToEditMode();
        }

        if (cancelButton) { // Clicked on Cancel button
            event.preventDefault();
            const currentEditBtn = quizCard.querySelector('.edit-quiz-btn');
            const originalTitle = currentEditBtn ? currentEditBtn.dataset.currentTitle : (titleTextElement ? titleTextElement.textContent : '');
            switchToViewMode(originalTitle);
        }

        if (saveButton) { // Clicked on Save button
            event.preventDefault();
            const quizNameAttributeSource = quizCard.querySelector('.edit-quiz-btn'); // Get quizName from a stable element
            const quizName = quizNameAttributeSource ? quizNameAttributeSource.dataset.quizName : null;

            if (!renameInput || !quizName) {
                console.error("Save rename: Missing renameInput or quizName from edit button dataset.");
                alert("An error occurred. Could not identify the quiz to rename.");
                return;
            }

            const newTitle = renameInput.value.trim();
            const originalTitle = quizNameAttributeSource.dataset.currentTitle || '';

            if (!newTitle) {
                alert("Quiz title cannot be empty.");
                renameInput.focus();
                return;
            }
            if (newTitle === originalTitle) {
                switchToViewMode(originalTitle); // No change, just switch back
                return;
            }

            showGlobalLoader(`Renaming quiz to: ${newTitle}...`);
            try {
                const response = await fetch(`/api/rename-quiz/${quizName}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({ new_title: newTitle })
                });
                const data = await response.json();

                if (response.ok && data.status === 'success') {
                    switchToViewMode(data.new_title); // Switch to view mode with the new title
                    if(uploadStatus) { 
                        uploadStatus.textContent = data.message || `Quiz renamed to "${data.new_title}".`;
                        uploadStatus.className = 'status-success';
                        setTimeout(() => { uploadStatus.textContent = ''; }, 3000);
                    }
                } else {
                    alert(`Error: ${data.detail || 'Could not rename quiz.'}`);
                    if(uploadStatus) {
                        uploadStatus.textContent = `Error: ${data.detail || 'Could not rename quiz.'}`;
                        uploadStatus.className = 'status-error';
                    }
                    // Do not switch view mode on error, keep input open for user to correct
                }
            } catch (error) {
                console.error('Error during quiz rename API call:', error);
                alert('An unexpected error occurred while renaming the quiz.');
                if(uploadStatus) {
                    uploadStatus.textContent = 'An unexpected error occurred while renaming the quiz.';
                    uploadStatus.className = 'status-error';
                }
                 // Do not switch view mode on error
            } finally {
                hideGlobalLoader();
            }
        }
    });
    // --- END RENAME QUIZ LOGIC ---

    // Event listener for deleting custom quizzes
    quizSelectionGrid.addEventListener('click', async (event) => {
        const deleteButton = event.target.closest('.delete-quiz-btn');
        if (!deleteButton) return;

        event.preventDefault(); // Prevent any default button action if it were a form submit, etc.

        const quizName = deleteButton.dataset.quizName;
        const quizTitle = deleteButton.dataset.quizTitle || "this quiz";

        if (!quizName) {
            console.error('Delete button clicked but quiz_name not found in dataset.');
            if(uploadStatus) {
                uploadStatus.textContent = 'Error: Could not identify quiz to delete.';
                uploadStatus.className = 'status-error';
            }
            return;
        }

        if (window.confirm(`Are you sure you want to delete the quiz "${quizTitle}"? This action cannot be undone.`)) {
            showGlobalLoader(`Deleting quiz: ${quizTitle}...`);
            try {
                const response = await fetch(`/api/delete-quiz/${quizName}`, { 
                    method: 'POST',
                    headers: {
                        'Accept': 'application/json'
                        // No 'Content-Type' needed for POST without body, but good practice if sending data
                    }
                });
                const data = await response.json();

                if (response.ok && data.status === 'success') {
                    const cardToDelete = deleteButton.closest('.quiz-card-item');
                    if (cardToDelete) {
                        cardToDelete.remove();
                    }
                    if(uploadStatus) { // Reuse uploadStatus for brief messages
                        uploadStatus.textContent = data.message || `Quiz "${quizTitle}" deleted.`;
                        uploadStatus.className = 'status-success';
                        setTimeout(() => { uploadStatus.textContent = ''; }, 3000); // Clear after 3s
                    }
                } else {
                    console.error('Failed to delete quiz:', data);
                    if(uploadStatus) {
                        uploadStatus.textContent = `Error: ${data.detail || 'Could not delete quiz.'}`;
                        uploadStatus.className = 'status-error';
                    }
                }
            } catch (error) {
                console.error('Error during quiz deletion API call:', error);
                if(uploadStatus) {
                    uploadStatus.textContent = 'An unexpected error occurred while deleting the quiz.';
                    uploadStatus.className = 'status-error';
                }
            }
            finally {
                hideGlobalLoader();
            }
        }
    });

    // Handle click on upload card to open modal
    if (uploadCardTrigger) {
        uploadCardTrigger.addEventListener('click', () => {
            if (uploadModal) uploadModal.classList.remove('hidden');
            if (pdfUploadInput) pdfUploadInput.value = ''; // Clear any previously selected file in hidden input
            if (pdfFileInputModal) pdfFileInputModal.value = ''; // Clear file in modal input
            if (quizTitleInput) quizTitleInput.value = '';
            if (uploadStatus) uploadStatus.textContent = '';
        });
    }

    // Close upload modal
    if (closeUploadModalBtn) {
        closeUploadModalBtn.addEventListener('click', () => {
            if (uploadModal) uploadModal.classList.add('hidden');
        });
    }
    // Close modal if backdrop is clicked
    if (uploadModal) {
        uploadModal.addEventListener('click', (event) => {
            if (event.target === uploadModal) {
                uploadModal.classList.add('hidden');
            }
        });
    }


    // Handle PDF upload form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const file = pdfFileInputModal.files[0];
            const title = quizTitleInput.value.trim();
            const sizePreference = document.getElementById('quizSizePrefInput').value;

            if (!file) {
                uploadStatus.textContent = 'Please select a PDF file.';
                uploadStatus.className = 'status-error';
                return;
            }

            const formData = new FormData();
            formData.append('file', file);
            if (title) {
                formData.append('quiz_title_form', title);
            }
            if (sizePreference) { // Add size preference if selected
                formData.append('quiz_size_preference', sizePreference);
            }

            submitUploadBtn.disabled = true;
            submitUploadBtn.innerHTML = `<div class="spinner-small"></div> Uploading & Processing...`;
            
            // Show loader ONLY for the initial synchronous part of upload & text extraction.
            // The backend will return quickly.
            showGlobalLoader(title ? `Preparing '${title}'...` : "Preparing your PDF...");
            uploadStatus.textContent = '';

            try {
                // Changed endpoint to /api/initiate-quiz-generation
                const response = await fetch('/api/initiate-quiz-generation', {
                    method: 'POST',
                    body: formData,
                });
                const data = await response.json();

                if (response.ok && data.status === 'generating') {
                    if (uploadModal) uploadModal.classList.add('hidden'); // Close modal
                    
                    // Display the placeholder card
                    displayGeneratingQuizCard(data.quiz_id, data.quiz_title);
                    
                    // Optionally, provide a success message on the main page (not in modal)
                    // For example, using a toast notification library or a simple alert
                    // alert(data.message); // Simple alert for now

                } else {
                    uploadStatus.textContent = `Error: ${data.detail || 'Could not start quiz generation.'}`;
                    uploadStatus.className = 'status-error';
                }
            } catch (error) {
                console.error('Quiz generation initiation error:', error);
                uploadStatus.textContent = 'An unexpected error occurred while starting quiz generation.';
                uploadStatus.className = 'status-error';
            } finally {
                submitUploadBtn.disabled = false;
                submitUploadBtn.innerHTML = 'Generate Quiz';
                // Hide global loader as the initial synchronous part is done.
                // The background task will proceed without blocking UI.
                hideGlobalLoader(); 
            }
        });
    }
});
