// Base de données simulée de signalements
        const reportsDatabase = [
            {
                id: 1,
                type: "lost",
                title: "Montre bracelet en or",
                location: "Cotonou, Marché Dantokpa",
                date: "2023-06-15",
                category: "Bijoux",
                description: "Montre bracelet en or perdue près de l'entrée principale du marché Dantokpa. C'est un souvenir de famille.",
                contact: "akpan.b@email.com",
                reward: "50000 CFA",
                status: "active",
                image: "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80"
            },
            {
                id: 2,
                type: "missing",
                title: "Boco Zinsou, 72 ans",
                location: "Porto-Novo, Jardin Public",
                date: "2023-06-12",
                category: "Personne disparue",
                description: "Boco Zinsou, 72 ans, disparu depuis hier après-midi. Il portait une chemise blanche et un pantalon noir. Souffre de légers troubles de la mémoire.",
                contact: "famille.zinsou@email.com",
                reward: "",
                status: "active",
                image: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80"
            },
            {
                id: 3,
                type: "stolen",
                title: "Moto-taxi 'Zemidjan'",
                location: "Parakou, Gare",
                date: "2023-06-10",
                category: "Véhicule",
                description: "Moto-taxi de marque Bajaj, volée devant la gare de Parakou. De couleur jaune avec l'immatriculation 'BJ 1234'.",
                contact: "+229 97 12 34 56",
                reward: "100000 CFA",
                status: "active",
                image: "https://images.unsplash.com/photo-1556656793-08538906a9f8?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80"
            },
            {
                id: 4,
                type: "lost",
                title: "Portefeuille en cuir noir",
                location: "Abomey-Calavi, Université",
                date: "2023-06-08",
                category: "Documents",
                description: "Portefeuille en cuir noir contenant une carte d'étudiant, une carte d'identité et de l'argent. Perdu près de l'amphithéâtre.",
                contact: "dossou.a@email.com",
                reward: "25000 CFA",
                status: "found",
                image: "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80"
            },
            {
                id: 5,
                type: "stolen",
                title: "Ordinateur portable HP",
                location: "Cotonou, Cybercafé",
                date: "2023-06-05",
                category: "Électronique",
                description: "Ordinateur portable HP 15 pouces volé dans un cybercafé du quartier Haie Vive. L'ordinateur est noir avec un autocollant du drapeau béninois.",
                contact: "yao.g@email.com",
                reward: "150000 CFA",
                status: "active",
                image: "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80"
            },
            {
                id: 6,
                type: "missing",
                title: "Chien de race locale",
                location: "Ganvié, Lac Nokoué",
                date: "2023-06-03",
                category: "Animal",
                description: "Kiki, notre chien, a disparu près de l'embarcadère. Il est de couleur sable et porte un collier en perles.",
                contact: "+229 95 67 89 12",
                reward: "75000 CFA",
                status: "found",
                image: "https://images.unsplash.com/photo-1568572933382-74d440642117?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80"
            }
        ];

        // Éléments DOM
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');
        const mainNav = document.getElementById('mainNav');
        const reportBtn = document.getElementById('reportBtn');
        const heroReportBtn = document.getElementById('heroReportBtn');
        const loginBtn = document.getElementById('loginBtn');
        const reportModal = document.getElementById('reportModal');
        const loginModal = document.getElementById('loginModal');
        const closeReportModal = document.getElementById('closeReportModal');
        const closeLoginModal = document.getElementById('closeLoginModal');
        const cancelReport = document.getElementById('cancelReport');
        const reportForm = document.getElementById('reportForm');
        const loginForm = document.getElementById('loginForm');
        const filterButtons = document.querySelectorAll('.filter-btn');
        const reportsContainer = document.getElementById('reportsContainer');
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        const categoryButtons = document.querySelectorAll('.category-btn');
        const browseBtn = document.getElementById('browseBtn');
        const showRegister = document.getElementById('showRegister');
        
        // Variables d'état
        let currentFilter = 'all';
        let displayedReports = 3;
        
        // Initialisation
        document.addEventListener('DOMContentLoaded', function() {
            // Charger les signalements initiaux
            loadReports();
            
            // Configurer la date du formulaire à aujourd'hui
            document.getElementById('reportDate').valueAsDate = new Date();
        });
        
        // Gestion du menu mobile
        mobileMenuBtn.addEventListener('click', function() {
            mainNav.classList.toggle('active');
            mobileMenuBtn.innerHTML = mainNav.classList.contains('active') 
                ? '<i class="fas fa-times"></i>' 
                : '<i class="fas fa-bars"></i>';
        });
        
        // Fermer le menu mobile en cliquant sur un lien
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.addEventListener('click', function() {
                mainNav.classList.remove('active');
                mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
            });
        });
        
        // Gestion des modals
        function openModal(modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
        
        function closeModal(modal) {
            modal.classList.remove('active');
            document.body.style.overflow = 'auto';
        }
        
        reportBtn.addEventListener('click', () => openModal(reportModal));
        heroReportBtn.addEventListener('click', () => openModal(reportModal));
        loginBtn.addEventListener('click', () => openModal(loginModal));
        
        closeReportModal.addEventListener('click', () => closeModal(reportModal));
        closeLoginModal.addEventListener('click', () => closeModal(loginModal));
        cancelReport.addEventListener('click', () => closeModal(reportModal));
        
        // Fermer les modals en cliquant à l'extérieur
        window.addEventListener('click', function(e) {
            if (e.target === reportModal) closeModal(reportModal);
            if (e.target === loginModal) closeModal(loginModal);
        });
        
        // Gestion des filtres
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Mettre à jour le bouton actif
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Mettre à jour le filtre
                currentFilter = this.getAttribute('data-filter');
                displayedReports = 3;
                
                // Recharger les signalements
                loadReports();
            });
        });
        
        // Gestion des boutons de catégorie
        categoryButtons.forEach(button => {
            button.addEventListener('click', function() {
                const category = this.getAttribute('data-category');
                
                // Mettre à jour les filtres
                filterButtons.forEach(btn => btn.classList.remove('active'));
                document.querySelector(`.filter-btn[data-filter="${category}"]`).classList.add('active');
                
                // Mettre à jour le filtre
                currentFilter = category;
                displayedReports = 3;
                
                // Recharger les signalements
                loadReports();
                
                // Faire défiler jusqu'à la section des signalements
                document.getElementById('reports').scrollIntoView({ behavior: 'smooth' });
            });
        });
        
        // Gestion du bouton "Parcourir"
        browseBtn.addEventListener('click', function() {
            document.getElementById('reports').scrollIntoView({ behavior: 'smooth' });
        });
        
        // Gestion du bouton "Charger plus"
        loadMoreBtn.addEventListener('click', function() {
            displayedReports += 3;
            loadReports();
        });
        
        // Gestion du formulaire de signalement
        reportForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Récupérer les valeurs du formulaire
            const reportType = document.getElementById('reportType').value;
            const title = document.getElementById('reportTitle').value;
            const location = document.getElementById('reportLocation').value;
            const date = document.getElementById('reportDate').value;
            const category = document.getElementById('reportCategory').value;
            const description = document.getElementById('reportDescription').value;
            const contact = document.getElementById('reportContact').value;
            const reward = document.getElementById('reportReward').value;
            
            // Créer un nouvel objet signalement
            const newReport = {
                id: reportsDatabase.length + 1,
                type: reportType,
                title: title,
                location: location,
                date: date,
                category: category,
                description: description,
                contact: contact,
                reward: reward,
                status: "active",
                image: getRandomImageForType(reportType)
            };
            
            // Ajouter à la base de données simulée
            reportsDatabase.unshift(newReport);
            
            // Réinitialiser le formulaire
            reportForm.reset();
            document.getElementById('reportDate').valueAsDate = new Date();
            
            // Fermer le modal
            closeModal(reportModal);
            
            // Afficher un message de confirmation
            alert('Votre signalement a été publié avec succès ! Il est maintenant visible par la communauté.');
            
            // Recharger les signalements
            currentFilter = 'all';
            filterButtons.forEach(btn => btn.classList.remove('active'));
            document.querySelector('.filter-btn[data-filter="all"]').classList.add('active');
            displayedReports = 3;
            loadReports();
        });
        
        // Gestion du formulaire de connexion
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            
            // Simulation de connexion
            if (email && password) {
                alert(`Connexion réussie avec l'adresse: ${email}`);
                closeModal(loginModal);
                loginBtn.innerHTML = '<i class="fas fa-user"></i> Mon compte';
                loginBtn.classList.remove('btn-outline');
                loginBtn.classList.add('btn-secondary');
                
                // Mettre à jour l'action de connexion pour ouvrir un dashboard
                loginBtn.removeEventListener('click', () => openModal(loginModal));
                loginBtn.addEventListener('click', function() {
                    alert('Ouverture du tableau de bord utilisateur (simulation)');
                });
            } else {
                alert('Veuillez remplir tous les champs');
            }
        });
        
        // Gestion du lien "S'inscrire"
        showRegister.addEventListener('click', function(e) {
            e.preventDefault();
            closeModal(loginModal);
            alert('Ouverture du formulaire d\'inscription (simulation)');
        });
        
        // Fonction pour charger les signalements
        function loadReports() {
            // Filtrer les signalements selon le filtre actif
            let filteredReports = reportsDatabase;
            
            if (currentFilter !== 'all') {
                if (currentFilter === 'found') {
                    filteredReports = reportsDatabase.filter(report => report.status === 'found');
                } else {
                    filteredReports = reportsDatabase.filter(report => report.type === currentFilter);
                }
            }
            
            // Limiter le nombre de signalements affichés
            const reportsToShow = filteredReports.slice(0, displayedReports);
            
            // Vider le conteneur
            reportsContainer.innerHTML = '';
            
            // Générer les cartes de signalement
            reportsToShow.forEach(report => {
                const reportCard = createReportCard(report);
                reportsContainer.appendChild(reportCard);
            });
            
            // Afficher/masquer le bouton "Charger plus"
            if (displayedReports >= filteredReports.length) {
                loadMoreBtn.style.display = 'none';
            } else {
                loadMoreBtn.style.display = 'inline-flex';
            }
        }
        
        // Fonction pour créer une carte de signalement
        function createReportCard(report) {
            const card = document.createElement('div');
            card.className = 'report-card card';
            card.setAttribute('data-category', report.type);
            card.setAttribute('data-status', report.status);
            
            // Déterminer la classe de badge selon le type
            let badgeClass = '';
            let badgeText = '';
            
            switch(report.type) {
                case 'lost':
                    badgeClass = 'badge-lost';
                    badgeText = 'Objet perdu';
                    break;
                case 'missing':
                    badgeClass = 'badge-missing';
                    badgeText = 'Personne disparue';
                    break;
                case 'stolen':
                    badgeClass = 'badge-stolen';
                    badgeText = 'Chose volée';
                    break;
            }
            
            // Ajouter un badge supplémentaire si retrouvé
            const statusBadge = report.status === 'found' ? '<span class="badge badge-found" style="margin-left: 0.5rem;">Retrouvé</span>' : '';
            
            // Formater la date
            const formattedDate = new Date(report.date).toLocaleDateString('fr-FR', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
            });
            
            // Créer le contenu HTML de la carte
            card.innerHTML = `
                <img src="${report.image}" alt="${report.title}" class="card-image">
                <div class="card-content">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span class="badge ${badgeClass}">${badgeText}</span>
                        ${statusBadge}
                    </div>
                    <h3>${report.title}</h3>
                    <div class="card-meta">
                        <span><i class="fas fa-map-marker-alt"></i> ${report.location}</span>
                        <span><i class="far fa-calendar"></i> ${formattedDate}</span>
                    </div>
                    <p class="card-description">${report.description}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 600; color: var(--dark-color);">${report.category}</span>
                        <button class="btn btn-primary view-report-btn" data-id="${report.id}">
                            <i class="fas fa-eye"></i> Voir détails
                        </button>
                    </div>
                </div>
            `;
            
            // Ajouter un écouteur d'événement au bouton "Voir détails"
            const viewBtn = card.querySelector('.view-report-btn');
            viewBtn.addEventListener('click', function() {
                viewReportDetails(report.id);
            });
            
            return card;
        }
        
        // Fonction pour afficher les détails d'un signalement
        function viewReportDetails(id) {
            const report = reportsDatabase.find(r => r.id === id);
            
            if (!report) return;
            
            // Formater la date
            const formattedDate = new Date(report.date).toLocaleDateString('fr-FR', {
                weekday: 'long',
                day: 'numeric',
                month: 'long',
                year: 'numeric'
            });
            
            // Déterminer le type en français
            let typeText = '';
            switch(report.type) {
                case 'lost': typeText = 'Objet perdu'; break;
                case 'missing': typeText = 'Personne disparue'; break;
                case 'stolen': typeText = 'Chose volée'; break;
            }
            
            // Créer le contenu du modal de détails
            const modalContent = `
                <div class="modal-header">
                    <h2>Détails du signalement</h2>
                    <button class="modal-close" id="closeDetailsModal">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div style="display: flex; gap: var(--spacing-md); margin-bottom: var(--spacing-md); flex-wrap: wrap;">
                        <span class="badge ${report.type === 'lost' ? 'badge-lost' : report.type === 'missing' ? 'badge-missing' : 'badge-stolen'}">${typeText}</span>
                        ${report.status === 'found' ? '<span class="badge badge-found">Retrouvé/Résolu</span>' : ''}
                    </div>
                    
                    <h3>${report.title}</h3>
                    
                    <div style="margin-bottom: var(--spacing-md);">
                        <img src="${report.image}" alt="${report.title}" style="width: 100%; border-radius: var(--border-radius);">
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--spacing-md); margin-bottom: var(--spacing-lg);">
                        <div>
                            <strong><i class="fas fa-map-marker-alt"></i> Lieu</strong>
                            <p>${report.location}</p>
                        </div>
                        <div>
                            <strong><i class="far fa-calendar"></i> Date</strong>
                            <p>${formattedDate}</p>
                        </div>
                        <div>
                            <strong><i class="fas fa-tag"></i> Catégorie</strong>
                            <p>${report.category}</p>
                        </div>
                        ${report.reward ? `
                        <div>
                            <strong><i class="fas fa-gift"></i> Récompense</strong>
                            <p>${report.reward}</p>
                        </div>
                        ` : ''}
                    </div>
                    
                    <div style="margin-bottom: var(--spacing-lg);">
                        <strong>Description</strong>
                        <p>${report.description}</p>
                    </div>
                    
                    <div style="background-color: var(--gray-light); padding: var(--spacing-md); border-radius: var(--border-radius); margin-bottom: var(--spacing-lg);">
                        <strong><i class="fas fa-info-circle"></i> Information de contact</strong>
                        <p>Pour toute information concernant ce signalement, contactez : <strong>${report.contact}</strong></p>
                    </div>
                    
                    <div style="display: flex; gap: var(--spacing-md); justify-content: flex-end;">
                        <button class="btn btn-outline" id="shareReportBtn">
                            <i class="fas fa-share-alt"></i> Partager
                        </button>
                        ${report.status !== 'found' ? `
                        <button class="btn btn-secondary" id="markAsFoundBtn" data-id="${report.id}">
                            <i class="fas fa-check"></i> Marquer comme retrouvé
                        </button>
                        ` : ''}
                    </div>
                </div>
            `;
            
            // Créer un nouveau modal pour les détails
            const detailsModal = document.createElement('div');
            detailsModal.className = 'modal';
            detailsModal.id = 'detailsModal';
            detailsModal.innerHTML = modalContent;
            
            // Ajouter le modal au body
            document.body.appendChild(detailsModal);
            
            // Ouvrir le modal
            openModal(detailsModal);
            
            // Configurer les écouteurs d'événements
            document.getElementById('closeDetailsModal').addEventListener('click', () => {
                closeModal(detailsModal);
                setTimeout(() => detailsModal.remove(), 300);
            });
            
            // Gérer le bouton "Partager"
            document.getElementById('shareReportBtn').addEventListener('click', function() {
                alert('Fonction de partage (simulation) - Le signalement serait partagé sur les réseaux sociaux');
            });
            
            // Gérer le bouton "Marquer comme retrouvé"
            const markAsFoundBtn = document.getElementById('markAsFoundBtn');
            if (markAsFoundBtn) {
                markAsFoundBtn.addEventListener('click', function() {
                    const reportId = parseInt(this.getAttribute('data-id'));
                    const reportIndex = reportsDatabase.findIndex(r => r.id === reportId);
                    
                    if (reportIndex !== -1) {
                        reportsDatabase[reportIndex].status = 'found';
                        alert('Signalement marqué comme retrouvé !');
                        closeModal(detailsModal);
                        setTimeout(() => detailsModal.remove(), 300);
                        loadReports();
                    }
                });
            }
            
            // Fermer le modal en cliquant à l'extérieur
            detailsModal.addEventListener('click', function(e) {
                if (e.target === detailsModal) {
                    closeModal(detailsModal);
                    setTimeout(() => detailsModal.remove(), 300);
                }
            });
        }
        
        // Fonction pour obtenir une image aléatoire selon le type
        function getRandomImageForType(type) {
            const images = {
                lost: [
                    'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80',
                    'https://images.unsplash.com/photo-1594736797933-d07d5d6c7c84?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80',
                    'https://images.unsplash.com/photo-1582550945154-66ea8fff47e2?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80'
                ],
                missing: [
                    'https://images.unsplash.com/photo-1551836026-d5c2c5af78e4?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80',
                    'https://images.unsplash.com/photo-1517841905240-472988babdf9?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80',
                    'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80'
                ],
                stolen: [
                    'https://images.unsplash.com/photo-1563013544-824ae1b704d3?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80',
                    'https://images.unsplash.com/photo-1586105251261-72a756497a11?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80',
                    'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80'
                ]
            };
            
            const typeImages = images[type] || images.lost;
            return typeImages[Math.floor(Math.random() * typeImages.length)];
        }
        
        // Mettre à jour les statistiques en temps réel
        function updateStats() {
            // Simuler des statistiques en temps réel
            const statsFound = document.getElementById('statsFound');
            const statsResolved = document.getElementById('statsResolved');
            const statsUsers = document.getElementById('statsUsers');
            
            // Incrémenter les statistiques périodiquement
            setInterval(() => {
                const currentFound = parseInt(statsFound.textContent.replace(/,/g, ''));
                const currentResolved = parseInt(statsResolved.textContent.replace(/,/g, ''));
                const currentUsers = parseInt(statsUsers.textContent.replace(/,/g, ''));
                
                // Ajouter un petit nombre aléatoire pour simuler la croissance
                statsFound.textContent = (currentFound + Math.floor(Math.random() * 3)).toLocaleString();
                statsResolved.textContent = (currentResolved + Math.floor(Math.random() * 2)).toLocaleString();
                statsUsers.textContent = (currentUsers + Math.floor(Math.random() * 5)).toLocaleString();
            }, 10000); // Mettre à jour toutes les 10 secondes
        }
        
        // Démarrer la mise à jour des statistiques
        updateStats();
        
        // Gestion du défilement fluide pour les ancres
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;
                
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 80,
                        behavior: 'smooth'
                    });
                }
            });
        });
