/**
 * Products Page Filters and Sort
 * Handles filter dropdown, tabs, and sort functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    const filtersSortBtn = document.getElementById('filtersSortBtn');
    const filtersDropdown = document.getElementById('filtersDropdown');
    const filtersOverlay = document.getElementById('filtersOverlay');
    const filtersCloseBtn = document.getElementById('filtersCloseBtn');
    const applyFiltersBtn = document.querySelector('.apply-filters-btn');
    const clearFiltersBtn = document.querySelector('.clear-filters-btn');
    
    const filterTabs = document.querySelectorAll('.filter-tab');
    // filterContents not used but kept for future filter content switching functionality

    // console.log('Products Filters JS loaded');
    // console.log('filtersSortBtn:', filtersSortBtn);
    // console.log('filtersDropdown:', filtersDropdown);
    // console.log('applyFiltersBtn:', applyFiltersBtn);

    // Open filters
    if (filtersSortBtn && filtersDropdown && filtersOverlay) {
        filtersSortBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Filters button clicked');
            filtersDropdown.classList.add('show');
            filtersOverlay.classList.add('show');
            document.body.style.overflow = 'hidden';
            console.log('Dropdown classes:', filtersDropdown.classList);
        });
    } else {
        console.log('Missing elements:', {
            btn: !!filtersSortBtn,
            dropdown: !!filtersDropdown,
            overlay: !!filtersOverlay
        });
    }

    // Close filters
    function closeFilters() {
        if (filtersDropdown) filtersDropdown.classList.remove('show');
        if (filtersOverlay) filtersOverlay.classList.remove('show');
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
            const filterPanes = document.querySelectorAll('.filter-tab-pane');
            filterPanes.forEach(pane => {
                if (pane.getAttribute('data-content') === targetTab) {
                    pane.classList.add('active');
                } else {
                    pane.classList.remove('active');
                }
            });
        });
    });

    // Sort selector (old style select - if it exists)
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

    // Handle filter checkboxes - DON'T redirect immediately
    const filterCheckboxes = document.querySelectorAll('.filter-option input[type="checkbox"]');
    filterCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const name = this.name;
            
            // Uncheck other checkboxes in the same group
            const groupCheckboxes = document.querySelectorAll(`input[name="${name}"]`);
            groupCheckboxes.forEach(cb => {
                if (cb !== this) {
                    cb.checked = false;
                }
            });
        });
    });

    // Apply Filters Button
    if (applyFiltersBtn) {
        // console.log('Apply filters button found, attaching handler');
        applyFiltersBtn.addEventListener('click', function() {
            // console.log('Apply filters clicked');
            const url = new URL(window.location);
            
            // Collect all checked checkboxes
            const checkedBoxes = document.querySelectorAll('.filter-option input[type="checkbox"]:checked');
            console.log('Checked boxes:', checkedBoxes.length);
            
            // Clear existing filter params
            url.searchParams.delete('collection');
            url.searchParams.delete('type');
            url.searchParams.delete('audience');
            url.searchParams.delete('sort');
            url.searchParams.delete('page');
            
            // Add selected filters
            checkedBoxes.forEach(checkbox => {
                const name = checkbox.name;
                const value = checkbox.value;
                console.log('Adding filter:', name, '=', value);
                
                if (value) {
                    url.searchParams.set(name, value);
                }
            });
            
            console.log('Redirecting to:', url.toString());
            // Redirect to filtered page
            window.location.href = url.toString();
        });
    } else {
        console.log('Apply filters button NOT found');
    }

    // Clear Filters Button
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            const url = new URL(window.location);
            
            // Clear all filter params
            url.searchParams.delete('collection');
            url.searchParams.delete('type');
            url.searchParams.delete('audience');
            url.searchParams.delete('sort');
            url.searchParams.delete('page');
            
            // Redirect to clean page
            window.location.href = url.toString();
        });
    }
});
