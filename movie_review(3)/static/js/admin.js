document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Delete Confirmation
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const message = this.dataset.confirm || 'Are you sure you want to delete this item? This action cannot be undone.';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    const batchDeleteForms = document.querySelectorAll('.batch-delete-form');
    batchDeleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const count = document.querySelectorAll('.batch-checkbox:checked').length;
            if (count === 0) {
                e.preventDefault();
                alert('Please select items to delete.');
                return;
            }
            if (!confirm(`Are you sure you want to delete ${count} selected items?`)) {
                e.preventDefault();
            }
        });
    });

    // Handle individual deletes within batch forms (to avoid nested forms)
    const deleteSingleBtns = document.querySelectorAll('.delete-single');
    deleteSingleBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.dataset.url;
            if (confirm('Are you sure you want to delete this item?')) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = url;
                
                const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrf_token';
                csrfInput.value = csrfToken;
                form.appendChild(csrfInput);

                document.body.appendChild(form);
                form.submit();
            }
        });
    });

    // 2. Batch Selection
    const selectAllCheckbox = document.getElementById('select-all');
    const batchCheckboxes = document.querySelectorAll('.batch-checkbox');
    const batchActionBtn = document.getElementById('batch-delete-btn');
    const selectedCountDisplay = document.getElementById('selected-count'); // Optional display

    function updateBatchState() {
        const checkedCount = document.querySelectorAll('.batch-checkbox:checked').length;
        
        // Update button state
        if (batchActionBtn) {
            batchActionBtn.disabled = checkedCount === 0;
        }

        // Update count display if exists
        if (selectedCountDisplay) {
            selectedCountDisplay.textContent = checkedCount;
        }

        // Update Select All checkbox state
        if (selectAllCheckbox) {
            selectAllCheckbox.checked = batchCheckboxes.length > 0 && checkedCount === batchCheckboxes.length;
            selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < batchCheckboxes.length;
        }
    }

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            batchCheckboxes.forEach(cb => {
                cb.checked = this.checked;
            });
            updateBatchState();
        });
    }

    batchCheckboxes.forEach(cb => {
        cb.addEventListener('change', updateBatchState);
    });

    // 3. Quick User Status Toggle (AJAX)
    const toggleButtons = document.querySelectorAll('.btn-toggle-status');
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const userId = this.dataset.id;
            const originalHtml = this.innerHTML;
            
            // Show loading state
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            this.disabled = true;

            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

            fetch(`/admin/users/${userId}/toggle-status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const badge = document.getElementById(`status-badge-${userId}`);
                    if (badge) {
                        if (data.is_active) {
                            badge.className = 'status-badge status-active';
                            badge.textContent = 'Active';
                        } else {
                            badge.className = 'status-badge status-banned';
                            badge.textContent = 'Banned';
                        }
                    }
                    // Optional: Show toast/notification
                } else {
                    alert(data.message || 'Failed to toggle status');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred');
            })
            .finally(() => {
                this.innerHTML = originalHtml;
                this.disabled = false;
            });
        });
    });

    // 4. Image Preview
    const posterInput = document.getElementById('poster_url_input');
    const posterPreview = document.getElementById('poster_preview');
    
    if (posterInput && posterPreview) {
        const posterImg = posterPreview.querySelector('img');
        const defaultImg = 'https://via.placeholder.com/200x300?text=No+Image';

        function updatePreview() {
            const url = posterInput.value.trim();
            if (url) {
                posterImg.src = url;
                posterPreview.style.display = 'block';
            } else {
                posterPreview.style.display = 'none';
            }
        }

        posterImg.onerror = function() {
            this.src = defaultImg;
        };

        posterInput.addEventListener('input', updatePreview);
        // Initial check
        updatePreview();
    }

    // 5. Sidebar Collapse
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const mainContent = document.querySelector('.main-content');

    // Restore state
    const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
    if (isCollapsed && sidebar && window.innerWidth > 768) {
        sidebar.classList.add('collapsed');
        if (mainContent) mainContent.classList.add('expanded');
    }

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            // Mobile behavior
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('active');
                if (overlay) overlay.classList.toggle('active');
            } else {
                // Desktop behavior
                sidebar.classList.toggle('collapsed');
                if (mainContent) mainContent.classList.toggle('expanded');
                localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('collapsed'));
            }
        });
    }

    if (overlay) {
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        });
    }

    // 6. Search Debounce
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        let timeout = null;
        input.addEventListener('input', function() {
            clearTimeout(timeout);
            const form = this.closest('form');
            if (form) {
                timeout = setTimeout(() => {
                    form.submit();
                }, 800); // 800ms delay
            }
        });
    });

});
