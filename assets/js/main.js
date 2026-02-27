document.addEventListener('DOMContentLoaded', () => {
    
    // ==========================================
    // 1. Mobile Hamburger Menu Logic
    // ==========================================
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const mainNav = document.querySelector('.main-nav');

    if (mobileToggle && mainNav) {
        mobileToggle.addEventListener('click', () => {
            mainNav.classList.toggle('is-open');
        });
    }

    // ==========================================
    // 2. Smart Search Bar Logic (The Fix!)
    // ==========================================
    const searchForm = document.querySelector('.search-form');
    const searchInput = document.querySelector('.search-input');

    if (searchForm && searchInput) {
        searchForm.addEventListener('submit', (event) => {
            // Check if the input is completely empty (or just spaces)
            if (searchInput.value.trim() === '') {
                // Stop the page from changing
                event.preventDefault(); 
                // Force the search box to expand and put the blinking cursor inside
                searchInput.focus(); 
            }
        });
    }

});