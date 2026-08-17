/**
 * ResQPaws AI - Geolocation & Leaflet Map Integration
 */

let mapInstance = null;
let currentMarker = null;

function initRescueMap(defaultLat = 28.6139, defaultLon = 77.2090, hospitalsList = []) {
    const mapElement = document.getElementById('map');
    if (!mapElement) return;

    mapInstance = L.map('map').setView([defaultLat, defaultLon], 14);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(mapInstance);

    // Custom pulse icon for injured animal
    const animalIcon = L.divIcon({
        className: 'custom-pin',
        html: '<div style="background-color:#dc2626; color:white; width:34px; height:34px; border-radius:50%; display:flex; align-items:center; justify-content:center; border:3px solid white; box-shadow:0 0 10px rgba(220,38,38,0.7);"><i class="fas fa-paw"></i></div>',
        iconSize: [34, 34],
        iconAnchor: [17, 17]
    });

    currentMarker = L.marker([defaultLat, defaultLon], {
        draggable: true,
        icon: animalIcon
    }).addTo(mapInstance);

    currentMarker.bindPopup("<b>Injured Animal Location</b><br>Drag pin to fine-tune exact spot").openPopup();

    currentMarker.on('dragend', function(e) {
        const pos = e.target.getLatLng();
        updateLocationFields(pos.lat, pos.lng);
    });

    // Plot nearby active rescue centers/hospitals
    if (hospitalsList && hospitalsList.length > 0) {
        const hospitalIcon = L.divIcon({
            className: 'hospital-pin',
            html: '<div style="background-color:#0f766e; color:white; width:30px; height:30px; border-radius:50%; display:flex; align-items:center; justify-content:center; border:2px solid white;"><i class="fas fa-hospital"></i></div>',
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });

        hospitalsList.forEach(hosp => {
            L.marker([hosp.latitude, hosp.longitude], { icon: hospitalIcon })
             .addTo(mapInstance)
             .bindPopup(`<b>${hosp.name}</b><br>${hosp.address}<br>📞 ${hosp.phone}`);
        });
    }

    // Attempt automatic GPS capture on page load
    triggerGPSLocation();
}

function updateLocationFields(lat, lon) {
    const latInput = document.getElementById('id_latitude');
    const lonInput = document.getElementById('id_longitude');
    const addrInput = document.getElementById('id_location_address');

    if (latInput) latInput.value = lat.toFixed(6);
    if (lonInput) lonInput.value = lon.toFixed(6);

    // Reverse Geocode using free OpenStreetMap Nominatim
    if (addrInput) {
        addrInput.placeholder = "Locating address details...";
        fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`)
            .then(res => res.json())
            .then(data => {
                if (data && data.display_name) {
                    addrInput.value = data.display_name;
                }
            })
            .catch(() => {
                addrInput.placeholder = "Enter street name or landmark";
            });
    }
}

function triggerGPSLocation() {
    const statusText = document.getElementById('gps-status-badge');
    if (navigator.geolocation) {
        if (statusText) {
            statusText.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Acquiring GPS...';
            statusText.className = 'badge bg-warning text-dark';
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                if (mapInstance && currentMarker) {
                    mapInstance.setView([lat, lon], 15);
                    currentMarker.setLatLng([lat, lon]);
                }
                updateLocationFields(lat, lon);

                if (statusText) {
                    statusText.innerHTML = '<i class="fas fa-check-circle me-1"></i> GPS Locked (±' + Math.round(position.coords.accuracy) + 'm)';
                    statusText.className = 'badge bg-success';
                }
            },
            (error) => {
                console.warn('Geolocation error:', error.message);
                if (statusText) {
                    statusText.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i> GPS disabled - drag map pin';
                    statusText.className = 'badge bg-secondary';
                }
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    }
}
