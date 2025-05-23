/**
 * Project 2028 - America's Progressive Future
 * Main JavaScript File
 * Version 1.0
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize preloader
    initPreloader();
    
    // Initialize navigation
    initNavigation();
    
    // Initialize floating action button
    initFAB();
    
    // Initialize animations
    initAnimations();
    
    // Initialize charts if they exist on the page
    if (document.querySelector('#economyChart')) initCharts();
    
    // Initialize testimonial slider if it exists
    if (document.querySelector('.testimonial-slider')) initTestimonialSlider();
    
    // Initialize news tabs if they exist
    if (document.querySelector('.news-tabs')) initNewsTabs();
    
    // Initialize form handlers
    initForms();
});

// Preloader initialization
function initPreloader() {
    const preloader = document.querySelector('.preloader');
    
    if (!preloader) return;
    
    // Hide preloader after content is loaded
    window.addEventListener('load', function() {
        setTimeout(function() {
            preloader.classList.add('hidden');
            
            // Remove preloader from DOM after transition
            setTimeout(function() {
                preloader.style.display = 'none';
            }, 500);
        }, 1000);
    });
}

// Navigation initialization
function initNavigation() {
    const nav = document.querySelector('.main-nav');
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (!nav || !menuToggle || !navLinks) return;
    
    // Handle menu toggle on mobile
    menuToggle.addEventListener('click', function() {
        this.classList.toggle('active');
        navLinks.classList.toggle('active');
    });
    
    // Close menu when clicking a link
    const links = navLinks.querySelectorAll('a');
    links.forEach(link => {
        link.addEventListener('click', function() {
            menuToggle.classList.remove('active');
            navLinks.classList.remove('active');
        });
    });
    
    // Change navigation style on scroll
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
    });
}

// Floating Action Button initialization
function initFAB() {
    const fab = document.querySelector('.fab');
    const fabButton = document.querySelector('.fab-button');
    
    if (!fab || !fabButton) return;
    
    fabButton.addEventListener('click', function() {
        fab.classList.toggle('active');
    });
    
    // Close FAB when clicking outside
    document.addEventListener('click', function(event) {
        if (!fab.contains(event.target)) {
            fab.classList.remove('active');
        }
    });
}

// Animations initialization
function initAnimations() {
    // Initialize GSAP if available
    if (typeof gsap !== 'undefined') {
        // Register ScrollTrigger plugin if available
        if (typeof ScrollTrigger !== 'undefined') {
            gsap.registerPlugin(ScrollTrigger);
            
            // Animate section headers
            gsap.utils.toArray('.section-header').forEach(header => {
                gsap.from(header, {
                    y: 50,
                    opacity: 0,
                    duration: 1,
                    scrollTrigger: {
                        trigger: header,
                        start: 'top 80%',
                        toggleActions: 'play none none none'
                    }
                });
            });
            
            // Animate policy cards
            gsap.utils.toArray('.policy-card').forEach((card, i) => {
                gsap.from(card, {
                    y: 100,
                    opacity: 0,
                    duration: 0.8,
                    delay: i * 0.2,
                    scrollTrigger: {
                        trigger: card,
                        start: 'top 80%',
                        toggleActions: 'play none none none'
                    }
                });
            });
            
            // Animate news cards
            gsap.utils.toArray('.news-card').forEach((card, i) => {
                gsap.from(card, {
                    y: 100,
                    opacity: 0,
                    duration: 0.8,
                    delay: i * 0.2,
                    scrollTrigger: {
                        trigger: card,
                        start: 'top 80%',
                        toggleActions: 'play none none none'
                    }
                });
            });
        }
        
        // Hero section animations
        const heroText = document.querySelector('.hero-text');
        const heroImage = document.querySelector('.hero-image');
        
        if (heroText && heroImage) {
            gsap.from(heroText, {
                x: -100,
                opacity: 0,
                duration: 1.2,
                delay: 0.5
            });
            
            gsap.from(heroImage, {
                x: 100,
                opacity: 0,
                duration: 1.2,
                delay: 0.8
            });
        }
    }
    
    // Initialize particles.js if available
    if (typeof particlesJS !== 'undefined') {
        const heroParticles = document.querySelector('.hero-particles');
        
        if (heroParticles) {
            particlesJS('hero-particles', {
                particles: {
                    number: {
                        value: 80,
                        density: {
                            enable: true,
                            value_area: 800
                        }
                    },
                    color: {
                        value: '#00a8ff'
                    },
                    shape: {
                        type: 'circle',
                        stroke: {
                            width: 0,
                            color: '#000000'
                        }
                    },
                    opacity: {
                        value: 0.5,
                        random: true,
                        anim: {
                            enable: true,
                            speed: 1,
                            opacity_min: 0.1,
                            sync: false
                        }
                    },
                    size: {
                        value: 3,
                        random: true,
                        anim: {
                            enable: true,
                            speed: 2,
                            size_min: 0.1,
                            sync: false
                        }
                    },
                    line_linked: {
                        enable: true,
                        distance: 150,
                        color: '#00a8ff',
                        opacity: 0.4,
                        width: 1
                    },
                    move: {
                        enable: true,
                        speed: 1,
                        direction: 'none',
                        random: true,
                        straight: false,
                        out_mode: 'out',
                        bounce: false,
                        attract: {
                            enable: false,
                            rotateX: 600,
                            rotateY: 1200
                        }
                    }
                },
                interactivity: {
                    detect_on: 'canvas',
                    events: {
                        onhover: {
                            enable: true,
                            mode: 'grab'
                        },
                        onclick: {
                            enable: true,
                            mode: 'push'
                        },
                        resize: true
                    },
                    modes: {
                        grab: {
                            distance: 140,
                            line_linked: {
                                opacity: 1
                            }
                        },
                        push: {
                            particles_nb: 4
                        }
                    }
                },
                retina_detect: true
            });
        }
    }
    
    // Initialize glitch effect
    const glitchElements = document.querySelectorAll('.glitch');
    
    glitchElements.forEach(element => {
        // Set data-text attribute to match text content if not already set
        if (!element.getAttribute('data-text')) {
            element.setAttribute('data-text', element.textContent);
        }
    });
}

// Charts initialization
function initCharts() {
    // Initialize Chart.js if available
    if (typeof Chart !== 'undefined') {
        // Economy Chart
        const economyChart = document.getElementById('economyChart');
        if (economyChart) {
            new Chart(economyChart, {
                type: 'line',
                data: {
                    labels: ['2023', '2024', '2025', '2026', '2027', '2028'],
                    datasets: [
                        {
                            label: 'Project 2028 Policies',
                            data: [100, 115, 135, 160, 190, 230],
                            borderColor: '#00a8ff',
                            backgroundColor: 'rgba(0, 168, 255, 0.1)',
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: 'Current Trajectory',
                            data: [100, 105, 110, 115, 120, 125],
                            borderColor: '#ff3e6c',
                            backgroundColor: 'rgba(255, 62, 108, 0.1)',
                            tension: 0.4,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                color: 'rgba(255, 255, 255, 0.7)'
                            }
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: 'rgba(255, 255, 255, 0.7)'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: 'rgba(255, 255, 255, 0.7)'
                            }
                        }
                    }
                }
            });
        }
        
        // Climate Chart
        const climateChart = document.getElementById('climateChart');
        if (climateChart) {
            new Chart(climateChart, {
                type: 'line',
                data: {
                    labels: ['2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030'],
                    datasets: [
                        {
                            label: 'Project 2028 Policies',
                            data: [100, 90, 75, 60, 50, 40, 30, 20],
                            borderColor: '#00a8ff',
                            backgroundColor: 'rgba(0, 168, 255, 0.1)',
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: 'Business as Usual',
                            data: [100, 102, 105, 108, 112, 115, 120, 125],
                            borderColor: '#ff3e6c',
                            backgroundColor: 'rgba(255, 62, 108, 0.1)',
                            tension: 0.4,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                color: 'rgba(255, 255, 255, 0.7)'
                            }
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: 'rgba(255, 255, 255, 0.7)'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: 'rgba(255, 255, 255, 0.7)'
                            }
                        }
                    }
                }
            });
        }
        
        // Education Chart
        const educationChart = document.getElementById('educationChart');
        if (educationChart) {
            new Chart(educationChart, {
                type: 'bar',
                data: {
                    labels: ['High School Graduation', 'College Enrollment', 'College Completion', 'Advanced Degrees'],
                    datasets: [
                        {
                            label: 'Project 2028 Policies',
                            data: [95, 85, 75, 40],
                            backgroundColor: 'rgba(0, 168, 255, 0.7)'
                        },
                        {
                            label: 'Current Trajectory',
                            data: [85, 65, 55, 25],
                            backgroundColor: 'rgba(255, 62, 108, 0.7)'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                color: 'rgba(255, 255, 255, 0.7)'
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: 'rgba(255, 255, 255, 0.7)'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: 'rgba(255, 255, 255, 0.7)'
                            }
                        }
                    }
                }
            });
        }
        
        // Technology Chart
        const techChart = document.getElementById('techChart');
        if (techChart) {
            new Chart(techChart, {
                type: 'radar',
                data: {
                    labels: ['Innovation', 'Equity', 'Privacy', 'Security', 'Accessibility', 'Economic Growth'],
                    datasets: [
                        {
                            label: 'Project 2028 Policies',
                            data: [90, 95, 85, 80, 90, 85],
                            borderColor: '#00a8ff',
                            backgroundColor: 'rgba(0, 168, 255, 0.2)'
                        },
                        {
                            label: 'Current Trajectory',
                            data: [75, 50, 60, 65, 55, 70],
                            borderColor: '#ff3e6c',
                            backgroundColor: 'rgba(255, 62, 108, 0.2)'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                color: 'rgba(255, 255, 255, 0.7)'
                            }
                        }
                    },
                    scales: {
                        r: {
                            angleLines: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            pointLabels: {
                                color: 'rgba(255, 255, 255, 0.7)'
                            },
                            ticks: {
                                backdropColor: 'transparent',
                                color: 'rgba(255, 255, 255, 0.7)'
                            }
                        }
                    }
                }
            });
        }
    }
}

// Testimonial slider initialization
function initTestimonialSlider() {
    const slider = document.querySelector('.testimonial-slider');
    const slides = document.querySelectorAll('.testimonial-slide');
    const dots = document.querySelectorAll('.testimonial-dots .dot');
    const prevBtn = document.querySelector('.testimonial-prev');
    const nextBtn = document.querySelector('.testimonial-next');
    
    if (!slider || !slides.length || !dots.length || !prevBtn || !nextBtn) return;
    
    let currentSlide = 0;
    
    // Hide all slides except the first one
    slides.forEach((slide, index) => {
        if (index !== 0) {
            slide.style.display = 'none';
        }
    });
    
    // Function to show a specific slide
    function showSlide(index) {
        // Hide all slides
        slides.forEach(slide => {
            slide.style.display = 'none';
        });
        
        // Remove active class from all dots
        dots.forEach(dot => {
            dot.classList.remove('active');
        });
        
        // Show the selected slide
        slides[index].style.display = 'block';
        
        // Add active class to the corresponding dot
        dots[index].classList.add('active');
        
        // Update current slide index
        currentSlide = index;
    }
    
    // Event listeners for prev/next buttons
    prevBtn.addEventListener('click', function() {
        let newIndex = currentSlide - 1;
        if (newIndex < 0) {
            newIndex = slides.length - 1;
        }
        showSlide(newIndex);
    });
    
    nextBtn.addEventListener('click', function() {
        let newIndex = currentSlide + 1;
        if (newIndex >= slides.length) {
            newIndex = 0;
        }
        showSlide(newIndex);
    });
    
    // Event listeners for dots
    dots.forEach((dot, index) => {
        dot.addEventListener('click', function() {
            showSlide(index);
        });
    });
    
    // Auto-advance slides every 5 seconds
    setInterval(function() {
        let newIndex = currentSlide + 1;
        if (newIndex >= slides.length) {
            newIndex = 0;
        }
        showSlide(newIndex);
    }, 5000);
}

// News tabs initialization
function initNewsTabs() {
    const tabs = document.querySelectorAll('.news-tab');
    const panels = document.querySelectorAll('.news-panel');
    
    if (!tabs.length || !panels.length) return;
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            tabs.forEach(t => {
                t.classList.remove('active');
            });
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Hide all panels
            panels.forEach(panel => {
                panel.classList.remove('active');
            });
            
            // Show the corresponding panel
            const tabId = this.getAttribute('data-tab');
            const panel = document.getElementById(tabId + '-news');
            if (panel) {
                panel.classList.add('active');
            }
        });
    });
}

// Form handlers initialization
function initForms() {
    // Newsletter form
    const newsletterForms = document.querySelectorAll('.newsletter-form');
    
    newsletterForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const emailInput = this.querySelector('input[type="email"]');
            if (emailInput && emailInput.value) {
                // Simulate form submission
                const submitButton = this.querySelector('button');
                if (submitButton) {
                    const originalText = submitButton.textContent;
                    submitButton.textContent = 'Subscribed!';
                    submitButton.disabled = true;
                    
                    // Reset form after 2 seconds
                    setTimeout(function() {
                        emailInput.value = '';
                        submitButton.textContent = originalText;
                        submitButton.disabled = false;
                    }, 2000);
                }
            }
        });
    });
    
    // Volunteer form
    const volunteerForm = document.querySelector('.volunteer-form');
    
    if (volunteerForm) {
        volunteerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Simulate form submission
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                const originalText = submitButton.textContent;
                submitButton.textContent = 'Thank You!';
                submitButton.disabled = true;
                
                // Show success message
                const formContainer = document.querySelector('.form-container');
                if (formContainer) {
                    const successMessage = document.createElement('div');
                    successMessage.className = 'success-message';
                    successMessage.innerHTML = '<h3>Thank You for Volunteering!</h3><p>We\'ve received your information and will be in touch soon about how you can get involved with Project 2028.</p>';
                    
                    // Replace form with success message
                    formContainer.innerHTML = '';
                    formContainer.appendChild(successMessage);
                    
                    // Scroll to success message
                    successMessage.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    }
    
    // Donation options
    const donationButtons = document.querySelectorAll('.donation-amount');
    
    if (donationButtons.length) {
        donationButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                donationButtons.forEach(btn => {
                    btn.classList.remove('active');
                });
                
                // Add active class to clicked button
                this.classList.add('active');
            });
        });
    }
    
    // Copy link functionality
    const copyLinkButtons = document.querySelectorAll('.copy-link');
    
    copyLinkButtons.forEach(button => {
        button.addEventListener('click', function() {
            const linkInput = this.previousElementSibling;
            if (linkInput) {
                // Select the text
                linkInput.select();
                linkInput.setSelectionRange(0, 99999); // For mobile devices
                
                // Copy the text
                document.execCommand('copy');
                
                // Update button text temporarily
                const originalText = this.textContent;
                this.textContent = 'Copied!';
                
                // Reset button text after 2 seconds
                setTimeout(() => {
                    this.textContent = originalText;
                }, 2000);
            }
        });
    });
}

// Video placeholder click handler
document.addEventListener('click', function(e) {
    if (e.target.closest('.video-placeholder')) {
        const placeholder = e.target.closest('.video-placeholder');
        const container = placeholder.closest('.video-container');
        
        if (container) {
            // Replace placeholder with embedded video (simulated)
            container.innerHTML = `
                <div class="video-frame">
                    <div class="video-message">
                        <i class="fas fa-film"></i>
                        <p>Video would play here in production environment</p>
                    </div>
                </div>
            `;
            
            // Style the video frame
            const videoFrame = container.querySelector('.video-frame');
            if (videoFrame) {
                videoFrame.style.position = 'absolute';
                videoFrame.style.top = '0';
                videoFrame.style.left = '0';
                videoFrame.style.width = '100%';
                videoFrame.style.height = '100%';
                videoFrame.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
                videoFrame.style.display = 'flex';
                videoFrame.style.justifyContent = 'center';
                videoFrame.style.alignItems = 'center';
                videoFrame.style.color = '#fff';
                videoFrame.style.textAlign = 'center';
            }
            
            // Style the video message
            const videoMessage = container.querySelector('.video-message');
            if (videoMessage) {
                videoMessage.style.padding = '2rem';
            }
            
            // Style the icon
            const icon = container.querySelector('.fas');
            if (icon) {
                icon.style.fontSize = '5rem';
                icon.style.marginBottom = '2rem';
                icon.style.color = '#00a8ff';
            }
        }
    }
});
