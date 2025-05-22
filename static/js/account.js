document.addEventListener('DOMContentLoaded', function() {
  // Dashboard menu functionality
  const menuItems = document.querySelectorAll('.dashboard-menu li a');
  
  if (menuItems.length) {
    menuItems.forEach(item => {
      item.addEventListener('click', function(e) {
        // Prevent default only for demo purposes
        // In a real implementation, these would navigate to different pages or sections
        // For this demo, we'll just update the active state
        e.preventDefault();
        
        // Remove active class from all menu items
        menuItems.forEach(menuItem => {
          menuItem.parentElement.classList.remove('active');
        });
        
        // Add active class to clicked menu item
        this.parentElement.classList.add('active');
        
        // Show feedback message
        const targetId = this.getAttribute('href').substring(1);
        
        if (targetId === 'logout') {
          if (confirm('Are you sure you want to log out?')) {
            alert('You have been logged out. Redirecting to home page...');
            // In a real implementation, this would redirect to the home page
          }
        } else {
          alert(`The "${targetId}" section would be displayed here. This is just a demo.`);
        }
      });
    });
  }

  // Trip card interactions
  const tripCards = document.querySelectorAll('.trip-card');
  
  if (tripCards.length) {
    tripCards.forEach(card => {
      card.addEventListener('mouseenter', function() {
        this.style.backgroundColor = 'var(--primary-light)';
        this.style.transform = 'translateY(-5px)';
        this.style.boxShadow = 'var(--shadow-md)';
        this.style.transition = 'all var(--transition-fast)';
      });
      
      card.addEventListener('mouseleave', function() {
        this.style.backgroundColor = 'var(--very-light-gray)';
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = 'none';
      });
    });
  }

  // Activity item interactions
  const activityItems = document.querySelectorAll('.activity-item');
  
  if (activityItems.length) {
    activityItems.forEach(item => {
      item.addEventListener('mouseenter', function() {
        this.style.backgroundColor = 'var(--primary-light)';
        this.style.transform = 'translateX(5px)';
        this.style.transition = 'all var(--transition-fast)';
      });
      
      item.addEventListener('mouseleave', function() {
        this.style.backgroundColor = 'var(--very-light-gray)';
        this.style.transform = 'translateX(0)';
      });
    });
  }

  // Route card interactions
  const routeCards = document.querySelectorAll('.route-card');
  
  if (routeCards.length) {
    routeCards.forEach(card => {
      card.addEventListener('mouseenter', function() {
        this.style.backgroundColor = 'var(--primary-light)';
        this.style.transform = 'scale(1.02)';
        this.style.transition = 'all var(--transition-fast)';
      });
      
      card.addEventListener('mouseleave', function() {
        this.style.backgroundColor = 'var(--very-light-gray)';
        this.style.transform = 'scale(1)';
      });
    });
  }

  // Profile interactions
  const editLink = document.querySelector('.edit-link');
  
  if (editLink) {
    editLink.addEventListener('click', function(e) {
      e.preventDefault();
      
      // In a real implementation, this would show an edit profile form
      // For this demo, we'll just show a message
      alert('Profile edit form would be displayed here. This is just a demo.');
    });
  }

  // Stats card animations
  const statCards = document.querySelectorAll('.stat-card');
  
  if (statCards.length) {
    // Add counting animation to stat numbers
    statCards.forEach(card => {
      const statValue = card.querySelector('h3');
      
      if (statValue) {
        const targetValue = parseFloat(statValue.textContent);
        let startValue = 0;
        
        if (!isNaN(targetValue)) {
          // Animate only number values
          const duration = 1500; // Animation duration in ms
          const frameDuration = 1000 / 60; // 60 FPS
          const totalFrames = Math.round(duration / frameDuration);
          let frame = 0;
          
          // Store original text to handle non-numeric parts
          const originalText = statValue.textContent;
          const isRating = originalText.includes('/');
          
          const animate = () => {
            frame++;
            const progress = frame / totalFrames;
            const currentValue = isRating
              ? (targetValue * progress).toFixed(1)
              : Math.floor(targetValue * progress);
            
            statValue.textContent = isRating
              ? `${currentValue}/5`
              : currentValue;
            
            if (frame < totalFrames) {
              requestAnimationFrame(animate);
            } else {
              statValue.textContent = originalText; // Ensure final value is exactly as original
            }
          };
          
          requestAnimationFrame(animate);
        }
      }
    });
  }

  // Quick action buttons
  const actionBtns = document.querySelectorAll('.action-btn');
  
  if (actionBtns.length) {
    actionBtns.forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        
        // In a real implementation, these would navigate to different pages
        // For this demo, we'll just show a message
        const actionText = this.textContent.trim();
        alert(`The "${actionText}" action would be performed here. This is just a demo.`);
      });
    });
  }

  // Ticket action links
  const ticketActionLinks = document.querySelectorAll('.trip-actions .action-link');
  
  if (ticketActionLinks.length) {
    ticketActionLinks.forEach(link => {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        
        const actionText = this.textContent.trim();
        
        if (actionText === 'Cancel') {
          if (confirm('Are you sure you want to cancel this ticket? Cancellation fees may apply.')) {
            alert('Ticket cancellation process would start here. This is just a demo.');
          }
        } else {
          alert(`The "${actionText}" action would be performed here. This is just a demo.`);
        }
      });
    });
  }

  // Add a welcome animation
  const welcomeSection = document.querySelector('.welcome-section');
  
  if (welcomeSection) {
    welcomeSection.style.opacity = '0';
    welcomeSection.style.transform = 'translateY(20px)';
    welcomeSection.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    
    setTimeout(() => {
      welcomeSection.style.opacity = '1';
      welcomeSection.style.transform = 'translateY(0)';
    }, 300);
  }
});