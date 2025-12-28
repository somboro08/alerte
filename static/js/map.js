document.addEventListener('DOMContentLoaded', function () {
    // Coordonnées approximatives du Bénin pour centrer la carte
    const map = L.map('map').setView([9.3077, 2.3158], 7);

    // Ajouter une couche de tuiles OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Définir des icônes personnalisées
    const icons = {
        lost: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        }),
        missing: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        }),
        stolen: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-black.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        }),
        default: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    };

    // Récupérer les données des signalements depuis l'API
    fetch('/api/signalements/locations')
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                console.log("Aucun signalement avec des coordonnées à afficher.");
                return;
            }

            const markers = L.markerClusterGroup();

            data.forEach(signalement => {
                const icon = icons[signalement.type] || icons.default;
                const marker = L.marker([signalement.lat, signalement.lng], { icon: icon });

                marker.bindPopup(`
                    <strong>${signalement.title}</strong>
                    <br>
                    <span class="badge badge-${signalement.type}">${signalement.type}</span>
                    <br><br>
                    <a href="/signalement/${signalement.id}" class="btn btn-primary btn-sm">Voir les détails</a>
                `);

                markers.addLayer(marker);
            });

            map.addLayer(markers);
            
            // Centrer la carte sur les marqueurs
            if (markers.getBounds().isValid()) {
                map.fitBounds(markers.getBounds().pad(0.1));
            }
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des localisations:', error);
            const mapContainer = document.getElementById('map');
            mapContainer.innerHTML = '<p style="text-align:center; color:red;">Impossible de charger les données de la carte.</p>';
        });
});
