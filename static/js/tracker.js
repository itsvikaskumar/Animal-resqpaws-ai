/**
 * ResQPaws AI - Live Rescue Status Tracker & Map Simulator
 */

function initLiveTracking(animalLat, animalLon, hospitalLat, hospitalLon, ambulanceLat, ambulanceLon, trackingId) {
    const trackMapEl = document.getElementById('tracking-map');
    if (!trackMapEl) return;

    const trackMap = L.map('tracking-map').setView([animalLat, animalLon], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap'
    }).addTo(trackMap);

    // Animal Marker
    const animalMarker = L.marker([animalLat, animalLon], {
        icon: L.divIcon({
            className: 'animal-marker',
            html: '<div style="background:#dc2626; color:white; width:34px; height:34px; border-radius:50%; display:flex; align-items:center; justify-content:center; border:2px solid white; box-shadow:0 0 8px rgba(0,0,0,0.4);"><i class="fas fa-paw"></i></div>',
            iconSize: [34, 34],
            iconAnchor: [17, 17]
        })
    }).addTo(trackMap).bindPopup("<b>Injured Animal Location</b>");

    // Hospital Marker
    if (hospitalLat && hospitalLon) {
        L.marker([hospitalLat, hospitalLon], {
            icon: L.divIcon({
                className: 'hosp-marker',
                html: '<div style="background:#0f766e; color:white; width:34px; height:34px; border-radius:50%; display:flex; align-items:center; justify-content:center; border:2px solid white; box-shadow:0 0 8px rgba(0,0,0,0.4);"><i class="fas fa-hospital"></i></div>',
                iconSize: [34, 34],
                iconAnchor: [17, 17]
            })
        }).addTo(trackMap).bindPopup("<b>Assigned Animal Hospital Base</b>");
    }

    // Ambulance Marker
    let ambMarker = null;
    if (ambulanceLat && ambulanceLon) {
        ambMarker = L.marker([ambulanceLat, ambulanceLon], {
            icon: L.divIcon({
                className: 'amb-marker',
                html: '<div style="background:#d97706; color:white; width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center; border:2px solid white; box-shadow:0 0 12px rgba(217,119,6,0.8);"><i class="fas fa-ambulance fa-beat"></i></div>',
                iconSize: [36, 36],
                iconAnchor: [18, 18]
            })
        }).addTo(trackMap).bindPopup("<b>Ambulance En Route</b>");

        // Fit bounds to show both
        const group = new L.featureGroup([animalMarker, ambMarker]);
        trackMap.fitBounds(group.getBounds().pad(0.2));
    }

    // Real-time Status Polling
    if (trackingId) {
        setInterval(() => {
            fetch(`/rescue/api/track/${trackingId}/`)
                .then(res => res.json())
                .then(data => {
                    const statusText = document.getElementById('live-status-text');
                    if (statusText && data.status_display) {
                        statusText.innerText = data.status_display;
                    }
                })
                .catch(err => console.debug('Polling check:', err));
        }, 12000);
    }
}
