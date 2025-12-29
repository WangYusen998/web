document.addEventListener('DOMContentLoaded', () => {
    console.log('Movie Review App Loaded');

    // ==========================================
    // 1. Mobile Navigation
    // ==========================================
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', () => {
            const isExpanded = menuToggle.getAttribute('aria-expanded') === 'true';
            menuToggle.setAttribute('aria-expanded', !isExpanded);
            navLinks.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });
    }

    // Auto-hide flash messages
    const flashMessages = document.querySelectorAll('.flash-messages li');
    if (flashMessages.length > 0) {
        setTimeout(() => {
            flashMessages.forEach(msg => {
                msg.style.opacity = '0';
                setTimeout(() => msg.remove(), 500);
            });
        }, 5000);
    }

    // ==========================================
    // 2. Favorites Functionality (AJAX)
    // ==========================================
    const favoriteBtns = document.querySelectorAll('.favorite-btn');

    favoriteBtns.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();

            // Prevent double submission
            if (btn.disabled || btn.classList.contains('loading')) return;

            const movieId = btn.dataset.movieId;
            if (!movieId) {
                console.error('No movie ID found');
                return;
            }

            // Save original state
            const originalText = btn.innerHTML;
            
            // Set loading state
            btn.classList.add('loading');
            btn.disabled = true;
            btn.innerHTML = '<span class="loading-spinner">⏳</span> Processing...';

            try {
                const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
                const response = await fetch(`/api/favorite/${movieId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken
                    }
                });

                if (response.status === 401) {
                    // Redirect to login if unauthorized
                    window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
                    return;
                }

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();

                if (data.success) {
                    // Update Button State
                    if (data.favorited) {
                        btn.classList.add('favorited');
                        btn.setAttribute('aria-pressed', 'true');
                        // Update text with count
                        btn.innerHTML = `❤️ Favorited (${data.favorite_count})`;
                    } else {
                        btn.classList.remove('favorited');
                        btn.setAttribute('aria-pressed', 'false');
                        // Update text with count
                        btn.innerHTML = `🤍 Add to Favorites (${data.favorite_count})`;
                    }
                } else {
                    console.error('Favorite toggle failed');
                    btn.innerHTML = originalText;
                    alert('Failed to update favorite status.');
                }

            } catch (error) {
                console.error('Error:', error);
                btn.innerHTML = originalText;
                alert('An error occurred. Please try again later.');
            } finally {
                // Reset loading state
                btn.classList.remove('loading');
                btn.disabled = false;
            }
        });
    });

    // ==========================================
    // 3. Review Form Validation & Char Count
    // ==========================================
    const reviewForm = document.querySelector('form[action*="review"]');
    
    if (reviewForm) {
        const contentInput = reviewForm.querySelector('textarea[name="content"]');
        const submitBtn = reviewForm.querySelector('input[type="submit"], button[type="submit"]');

        if (contentInput) {
            // Configuration
            const minLength = 10;
            const maxLength = 500;

            // Create Character Counter Element
            const counterDiv = document.createElement('div');
            counterDiv.className = 'char-counter';
            counterDiv.id = 'review-char-counter'; // Add ID for accessibility
            counterDiv.style.textAlign = 'right';
            counterDiv.style.fontSize = '0.85rem';
            counterDiv.style.marginTop = '0.5rem';
            counterDiv.style.color = '#aaa'; // Improved contrast for default state
            contentInput.parentNode.insertBefore(counterDiv, contentInput.nextSibling);

            // Link counter to input via aria-describedby
            const existingDescribedBy = contentInput.getAttribute('aria-describedby') || '';
            if (!existingDescribedBy.includes('review-char-counter')) {
                contentInput.setAttribute('aria-describedby', (existingDescribedBy + ' review-char-counter').trim());
            }

            // Validation Logic
            const validateInput = () => {
                const currentLength = contentInput.value.length;
                counterDiv.textContent = `${currentLength} / ${maxLength} characters`;

                let isValid = true;
                if (currentLength < minLength) {
                    counterDiv.style.color = '#ff6b6b'; // Lighter red for better contrast in dark mode
                    counterDiv.textContent += ` (Min: ${minLength})`;
                    isValid = false;
                } else if (currentLength > maxLength) {
                    counterDiv.style.color = '#ff6b6b'; // Lighter red
                    isValid = false;
                } else {
                    counterDiv.style.color = '#4ade80'; // Lighter green for better contrast in dark mode
                }

                if (submitBtn) {
                    submitBtn.disabled = !isValid;
                    if (!isValid) {
                        submitBtn.style.opacity = '0.6';
                        submitBtn.style.cursor = 'not-allowed';
                    } else {
                        submitBtn.style.opacity = '1';
                        submitBtn.style.cursor = 'pointer';
                    }
                }
            };

            // Event Listeners
            contentInput.addEventListener('input', validateInput);
            
            // Initial check
            validateInput();

            // Prevent submit if invalid
            reviewForm.addEventListener('submit', (e) => {
                const currentLength = contentInput.value.length;
                if (currentLength < minLength || currentLength > maxLength) {
                    e.preventDefault();
                    alert(`Review must be between ${minLength} and ${maxLength} characters.`);
                    contentInput.focus();
                }
            });
        }
    }

    // ==========================================
    // 4. Download Functionality (Mock)
    // ==========================================
    const downloadBtns = document.querySelectorAll('.download-btn');
    
    downloadBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            
            if (btn.disabled || btn.classList.contains('loading')) return;
            
            const movieTitle = btn.dataset.movieTitle || 'Movie';
            const originalText = btn.innerHTML;
            
            // Set loading state
            btn.classList.add('loading');
            btn.disabled = true;
            btn.innerHTML = '⏳ Preparing...';
            
            // Simulate server request / download start
            setTimeout(() => {
                alert(`Starting download for "${movieTitle}"...\n(This is a demo, no actual file is downloaded)`);
                
                // Reset button
                btn.classList.remove('loading');
                btn.disabled = false;
                btn.innerHTML = originalText;
            }, 1500);
        });
    });
});
