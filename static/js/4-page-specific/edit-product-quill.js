/* ================================================
   HENDOSHI - EDIT PRODUCT QUILL
   ================================================
   
   Purpose: JavaScript functionality for edit product quill
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

// Edit Product - Quill Editor Initialization and AI Generation for Meta/Story/Description
// Helper to read Django CSRF cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize Quill editor and expose global instance for shared usage
var quill = new Quill('#quill-editor', {
    theme: 'snow',
    modules: {
        toolbar: [
            ['bold', 'italic', 'underline'],
            [{ 'list': 'ordered'}, { 'list': 'bullet' }],
            ['link'],
            ['clean']
        ]
    },
    placeholder: 'Tell me the design story...'
});
window.__quill_editor = quill;

// Update character count and preview for Quill editor
function updateStoryCharCountAndPreview() {
    var text = quill.getText();
    var length = text.trim().length;
    var counter = document.getElementById('story-char-count');
    if (counter) {
        counter.textContent = length + ' / 500';
        if (length > 500) {
            counter.style.color = '#ff1493';
        } else {
            counter.style.color = 'var(--neon-pink)';
        }
    }
    var preview = document.getElementById('story-preview');
    if (preview) {
        preview.textContent = text.trim();
    }
}

// Sync Quill content with hidden textarea
quill.on('text-change', function() {
    var textarea = document.getElementById('id_story');
    if (textarea) {
        // Store plain text in textarea (since model has max 500 chars)
        textarea.value = quill.getText().trim();
    }
    updateStoryCharCountAndPreview();
});

// Update character count for SEO meta description
function updateMetaCharCount(textarea) {
    var count = textarea.value.length;
    var counter = document.getElementById('meta-char-count');
    if (counter) {
        counter.textContent = count + ' / 160';
        if (count > 160) {
            counter.style.color = '#ff1493';
        } else {
            counter.style.color = 'var(--neon-pink)';
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize meta description counter
    var metaField = document.getElementById('id_meta_description');
    if (metaField) {
        updateMetaCharCount(metaField);
        metaField.addEventListener('input', function() {
            updateMetaCharCount(this);
        });
    }

    // Load existing content into Quill
    var storyTextarea = document.getElementById('id_story');
    if (storyTextarea && storyTextarea.value) {
        quill.setText(storyTextarea.value);
    }

    // Initialize story counter and preview
    updateStoryCharCountAndPreview();

    // AI Meta Description Generator
    const generateBtn = document.getElementById('generateMetaBtn');
    const modal = document.getElementById('aiSuggestionsModal');
    const closeModalBtn = document.getElementById('closeModal');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const suggestionsContainer = document.getElementById('suggestionsContainer');
    const suggestionsList = document.getElementById('suggestionsList');
    const errorContainer = document.getElementById('errorContainer');
    const errorMessage = document.getElementById('errorMessage');

    const generateMetaUrl = generateBtn ? generateBtn.dataset.generateMetaUrl : '';

    generateBtn.addEventListener('click', async function() {
        const productName = document.getElementById('id_name').value.trim();
        const productDescription = document.getElementById('id_description').value.trim();

        if (!productDescription) {
            alert('Please enter a product description first!');
            return;
        }

        // Show modal with loading state
        modal.style.display = 'flex';
        loadingSpinner.style.display = 'block';
        suggestionsContainer.style.display = 'none';
        errorContainer.style.display = 'none';

        try {
            const response = await fetch(generateMetaUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    name: productName,
                    description: productDescription
                })
            });

            const data = await response.json();

            if (data.success && data.suggestions) {
                // Hide loading, show suggestions
                loadingSpinner.style.display = 'none';
                suggestionsContainer.style.display = 'block';

                // Clear previous suggestions
                suggestionsList.innerHTML = '';

                // Add each suggestion as a clickable card
                data.suggestions.forEach((suggestion, index) => {
                    const card = document.createElement('div');
                    card.className = 'suggestion-card';
                    card.innerHTML = `
                        <div class="suggestion-text">${suggestion}</div>
                        <div class="suggestion-length">${suggestion.length} characters</div>
                    `;
                    card.addEventListener('click', function() {
                        document.getElementById('id_meta_description').value = suggestion;
                        updateMetaCharCount(document.getElementById('id_meta_description'));
                        modal.style.display = 'none';
                    });
                    suggestionsList.appendChild(card);
                });
            } else {
                throw new Error(data.error || 'Failed to generate suggestions');
            }
        } catch (error) {
            loadingSpinner.style.display = 'none';
            errorContainer.style.display = 'block';
            errorMessage.textContent = error.message || 'An error occurred. Please try again.';
        }
    });

    // Close modal
    closeModalBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    // Close modal when clicking outside
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Design Story AI Generation
    const storyModal = document.getElementById('aiDesignStoryModal');
    const storyModalTitle = document.getElementById('storyModalTitle');
    const closeStoryModal = document.getElementById('closeStoryModal');
    const storyLoadingSpinner = document.getElementById('storyLoadingSpinner');
    const storySuggestionsContainer = document.getElementById('storySuggestionsContainer');
    const storySuggestionsList = document.getElementById('storySuggestionsList');
    const storyErrorContainer = document.getElementById('storyErrorContainer');
    const storyErrorMessage = document.getElementById('storyErrorMessage');

    const generateStoryTitleBtn = document.getElementById('generateStoryTitleBtn');
    const generateStoryContentBtn = document.getElementById('generateStoryContentBtn');
    const generateStoryUrl = generateStoryTitleBtn ? generateStoryTitleBtn.dataset.generateStoryUrl : '';

    async function generateDesignStory(type) {
        const productName = document.getElementById('id_name').value.trim();
        const productDescription = document.getElementById('id_description').value.trim();

        if (!productName || !productDescription) {
            alert('Please enter product name and description first!');
            return;
        }

        // Update modal title
        storyModalTitle.textContent = type === 'title' ? 'AI-Generated Story Titles' : 'AI-Generated Design Stories';

        // Show modal with loading state
        storyModal.style.display = 'flex';
        storyLoadingSpinner.style.display = 'block';
        storySuggestionsContainer.style.display = 'none';
        storyErrorContainer.style.display = 'none';

        try {
            const response = await fetch(generateStoryUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    name: productName,
                    description: productDescription,
                    type: type
                })
            });

            const data = await response.json();

            if (data.success) {
                storyLoadingSpinner.style.display = 'none';
                storySuggestionsContainer.style.display = 'block';
                storySuggestionsList.innerHTML = '';

                const suggestions = type === 'title' ? data.titles : data.stories;

                if (suggestions && suggestions.length > 0) {
                    suggestions.forEach((suggestion) => {
                        const card = document.createElement('div');
                        card.className = 'suggestion-card';
                        card.innerHTML = `
                            <div class="suggestion-text">${suggestion}</div>
                            <div class="suggestion-length">${suggestion.length} characters</div>
                        `;
                        card.addEventListener('click', function() {
                            if (type === 'title') {
                                document.getElementById('id_title').value = suggestion;
                            } else {
                                quill.setText(suggestion);
                                updateStoryCharCountAndPreview();
                            }
                            storyModal.style.display = 'none';
                        });
                        storySuggestionsList.appendChild(card);
                    });
                } else {
                    throw new Error('No suggestions generated');
                }
            } else {
                throw new Error(data.error || 'Failed to generate suggestions');
            }
        } catch (error) {
            storyLoadingSpinner.style.display = 'none';
            storyErrorContainer.style.display = 'block';
            storyErrorMessage.textContent = error.message || 'An error occurred. Please try again.';
        }
    }

    // Title generation button
    generateStoryTitleBtn.addEventListener('click', function() {
        generateDesignStory('title');
    });

    // Story content generation button
    generateStoryContentBtn.addEventListener('click', function() {
        generateDesignStory('story');
    });

    // Close story modal
    closeStoryModal.addEventListener('click', function() {
        storyModal.style.display = 'none';
    });

    // Close modal when clicking outside
    storyModal.addEventListener('click', function(e) {
        if (e.target === storyModal) {
            storyModal.style.display = 'none';
        }
    });

    // Product Description AI Generation
    const descInputModal = document.getElementById('aiDescriptionInputModal');
    const descModal = document.getElementById('aiDescriptionModal');
    const descriptionInput = document.getElementById('descriptionInput');
    const closeDescInputModal = document.getElementById('closeDescInputModal');
    const closeDescModal = document.getElementById('closeDescModal');
    const submitDescriptionInput = document.getElementById('submitDescriptionInput');
    const descLoadingSpinner = document.getElementById('descLoadingSpinner');
    const descSuggestionsContainer = document.getElementById('descSuggestionsContainer');
    const descSuggestionsList = document.getElementById('descSuggestionsList');
    const descErrorContainer = document.getElementById('descErrorContainer');
    const descErrorMessage = document.getElementById('descErrorMessage');

    const generateDescriptionBtn = document.getElementById('generateDescriptionBtn');
    const generateDescUrl = generateDescriptionBtn ? generateDescriptionBtn.dataset.generateDescUrl : '';

    // Open input modal when clicking Generate with AI
    generateDescriptionBtn.addEventListener('click', function() {
        const productName = document.getElementById('id_name').value.trim();
        if (!productName) {
            alert('Please enter a product name first!');
            return;
        }
        descInputModal.style.display = 'flex';
        descriptionInput.focus();
    });

    function sanitizeAIError(raw) {
        if (!raw) return 'AI service temporarily unavailable. Please try again later.';
        const low = String(raw).toLowerCase();
        if (low.includes('quota') || low.includes('429')) return 'AI quota exceeded. Please try again later.';
        if (low.length > 300) return 'AI service temporarily unavailable. Please try again later.';
        if (low.includes('http') || low.includes('https') || low.includes('{') || low.includes('}')) return 'AI service temporarily unavailable. Please try again later.';
        return String(raw);
    }

    let descRetryTimer = null;
    function startDescRetryCountdown(seconds) {
        const genBtn = document.getElementById('generateDescriptionBtn');
        if (genBtn) genBtn.disabled = true;

        if (descRetryTimer) { clearInterval(descRetryTimer); descRetryTimer = null; }
        const existing = document.getElementById('descRetryBtn');
        if (existing) existing.remove();

        let remaining = Math.max(0, Math.floor(seconds));
        const retryBtn = document.createElement('button');
        retryBtn.id = 'descRetryBtn';
        retryBtn.className = 'btn btn-pink mt-3';
        retryBtn.disabled = true;
        retryBtn.textContent = `Retry (${remaining}s)`;
        descErrorContainer.appendChild(retryBtn);

        descRetryTimer = setInterval(() => {
            remaining -= 1;
            if (remaining <= 0) {
                clearInterval(descRetryTimer);
                descRetryTimer = null;
                retryBtn.disabled = false;
                retryBtn.textContent = 'Retry now';
                if (genBtn) genBtn.disabled = false;
            } else {
                retryBtn.textContent = `Retry (${remaining}s)`;
            }
        }, 1000);

        retryBtn.addEventListener('click', function() {
            retryBtn.remove();
            descErrorContainer.style.display = 'none';
            submitDescriptionInput.click();
        });
    }

    // Submit description input and generate
    submitDescriptionInput.addEventListener('click', async function() {
        const productName = document.getElementById('id_name').value.trim();
        const userInput = descriptionInput.value.trim();

        if (!userInput) {
            alert('Please enter a description or keywords!');
            return;
        }

        // Close input modal, open suggestions modal with loading
        descInputModal.style.display = 'none';
        descModal.style.display = 'flex';
        descLoadingSpinner.style.display = 'block';
        descSuggestionsContainer.style.display = 'none';
        descErrorContainer.style.display = 'none';

        try {
            const genBtn = document.getElementById('generateDescriptionBtn');
            if (genBtn) genBtn.disabled = true;
            const response = await fetch(generateDescUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    name: productName,
                    input: userInput
                })
            });

            let data;
            try {
                data = await response.json();
            } catch (jsonErr) {
                if (!response.ok) {
                    if (response.status === 429) throw new Error('AI quota exceeded. Please try again later.');
                    throw new Error('AI service temporarily unavailable. Please try again later.');
                }
                throw new Error('Unexpected AI response. Please try again.');
            }

            if (response.ok && data.success && data.descriptions) {
                descLoadingSpinner.style.display = 'none';
                descSuggestionsContainer.style.display = 'block';
                descSuggestionsList.innerHTML = '';

                data.descriptions.forEach((description) => {
                    const card = document.createElement('div');
                    card.className = 'suggestion-card';
                    card.innerHTML = `
                        <div class="suggestion-text">${description}</div>
                        <div class="suggestion-length">${description.length} characters</div>
                    `;
                    card.addEventListener('click', function() {
                        document.getElementById('id_description').value = description;
                        descModal.style.display = 'none';
                        descriptionInput.value = ''; // Clear input for next time
                    });
                    descSuggestionsList.appendChild(card);
                });
            } else if (!response.ok) {
                if (data && data.retry_seconds) {
                    descLoadingSpinner.style.display = 'none';
                    descErrorContainer.style.display = 'block';
                    descErrorMessage.textContent = sanitizeAIError(data.error);
                    startDescRetryCountdown(data.retry_seconds);
                    return;
                }
                throw new Error(sanitizeAIError(data.error));
            } else {
                throw new Error(sanitizeAIError(data.error || 'Failed to generate descriptions'));
            }
        } catch (error) {
            descLoadingSpinner.style.display = 'none';
            descErrorContainer.style.display = 'block';
            descErrorMessage.textContent = error.message || 'An error occurred. Please try again.';
            const genBtn = document.getElementById('generateDescriptionBtn');
            if (genBtn && !descRetryTimer) genBtn.disabled = false;
        }
    });

    // Close description input modal
    closeDescInputModal.addEventListener('click', function() {
        descInputModal.style.display = 'none';
    });

    // Close description suggestions modal
    closeDescModal.addEventListener('click', function() {
        descModal.style.display = 'none';
    });

    // Close modals when clicking outside
    descInputModal.addEventListener('click', function(e) {
        if (e.target === descInputModal) {
            descInputModal.style.display = 'none';
        }
    });

    descModal.addEventListener('click', function(e) {
        if (e.target === descModal) {
            descModal.style.display = 'none';
        }
    });
});
