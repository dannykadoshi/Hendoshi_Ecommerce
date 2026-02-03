/**
 * Products Page Filters and Sort
 * Handles filter dropdown, tabs, and sort functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    const filtersSortBtn = document.getElementById('filtersSortBtn');
    const filtersDropdown = document.getElementById('filtersDropdown');
    const filtersOverlay = document.getElementById('filtersOverlay');
    const filtersCloseBtn = document.getElementById('filtersCloseBtn');
    
    const filterTabs = document.querySelectorAll('.filter-tab');
    const filterContents = document.querySelectorAll('.filter-content');

    // Open filters
    if (filtersSortBtn && filtersDropdown && filtersOverlay) {
        filtersSortBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            filtersDropdown.classList.add('show');
            filtersOverlay.classList.add('show');
            document.body.style.overflow = 'hidden';
        });
    }

    // Close filters
    function closeFilters() {
        filtersDropdown.classList.remove('show');
        filtersOverlay.classList.remove('show');
        document.body.style.overflow = '';
    }

    if (filtersCloseBtn) {
        filtersCloseBtn.addEventListener('click', closeFilters);
    }

    if (filtersOverlay) {
        filtersOverlay.addEventListener('click', closeFilters);
    }

    // Filter tabs
    filterTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Update active tab
            filterTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Update active content
            filterContents.forEach(content => {
                if (content.getAttribute('data-content') === targetTab) {
                    content.classList.add('active');
                } else {
                    content.classList.remove('active');
                }
            });
        });
    });

    // Sort selector
    const sortSelector = document.getElementById('sortSelector');
    if (sortSelector) {
        sortSelector.addEventListener('change', function() {
            const url = new URL(window.location);
            const value = this.value;
            
            if (value) {
                const [sort, direction] = value.split('-');
                url.searchParams.set('sort', sort);
                url.searchParams.set('direction', direction);
            } else {
                url.searchParams.delete('sort');
                url.searchParams.delete('direction');
            }
            
            window.location.href = url.toString();
        });
    }

    // Handle filter links
    const filterLinks = document.querySelectorAll('.filter-option');
    filterLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Let the link work normally, just close the filters
            closeFilters();
        });
    });
});
