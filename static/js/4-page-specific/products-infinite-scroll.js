/* ================================================
   HENDOSHI - PRODUCTS INFINITE SCROLL
   ================================================

   Purpose: Implements infinite scroll on the product listing page using
            IntersectionObserver to load additional pages as the user scrolls down

   Contains:
   - IntersectionObserver watching #infiniteScrollLoader with 200px rootMargin pre-trigger
   - loadNextPage() — fetches the next page URL, parses returned HTML, and appends new product cards to #productsGrid
   - Updates data-has-next and data-next-page attributes on the loader for sequential pagination
   - Stops observing when all pages are exhausted

   Dependencies: None (vanilla JS, fetch API, IntersectionObserver)
   Load Order: Load on product listing pages only
   ================================================ */

document.addEventListener('DOMContentLoaded', function() {
    const loader = document.getElementById('infiniteScrollLoader');
    const productsGrid = document.getElementById('productsGrid');
    
    if (!loader || !productsGrid) {
        console.log('Infinite scroll elements not found');
        return;
    }

    let isLoading = false;
    let currentPage = 1;
    const hasNext = loader.getAttribute('data-has-next') === 'true';
    
    if (!hasNext) {
        // console.log('No next page available');
        return;
    }

    // Create Intersection Observer
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !isLoading) {
                loadNextPage();
            }
        });
    }, {
        root: null,
        rootMargin: '200px', // Start loading 200px before reaching the loader
        threshold: 0.1
    });

    // Observe the loader element
    observer.observe(loader);

    async function loadNextPage() {
        const hasNext = loader.getAttribute('data-has-next') === 'true';
        const nextPage = loader.getAttribute('data-next-page');
        
        if (!hasNext || isLoading || !nextPage) {
            return;
        }

        isLoading = true;
        const spinner = loader.querySelector('.spinner-border');
        if (spinner) spinner.classList.remove('d-none');

        try {
            // Build URL with current filters and next page
            const url = new URL(window.location);
            url.searchParams.set('page', nextPage);
            
            // Request the full HTML page (do not send X-Requested-With),
            // so server returns the full rendered HTML the script can parse.
            const response = await fetch(url.toString());

            if (!response.ok) throw new Error('Network response was not ok');

            const html = await response.text();
            
            // Create temporary container to parse response
            const temp = document.createElement('div');
            temp.innerHTML = html;
            
            // Extract new product cards
            const newProducts = temp.querySelector('#productsGrid');
            if (newProducts && newProducts.children.length > 0) {
                // Append new products to grid
                Array.from(newProducts.children).forEach(child => {
                    productsGrid.appendChild(child);
                });
                
                // Update page counter
                currentPage = parseInt(nextPage);
                
                // Update loader attributes for next page
                const newLoader = temp.querySelector('#infiniteScrollLoader');
                if (newLoader) {
                    const newHasNext = newLoader.getAttribute('data-has-next') === 'true';
                    const newNextPage = newLoader.getAttribute('data-next-page');
                    
                    loader.setAttribute('data-has-next', newHasNext ? 'true' : 'false');
                    loader.setAttribute('data-next-page', newNextPage || '');
                    
                    // If no more pages, stop observing
                    if (!newHasNext) {
                        observer.disconnect();
                        loader.style.display = 'none';
                    }
                }
                
                // Reinitialize battle vest buttons for new products
                if (typeof initializeBattleVestButtons === 'function') {
                    initializeBattleVestButtons();
                }
                
                console.log(`Loaded page ${currentPage}`);
            }
            
        } catch (error) {
            console.error('Error loading next page:', error);
        } finally {
            isLoading = false;
            if (spinner) spinner.classList.add('d-none');
        }
    }
});
