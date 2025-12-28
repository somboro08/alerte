document.addEventListener('DOMContentLoaded', function () {
    const latInput = document.getElementById('lat');
    const lngInput = document.getElementById('lng');
    const locationInput = document.getElementById('location');
    const searchBtn = document.getElementById('searchLocationBtn');

    // Définir les coordonnées initiales (Bénin ou coordonnées existantes)
    const initialLat = latInput.value || 9.3077;
    const initialLng = lngInput.value || 2.3158;
    const initialZoom = latInput.value ? 13 : 7;

    const map = L.map('location-picker-map').setView([initialLat, initialLng], initialZoom);
    let marker = null;

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Ajouter un marqueur initial s'il y a des coordonnées
    if (latInput.value && lngInput.value) {
        marker = L.marker([initialLat, initialLng], { draggable: true }).addTo(map);
        addMarkerDragEndListener(marker);
    }
    
    // Mettre à jour les champs cachés et le marqueur
    function updateMarkerAndInputs(lat, lng) {
        latInput.value = lat;
        lngInput.value = lng;

        if (marker) {
            marker.setLatLng([lat, lng]);
        } else {
            marker = L.marker([lat, lng], { draggable: true }).addTo(map);
            addMarkerDragEndListener(marker);
        }
        map.setView([lat, lng], 13);
    }

    // Gérer le clic sur la carte
    map.on('click', function (e) {
        const { lat, lng } = e.latlng;
        updateMarkerAndInputs(lat, lng);
        
        // Optionnel : Reverse geocoding pour mettre à jour le champ de texte
        fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
            .then(response => response.json())
            .then(data => {
                if (data && data.display_name) {
                    locationInput.value = data.display_name;
                }
            });
    });

    // Gérer la recherche d'adresse
    searchBtn.addEventListener('click', function () {
        const query = locationInput.value;
        if (!query) return;

        fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&countrycodes=bj`)
            .then(response => response.json())
            .then(data => {
                if (data && data.length > 0) {
                    const { lat, lon } = data[0];
                    updateMarkerAndInputs(parseFloat(lat), parseFloat(lon));
                } else {
                    alert('Adresse non trouvée. Veuillez essayer une autre recherche ou placer le marqueur manuellement.');
                }
            })
            .catch(error => {
                console.error("Erreur de géocodage:", error);
                alert("Le service de recherche d'adresse est momentanément indisponible.");
            });
    });

    // Gérer le glisser-déposer du marqueur
    function addMarkerDragEndListener(m) {
        m.on('dragend', function (event) {
            const { lat, lng } = event.target.getLatLng();
            latInput.value = lat;
            lngInput.value = lng;
        });
    }
});
