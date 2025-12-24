// Gestion globale de l'application
class SignalAlertApp {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupModals();
        this.setupAuth();
        this.setupNotifications();
        this.setupMobileMenu();
    }
    
    setupModals() {
        // Login modal
        const loginModal = document.getElementById('loginModal');
        const loginBtn = document.getElementById('loginModalBtn');
        const closeLogin = document.querySelector('#loginModal .close-modal');
        
        if (loginBtn && loginModal) {
            loginBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.openModal(loginModal);
            });
            
            if (closeLogin) {
                closeLogin.addEventListener('click', () => this.closeModal(loginModal));
            }
        }
        
        // Register modal
        const registerModal = document.getElementById('registerModal');
        const registerBtns = document.querySelectorAll('#registerModalBtn, #heroRegisterBtn, #ctaRegisterBtn');
        
        registerBtns.forEach(btn => {
            if (btn) {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (registerModal) this.openModal(registerModal);
                });
            }
        });
        
        // Close modals on background click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });
        });
    }
    
    openModal(modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    closeModal(modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
    
    setupAuth() {
        // Login form
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(loginForm);
                const data = Object.fromEntries(formData);
                
                try {
                    const response = await fetch('/api/login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data),
                        credentials: 'include'
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        // Recharger la page pour mettre à jour l'état d'authentification
                        window.location.reload();
                    } else {
                        this.showAlert(result.error || 'Erreur de connexion', 'error');
                    }
                } catch (error) {
                    this.showAlert('Erreur réseau', 'error');
                }
            });
        }
        
        // Logout
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', async (e) => {
                e.preventDefault();
                
                try {
                    await fetch('/api/logout', {
                        method: 'POST',
                        credentials: 'include'
                    });
                    
                    window.location.reload();
                } catch (error) {
                    this.showAlert('Erreur lors de la déconnexion', 'error');
                }
            });
        }
    }
    
    setupNotifications() {
        // Charger les notifications si l'utilisateur est connecté
        if (document.body.dataset.userId) {
            this.loadNotifications();
        }
    }
    
    async loadNotifications() {
        try {
            const response = await fetch('/api/notifications', {
                credentials: 'include'
            });
            
            if (response.ok) {
                const notifications = await response.json();
                this.displayNotifications(notifications);
            }
        } catch (error) {
            console.error('Erreur chargement notifications:', error);
        }
    }
    
    displayNotifications(notifications) {
        // Implémenter l'affichage des notifications
        const unreadCount = notifications.filter(n => !n.is_read).length;
        
        if (unreadCount > 0) {
            // Ajouter un badge au menu
            const userBtn = document.querySelector('.user-btn');
            if (userBtn) {
                let badge = userBtn.querySelector('.notification-badge');
                if (!badge) {
                    badge = document.createElement('span');
                    badge.className = 'notification-badge';
                    userBtn.appendChild(badge);
                }
                badge.textContent = unreadCount;
            }
        }
    }
    
    setupMobileMenu() {
        const menuBtn = document.querySelector('.mobile-menu-btn');
        const navMenu = document.querySelector('.main-nav'); // Corrected selector
        
        if (menuBtn && navMenu) {
            menuBtn.addEventListener('click', () => {
                navMenu.classList.toggle('active');
                // Toggle the icon between bars and times
                menuBtn.innerHTML = navMenu.classList.contains('active') 
                    ? '<i class="fas fa-times"></i>'
                    : '<i class="fas fa-bars"></i>';
            });
        }
    }
    
    showAlert(message, type = 'info') {
        // Créer une alerte temporaire
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-temporary`;
        alert.innerHTML = `
            ${message}
            <button class="close-alert">&times;</button>
        `;
        
        document.body.appendChild(alert);
        
        setTimeout(() => {
            alert.classList.add('show');
        }, 10);
        
        // Fermer l'alerte
        const closeBtn = alert.querySelector('.close-alert');
        closeBtn.addEventListener('click', () => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 300);
        });
        
        // Auto-fermeture après 5 secondes
        setTimeout(() => {
            if (alert.parentNode) {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 300);
            }
        }, 5000);
    }
}

// Initialiser l'application quand le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    window.signalAlertApp = new SignalAlertApp();
});