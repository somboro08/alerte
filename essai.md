<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Signalements - Objets perdus, disparitions, vols</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --danger-color: #e74c3c;
            --warning-color: #f39c12;
            --success-color: #27ae60;
            --light-color: #ecf0f1;
            --dark-color: #2c3e50;
        }
        
        body {
            background-color: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        /* Header Styles */
        header {
            background-color: var(--primary-color);
            color: white;
            padding: 20px 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .logo i {
            font-size: 2.2rem;
            color: var(--secondary-color);
        }
        
        .logo h1 {
            font-size: 1.8rem;
        }
        
        .logo span {
            color: var(--secondary-color);
        }
        
        nav ul {
            display: flex;
            list-style: none;
            gap: 25px;
        }
        
        nav a {
            color: white;
            text-decoration: none;
            font-weight: 500;
            font-size: 1.1rem;
            transition: color 0.3s;
            padding: 8px 0;
            position: relative;
        }
        
        nav a:hover {
            color: var(--secondary-color);
        }
        
        nav a.active {
            color: var(--secondary-color);
        }
        
        nav a.active::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background-color: var(--secondary-color);
        }
        
        .mobile-menu-btn {
            display: none;
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
        
        /* Hero Section */
        .hero {
            background: linear-gradient(rgba(44, 62, 80, 0.85), rgba(44, 62, 80, 0.9)), url('https://images.unsplash.com/photo-1557804506-669a67965ba0?ixlib=rb-4.0.3&auto=format&fit=crop&w=1600&q=80');
            background-size: cover;
            background-position: center;
            color: white;
            padding: 80px 0;
            text-align: center;
        }
        
        .hero h2 {
            font-size: 2.8rem;
            margin-bottom: 20px;
        }
        
        .hero p {
            font-size: 1.2rem;
            max-width: 700px;
            margin: 0 auto 30px;
        }
        
        .btn {
            display: inline-block;
            background-color: var(--secondary-color);
            color: white;
            padding: 14px 32px;
            border-radius: 4px;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1rem;
            border: none;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn:hover {
            background-color: #2980b9;
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        .btn-danger {
            background-color: var(--danger-color);
        }
        
        .btn-danger:hover {
            background-color: #c0392b;
        }
        
        .btn-warning {
            background-color: var(--warning-color);
        }
        
        .btn-warning:hover {
            background-color: #d68910;
        }
        
        /* Categories */
        .categories {
            padding: 80px 0;
        }
        
        .section-title {
            text-align: center;
            margin-bottom: 50px;
        }
        
        .section-title h2 {
            font-size: 2.2rem;
            color: var(--primary-color);
            margin-bottom: 15px;
        }
        
        .section-title p {
            color: #666;
            max-width: 700px;
            margin: 0 auto;
        }
        
        .category-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
        }
        
        .category-card {
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .category-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
        }
        
        .card-header {
            padding: 25px;
            color: white;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .lost-objects .card-header {
            background-color: var(--warning-color);
        }
        
        .missing-persons .card-header {
            background-color: var(--danger-color);
        }
        
        .stolen-items .card-header {
            background-color: var(--primary-color);
        }
        
        .card-header i {
            font-size: 2.5rem;
        }
        
        .card-header h3 {
            font-size: 1.5rem;
        }
        
        .card-body {
            padding: 25px;
        }
        
        .card-body p {
            margin-bottom: 20px;
            color: #555;
        }
        
        /* Stats Section */
        .stats {
            background-color: var(--primary-color);
            color: white;
            padding: 60px 0;
        }
        
        .stats-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 30px;
            text-align: center;
        }
        
        .stat-item {
            padding: 20px;
        }
        
        .stat-number {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 10px;
            color: var(--secondary-color);
        }
        
        .stat-text {
            font-size: 1.2rem;
        }
        
        /* Reports Section */
        .recent-reports {
            padding: 80px 0;
        }
        
        .report-filters {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }
        
        .filter-btn {
            padding: 10px 25px;
            background-color: #e0e6ed;
            border: none;
            border-radius: 30px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .filter-btn.active {
            background-color: var(--secondary-color);
            color: white;
        }
        
        .filter-btn:hover:not(.active) {
            background-color: #d1d9e6;
        }
        
        .report-cards {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 30px;
        }
        
        .report-card {
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        }
        
        .report-badge {
            display: inline-block;
            padding: 6px 15px;
            border-radius: 30px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 15px;
        }
        
        .badge-lost {
            background-color: rgba(243, 156, 18, 0.15);
            color: var(--warning-color);
        }
        
        .badge-missing {
            background-color: rgba(231, 76, 60, 0.15);
            color: var(--danger-color);
        }
        
        .badge-stolen {
            background-color: rgba(52, 152, 219, 0.15);
            color: var(--secondary-color);
        }
        
        .report-img {
            height: 200px;
            width: 100%;
            object-fit: cover;
        }
        
        .report-content {
            padding: 20px;
        }
        
        .report-content h4 {
            font-size: 1.3rem;
            margin-bottom: 10px;
            color: var(--primary-color);
        }
        
        .report-meta {
            display: flex;
            justify-content: space-between;
            color: #777;
            font-size: 0.9rem;
            margin-bottom: 15px;
        }
        
        .report-description {
            color: #555;
            margin-bottom: 20px;
        }
        
        /* Footer */
        footer {
            background-color: var(--dark-color);
            color: white;
            padding: 60px 0 30px;
        }
        
        .footer-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 40px;
            margin-bottom: 40px;
        }
        
        .footer-column h3 {
            font-size: 1.3rem;
            margin-bottom: 20px;
            color: var(--secondary-color);
        }
        
        .footer-column ul {
            list-style: none;
        }
        
        .footer-column ul li {
            margin-bottom: 12px;
        }
        
        .footer-column a {
            color: #ddd;
            text-decoration: none;
            transition: color 0.3s;
        }
        
        .footer-column a:hover {
            color: var(--secondary-color);
        }
        
        .footer-bottom {
            text-align: center;
            padding-top: 30px;
            border-top: 1px solid #444;
            color: #aaa;
            font-size: 0.9rem;
        }
        
        /* Responsive Styles */
        @media (max-width: 992px) {
            .hero h2 {
                font-size: 2.3rem;
            }
            
            .category-cards {
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            }
        }
        
        @media (max-width: 768px) {
            nav ul {
                display: none;
            }
            
            .mobile-menu-btn {
                display: block;
            }
            
            .hero {
                padding: 60px 0;
            }
            
            .hero h2 {
                font-size: 2rem;
            }
            
            .report-cards {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 576px) {
            .hero h2 {
                font-size: 1.8rem;
            }
            
            .btn {
                padding: 12px 25px;
            }
            
            .section-title h2 {
                font-size: 1.8rem;
            }
            
            .category-cards {
                grid-template-columns: 1fr;
            }
            
            .footer-content {
                grid-template-columns: 1fr;
                gap: 30px;
            }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header>
        <div class="container header-content">
            <div class="logo">
                <i class="fas fa-hands-helping"></i>
                <h1>Signal<span>Alert</span></h1>
            </div>
            
            <button class="mobile-menu-btn">
                <i class="fas fa-bars"></i>
            </button>
            
            <nav>
                <ul>
                    <li><a href="#" class="active">Accueil</a></li>
                    <li><a href="#categories">Catégories</a></li>
                    <li><a href="#reports">Signalements</a></li>
                    <li><a href="#about">À propos</a></li>
                    <li><a href="#contact">Contact</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <h2>Plateforme de signalements communautaires</h2>
            <p>Signalez et consultez les annonces d'objets perdus, personnes disparues et choses volées. Aidez-nous à retrouver ce qui a été perdu et à réunir ce qui a été séparé.</p>
            <a href="#report-form" class="btn">Faire un signalement</a>
        </div>
    </section>

    <!-- Categories Section -->
    <section id="categories" class="categories">
        <div class="container">
            <div class="section-title">
                <h2>Catégories de signalements</h2>
                <p>Notre plateforme prend en charge trois types de signalements pour couvrir différentes situations de perte ou de disparition.</p>
            </div>
            
            <div class="category-cards">
                <!-- Objets perdus -->
                <div class="category-card lost-objects">
                    <div class="card-header">
                        <i class="fas fa-key"></i>
                        <h3>Objets perdus</h3>
                    </div>
                    <div class="card-body">
                        <p>Vous avez perdu un objet personnel ? Signalez-le ici pour augmenter vos chances de le retrouver grâce à la communauté.</p>
                        <a href="#" class="btn btn-warning">Voir les annonces</a>
                    </div>
                </div>
                
                <!-- Personnes disparues -->
                <div class="category-card missing-persons">
                    <div class="card-header">
                        <i class="fas fa-user-friends"></i>
                        <h3>Personnes disparues</h3>
                    </div>
                    <div class="card-body">
                        <p>Une personne de votre entourage a disparu ? Signalez-la rapidement pour mobiliser un maximum de personnes dans les recherches.</p>
                        <a href="#" class="btn btn-danger">Voir les annonces</a>
                    </div>
                </div>
                
                <!-- Choses volées -->
                <div class="category-card stolen-items">
                    <div class="card-header">
                        <i class="fas fa-shield-alt"></i>
                        <h3>Choses volées</h3>
                    </div>
                    <div class="card-body">
                        <p>Vous avez été victime d'un vol ? Déclarez-le ici pour alerter la communauté et empêcher la revente de vos biens.</p>
                        <a href="#" class="btn">Voir les annonces</a>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Stats Section -->
    <section class="stats">
        <div class="container">
            <div class="stats-container">
                <div class="stat-item">
                    <div class="stat-number">1,247</div>
                    <div class="stat-text">Objets retrouvés</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">89</div>
                    <div class="stat-text">Personnes localisées</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">562</div>
                    <div class="stat-text">Affaires résolues</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">3,845</div>
                    <div class="stat-text">Membres actifs</div>
                </div>
            </div>
        </div>
    </section>

    <!-- Recent Reports Section -->
    <section id="reports" class="recent-reports">
        <div class="container">
            <div class="section-title">
                <h2>Signalements récents</h2>
                <p>Consultez les dernières annonces publiées par notre communauté.</p>
            </div>
            
            <div class="report-filters">
                <button class="filter-btn active" data-filter="all">Tous</button>
                <button class="filter-btn" data-filter="lost">Objets perdus</button>
                <button class="filter-btn" data-filter="missing">Personnes disparues</button>
                <button class="filter-btn" data-filter="stolen">Choses volées</button>
            </div>
            
            <div class="report-cards">
                <!-- Report 1 - Objet perdu -->
                <div class="report-card" data-category="lost">
                    <img src="https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80" alt="Montre perdue" class="report-img">
                    <div class="report-content">
                        <span class="report-badge badge-lost">Objet perdu</span>
                        <h4>Montre bracelet en or</h4>
                        <div class="report-meta">
                            <span><i class="far fa-calendar"></i> 15 juin 2023</span>
                            <span><i class="fas fa-map-marker-alt"></i> Paris 15e</span>
                        </div>
                        <p class="report-description">Montre bracelet en or perdue dans le métro ligne 6 entre Cambronne et Pasteur. Elle a une valeur sentimentale importante.</p>
                        <a href="#" class="btn">Voir les détails</a>
                    </div>
                </div>
                
                <!-- Report 2 - Personne disparue -->
                <div class="report-card" data-category="missing">
                    <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80" alt="Personne disparue" class="report-img">
                    <div class="report-content">
                        <span class="report-badge badge-missing">Personne disparue</span>
                        <h4>Marie Dubois, 72 ans</h4>
                        <div class="report-meta">
                            <span><i class="far fa-calendar"></i> 12 juin 2023</span>
                            <span><i class="fas fa-map-marker-alt"></i> Lyon 3e</span>
                        </div>
                        <p class="report-description">Marie Dubois, 72 ans, disparue depuis hier après-midi. Elle était habillée d'un manteau bleu et d'un pantalon gris. Souffre de légers troubles de la mémoire.</p>
                        <a href="#" class="btn btn-danger">Voir les détails</a>
                    </div>
                </div>
                
                <!-- Report 3 - Chose volée -->
                <div class="report-card" data-category="stolen">
                    <img src="https://images.unsplash.com/photo-1556656793-08538906a9f8?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80" alt="Vélo volé" class="report-img">
                    <div class="report-content">
                        <span class="report-badge badge-stolen">Chose volée</span>
                        <h4>Vélo de course Trek</h4>
                        <div class="report-meta">
                            <span><i class="far fa-calendar"></i> 10 juin 2023</span>
                            <span><i class="fas fa-map-marker-alt"></i> Marseille 8e</span>
                        </div>
                        <p class="report-description">Vélo de course Trek, modèle Domane SL 5, volé devant la gare Saint-Charles. Cadre rouge, selle noire, porte un autocollant "I love cycling" sur le cadre.</p>
                        <a href="#" class="btn">Voir les détails</a>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer id="contact">
        <div class="container">
            <div class="footer-content">
                <div class="footer-column">
                    <h3>SignalAlert</h3>
                    <p>Plateforme communautaire de signalements pour objets perdus, personnes disparues et choses volées.</p>
                    <p>Notre mission: aider à retrouver ce qui a été perdu et réunir ce qui a été séparé.</p>
                </div>
                
                <div class="footer-column">
                    <h3>Liens rapides</h3>
                    <ul>
                        <li><a href="#">Accueil</a></li>
                        <li><a href="#categories">Catégories</a></li>
                        <li><a href="#reports">Signalements</a></li>
                        <li><a href="#about">À propos</a></li>
                        <li><a href="#contact">Contact</a></li>
                    </ul>
                </div>
                
                <div class="footer-column">
                    <h3>Contactez-nous</h3>
                    <ul>
                        <li><i class="fas fa-map-marker-alt"></i> 123 Rue de la Solidarité, 75015 Paris</li>
                        <li><i class="fas fa-phone"></i> 01 23 45 67 89</li>
                        <li><i class="fas fa-envelope"></i> contact@signalalert.fr</li>
                    </ul>
                </div>
                
                <div class="footer-column">
                    <h3>Numéros d'urgence</h3>
                    <ul>
                        <li><strong>Police Secours:</strong> 17</li>
                        <li><strong>Pompiers:</strong> 18</li>
                        <li><strong>Urgences médicales:</strong> 15</li>
                        <li><strong>Numéro d'urgence européen:</strong> 112</li>
                        <li><strong>Enfants disparus:</strong> 116 000</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer-bottom">
                <p>&copy; 2023 SignalAlert. Tous droits réservés. | <a href="#">Politique de confidentialité</a> | <a href="#">Mentions légales</a></p>
            </div>
        </div>
    </footer>

    <script>
        // Mobile menu toggle
        document.querySelector('.mobile-menu-btn').addEventListener('click', function() {
            const nav = document.querySelector('nav ul');
            nav.style.display = nav.style.display === 'flex' ? 'none' : 'flex';
        });
        
        // Filter reports by category
        document.querySelectorAll('.filter-btn').forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                document.querySelectorAll('.filter-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                
                // Add active class to clicked button
                this.classList.add('active');
                
                const filter = this.getAttribute('data-filter');
                const reports = document.querySelectorAll('.report-card');
                
                reports.forEach(report => {
                    if (filter === 'all' || report.getAttribute('data-category') === filter) {
                        report.style.display = 'block';
                    } else {
                        report.style.display = 'none';
                    }
                });
            });
        });
        
        // Smooth scrolling for anchor links
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
                    
                    // Close mobile menu if open
                    if (window.innerWidth <= 768) {
                        document.querySelector('nav ul').style.display = 'none';
                    }
                }
            });
        });
        
        // Simple form submission simulation
        document.querySelectorAll('.btn').forEach(button => {
            if (button.textContent.includes('Faire un signalement')) {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    alert("Formulaire de signalement - Cette fonctionnalité sera bientôt disponible. En attendant, vous pouvez consulter les signalements existants.");
                });
            }
        });
    </script>
</body>
</html>