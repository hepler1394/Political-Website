// js/main.js

document.addEventListener('DOMContentLoaded', () => {
    // --- Mobile Menu Toggle ---
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileMenuOpenIcon = mobileMenuButton.querySelector('svg:not(.hidden)');
    const mobileMenuCloseIcon = mobileMenuButton.querySelector('svg.hidden');

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
            mobileMenuOpenIcon.classList.toggle('hidden');
            mobileMenuCloseIcon.classList.toggle('hidden');
        });

        // Close mobile menu when a link is clicked
        const mobileNavLinks = mobileMenu.querySelectorAll('a');
        mobileNavLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (!mobileMenu.classList.contains('hidden')) {
                    mobileMenu.classList.add('hidden');
                    mobileMenuOpenIcon.classList.remove('hidden');
                    mobileMenuCloseIcon.classList.add('hidden');
                }
            });
        });
    }

    // --- Smooth Scrolling for Anchor Links (within the same page) ---
    // This is more relevant for single-page designs or sections within a long page.
    // For multi-page navigation, standard hrefs will work.
    // However, if you have anchor links like #section-id on a page, this will smooth scroll.
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            // Check if it's a link to an ID on the *current* page
            if (href.length > 1 && href.startsWith('#') && document.getElementById(href.substring(1))) {
                e.preventDefault();
                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
            // If it's a link like "get_involved.html#donate", let the browser handle the jump
            // after page load. Smooth scroll for cross-page anchors is more complex.
        });
    });

    // --- Set Current Year in Footer ---
    const currentYearSpan = document.getElementById('currentYear');
    if (currentYearSpan) {
        currentYearSpan.textContent = new Date().getFullYear();
    }

    // --- Basic Form Handling with Custom Modal ---
    // This is a generic handler. You might have multiple forms.
    // This example targets a form inside a section with id "get-involved-form-section"
    // or any form with a specific ID like "contactForm".
    const contactForms = document.querySelectorAll('form.contact-form-hook'); // Add class="contact-form-hook" to your forms
    const modal = document.getElementById('form-submission-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalMessage = document.getElementById('modal-message');
    const modalCloseButton = document.getElementById('modal-close-button');

    if (modal && modalCloseButton) {
        modalCloseButton.addEventListener('click', () => {
            modal.classList.remove('active');
        });
        // Close modal if backdrop is clicked
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                modal.classList.remove('active');
            }
        });
    }

    contactForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            // In a real application, you would handle form submission here (e.g., AJAX request to your backend)
            // For now, we just show the custom modal.
            
            const nameInput = form.querySelector('input[name="name"]');
            let userName = "Friend";
            if (nameInput && nameInput.value.trim() !== "") {
                userName = nameInput.value.trim().split(" ")[0]; // Get first name
            }

            if (modalTitle) modalTitle.textContent = `Thank You, ${userName}!`;
            if (modalMessage) modalMessage.textContent = 'Your message has been received. We will be in touch shortly.';
            if (modal) modal.classList.add('active');
            
            this.reset(); // Clears the form
        });
    });

    // --- Active Navigation Link Highlighting ---
    // This function highlights the current page's link in the navigation.
    const navLinks = document.querySelectorAll('header nav a');
    const currentPath = window.location.pathname.split("/").pop(); // Gets the current HTML file name

    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href').split("/").pop();
        // Handle index.html or empty path for homepage
        if ((currentPath === "" || currentPath === "index.html") && (linkPath === "" || linkPath === "index.html")) {
            link.classList.add('bg-blue-100', 'text-blue-700', 'font-semibold');
            link.classList.remove('text-gray-700', 'hover:text-blue-700');
        } else if (linkPath !== "" && currentPath === linkPath) {
            link.classList.add('bg-blue-100', 'text-blue-700', 'font-semibold');
            link.classList.remove('text-gray-700', 'hover:text-blue-700');
        } else {
            link.classList.remove('bg-blue-100', 'text-blue-700', 'font-semibold');
            link.classList.add('text-gray-700', 'hover:text-blue-700');
        }
    });

});