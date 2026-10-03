/* =========================================================
   ResQPaws Live Ambulance Tracker
   Real Backend Tracking + Satellite & Normal Map Switcher
   Resilient WebSocket + Smart Polling Fallback (Zero Zoom Errors)
   ========================================================= */

document.addEventListener('DOMContentLoaded', () => {
    console.log('[ResQPaws] Live tracker initialized.');

    if (
        typeof CASE_ID === 'undefined' ||
        typeof ANIMAL_LAT === 'undefined' ||
        typeof ANIMAL_LNG === 'undefined'
    ) {
        console.error('[ResQPaws] Tracking variables (CASE_ID, ANIMAL_LAT, ANIMAL_LNG) are missing.');
        return;
    }

    initLiveTracker();
});


/* =========================================================
   GLOBAL VARIABLES
   ========================================================= */

let trackMap = null;

let animalMarker = null;
let ambulanceMarker = null;
let routeLine = null;

let trackingInterval = null;
let socket = null;

let ambulanceAssigned = false;
let lastStatus = null;
let lastEta = null;

// WebSocket reconnect management
let wsReconnectAttempts = 0;
const MAX_WS_RECONNECT_ATTEMPTS = 3;
let isWebSocketActive = false;


/* =========================================================
   INITIALIZE TRACKER WITH SATELLITE & NORMAL MAP LAYERS
   ========================================================= */
function initLiveTracker() {

    /*
     * 1. Create Leaflet Map (Max Zoom limited to 18 to prevent missing tiles)
     */
    trackMap = L.map('liveTrackingMap', {
        zoomControl: true,
        attributionControl: true,
        maxZoom: 18
    }).setView([ANIMAL_LAT, ANIMAL_LNG], 14);


    /*
     * 2. Define Map Layers (With maxNativeZoom to prevent grey tiles)
     */
    const streetMap = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 18,
        maxNativeZoom: 18,
        attribution: '&copy; Esri &mdash; OpenStreetMap contributors'
    });

    const satelliteMap = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 18,
        maxNativeZoom: 17, // Prevents "Map data not yet available" on zoom
        attribution: '&copy; Esri &mdash; Satellite Imagery'
    });

    // Default layer (Street Map)
    streetMap.addTo(trackMap);

    // 3. Add Layer Switcher Control in Top-Right
    const baseMaps = {
        "🗺️ Normal Map": streetMap,
        "🛰️ Satellite View": satelliteMap
    };
    L.control.layers(baseMaps, null, { position: 'topright' }).addTo(trackMap);


    /*
     * 4. Animal Pin Icon & Marker
     */
    const animalIcon = L.divIcon({
        className: 'custom-pin-animal',
        html: `
            <div style="
                background:#dc2626;
                color:white;
                border-radius:50%;
                width:34px;
                height:34px;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:16px;
                border:2px solid white;
                box-shadow:0 0 10px rgba(0,0,0,0.5);
            ">
                <i class="fa-solid fa-paw"></i>
            </div>
        `,
        iconSize: [34, 34],
        iconAnchor: [17, 17]
    });

    animalMarker = L.marker([ANIMAL_LAT, ANIMAL_LNG], { icon: animalIcon })
        .addTo(trackMap)
        .bindPopup('<b>Injured Animal Location</b>');


    /*
     * 5. Invalidate map size after container renders
     */
    setTimeout(() => {
        if (trackMap) {
            trackMap.invalidateSize();
        }
    }, 300);


    /*
     * 6. Start real-time connection (WebSocket with fallback)
     */
    connectWebSocket();

    /*
     * 7. Start Polling Engine (Primary/Fallback)
     */
    startTrackingPolling();

    /*
     * 8. Immediate first fetch
     */
    fetchTrackingData();
}


/* =========================================================
   WEBSOCKET CONNECTION (WITH AUTO-FALLBACK)
   ========================================================= */

function connectWebSocket() {
    if (wsReconnectAttempts >= MAX_WS_RECONNECT_ATTEMPTS) {
        console.warn('[ResQPaws] WebSocket unavailable on current server (WSGI). Continuing with Real-time HTTP Polling.');
        return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/rescue/track/${CASE_ID}/`;

    console.log('[ResQPaws] Connecting WebSocket:', wsUrl);

    try {
        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            console.log('[ResQPaws] WebSocket connected successfully.');
            isWebSocketActive = true;
            wsReconnectAttempts = 0;
            adjustPollingInterval(15000);

            if (typeof triggerResqpawsVoice === 'function') {
                triggerResqpawsVoice('tracking_connected', {});
            }
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                processTrackingData(data);
            } catch (error) {
                console.error('[ResQPaws] Invalid WebSocket message data:', error);
            }
        };

        socket.onerror = (error) => {
            console.warn('[ResQPaws] WebSocket connection issue. Fallback polling active.');
        };

        socket.onclose = (event) => {
            isWebSocketActive = false;
            wsReconnectAttempts++;
            adjustPollingInterval(4000);

            if (wsReconnectAttempts < MAX_WS_RECONNECT_ATTEMPTS) {
                console.log(`[ResQPaws] Retrying WebSocket connection (${wsReconnectAttempts}/${MAX_WS_RECONNECT_ATTEMPTS}) in 5s...`);
                setTimeout(connectWebSocket, 5000);
            } else {
                console.log('[ResQPaws] Switched to Full-Time Real-Time Polling Mode (every 4s).');
            }
        };

    } catch (error) {
        console.warn('[ResQPaws] WebSocket not supported or failed to initialize:', error);
        isWebSocketActive = false;
        adjustPollingInterval(4000);
    }
}


/* =========================================================
   REST POLLING ENGINE
   ========================================================= */

function startTrackingPolling(intervalMs = 4000) {
    if (trackingInterval) {
        clearInterval(trackingInterval);
    }

    trackingInterval = setInterval(() => {
        fetchTrackingData();
    }, intervalMs);

    console.log(`[ResQPaws] Live tracking polling running (every ${intervalMs / 1000}s).`);
}

function adjustPollingInterval(newIntervalMs) {
    startTrackingPolling(newIntervalMs);
}


/* =========================================================
   FETCH TRACKING DATA (HTTP REST)
   ========================================================= */

async function fetchTrackingData() {
    try {
        const response = await fetch(`/api/tracking/${CASE_ID}/`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            },
            cache: 'no-store'
        });

        if (!response.ok) {
            console.warn('[ResQPaws] Tracking API response:', response.status);
            return;
        }

        const data = await response.json();
        console.log('[ResQPaws] Tracking update:', data);

        processTrackingData(data);

    } catch (error) {
        console.debug('[ResQPaws] Tracking polling check:', error);
    }
}


/* =========================================================
   PROCESS TRACKING DATA & UI UPDATES
   ========================================================= */

function processTrackingData(data) {
    if (!data) return;

    if (data.type === 'connection') {
        console.log('[ResQPaws] WebSocket connection confirmed.');
        return;
    }

    syncPageUI(data);

    const assigned = data.ambulance_assigned === true;

    /*
     * 1. STATUS CHANGE
     */
    if (data.status && data.status !== lastStatus) {
        const previousStatus = lastStatus;
        lastStatus = data.status;
        handleStatusChange(data.status, previousStatus, data);
    }

    /*
     * 2. AMBULANCE ASSIGNMENT
     */
    if (assigned && !ambulanceAssigned) {
        ambulanceAssigned = true;
        console.log('[ResQPaws] Ambulance officially assigned.');

        createAmbulanceMarker(data);

        if (typeof triggerResqpawsVoice === 'function') {
            triggerResqpawsVoice('ambulance_assigned', {
                ambulance: data.ambulance_number || data.driver_name || 'Rescue ambulance',
                driver: data.driver_name || 'Rescue driver',
                eta: data.eta_minutes
            });
        }
    }

    /*
     * 3. UPDATE AMBULANCE GPS POSITION
     */
    if (assigned && data.ambulance_lat != null && data.ambulance_lng != null) {
        updateAmbulancePosition(
            Number(data.ambulance_lat),
            Number(data.ambulance_lng),
            data
        );
    }

    /*
     * 4. AMBULANCE UNASSIGNED / WAITING
     */
    if (!assigned) {
        ambulanceAssigned = false;
        removeAmbulanceMarker();
        showWaitingForAmbulance();
    }

    /*
     * 5. ETA UPDATES & VOICE NOTIFICATIONS
     */
    if (data.eta_minutes != null) {
        const eta = Number(data.eta_minutes);

        if (lastEta === null || Math.abs(eta - lastEta) >= 2) {
            if (lastEta !== null && typeof triggerResqpawsVoice === 'function') {
                triggerResqpawsVoice('ambulance_distance_update', { eta: eta });
            }
            lastEta = eta;
        }
    }
}


/* =========================================================
   SYNC ON-PAGE UI ELEMENTS
   ========================================================= */

function syncPageUI(data) {
    const statusTextEl = document.getElementById('live-status-text') || document.getElementById('liveStatusText');
    if (statusTextEl && (data.status_display || data.status)) {
        statusTextEl.innerText = data.status_display || data.status;
    }

    const etaEl = document.getElementById('ambulanceEta') || document.getElementById('etaMinutes');
    if (etaEl && data.eta_minutes != null) {
        etaEl.innerText = `${data.eta_minutes} mins`;
    }

    const driverEl = document.getElementById('driverName');
    if (driverEl && data.driver_name) {
        driverEl.innerText = data.driver_name;
    }

    const vehicleEl = document.getElementById('vehicleNumber');
    if (vehicleEl && data.ambulance_number) {
        vehicleEl.innerText = data.ambulance_number;
    }
}


/* =========================================================
   CREATE AMBULANCE MARKER
   ========================================================= */

function createAmbulanceMarker(data) {
    if (ambulanceMarker) return;

    const lat = Number(data.ambulance_lat);
    const lng = Number(data.ambulance_lng);

    if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
        console.warn('[ResQPaws] Ambulance assigned but GPS location coordinates are pending.');
        return;
    }

    const ambIcon = L.divIcon({
        className: 'custom-pin-amb',
        html: `
            <div style="
                background:#2563eb;
                color:white;
                border-radius:50%;
                width:38px;
                height:38px;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:18px;
                border:2px solid white;
                box-shadow:0 0 14px rgba(37,99,235,0.8);
            ">
                <i class="fa-solid fa-truck-medical"></i>
            </div>
        `,
        iconSize: [38, 38],
        iconAnchor: [19, 19]
    });

    ambulanceMarker = L.marker([lat, lng], { icon: ambIcon })
        .addTo(trackMap)
        .bindPopup(`<b>Ambulance Rescue Team</b><br>Driver: ${data.driver_name || 'En Route'}`);

    drawRoute(lat, lng);
    fitTrackingMap(lat, lng);

    console.log('[ResQPaws] Ambulance marker created on map.');
}


/* =========================================================
   UPDATE AMBULANCE POSITION
   ========================================================= */

function updateAmbulancePosition(lat, lng, data) {
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;

    if (!ambulanceMarker) {
        createAmbulanceMarker({
            ...data,
            ambulance_lat: lat,
            ambulance_lng: lng
        });
        return;
    }

    ambulanceMarker.setLatLng([lat, lng]);
    drawRoute(lat, lng);
}


/* =========================================================
   DRAW ROUTE
   ========================================================= */

function drawRoute(ambulanceLat, ambulanceLng) {
    const points = [
        [ambulanceLat, ambulanceLng],
        [ANIMAL_LAT, ANIMAL_LNG]
    ];

    if (routeLine) {
        routeLine.setLatLngs(points);
    } else {
        routeLine = L.polyline(points, {
            color: '#2563eb',
            weight: 4,
            dashArray: '6, 8',
            opacity: 0.8
        }).addTo(trackMap);
    }
}


/* =========================================================
   FIT MAP
   ========================================================= */

function fitTrackingMap(ambulanceLat, ambulanceLng) {
    if (!trackMap) return;

    const bounds = L.latLngBounds([
        [ANIMAL_LAT, ANIMAL_LNG],
        [ambulanceLat, ambulanceLng]
    ]);

    trackMap.fitBounds(bounds, { padding: [50, 50] });
}


/* =========================================================
   REMOVE AMBULANCE MARKER
   ========================================================= */

function removeAmbulanceMarker() {
    if (ambulanceMarker && trackMap) {
        trackMap.removeLayer(ambulanceMarker);
        ambulanceMarker = null;
    }

    if (routeLine && trackMap) {
        trackMap.removeLayer(routeLine);
        routeLine = null;
    }
}


/* =========================================================
   WAITING STATE
   ========================================================= */

function showWaitingForAmbulance() {
    console.log('[ResQPaws] Waiting for official ambulance assignment.');
}


/* =========================================================
   STATUS CHANGE HANDLER & VOICE EVENTS
   ========================================================= */

function handleStatusChange(status, previousStatus, data) {
    console.log('[ResQPaws] Status updated:', previousStatus, '→', status);

    if (status === 'DISPATCHED') {
        if (typeof triggerResqpawsVoice === 'function') {
            triggerResqpawsVoice('ambulance_en_route', { eta: data.eta_minutes });
        }
    } else if (status === 'ADMITTED') {
        if (typeof triggerResqpawsVoice === 'function') {
            triggerResqpawsVoice('hospital_transfer', { hospital: data.hospital_name || 'the assigned hospital' });
        }
    } else if (status === 'RESOLVED') {
        if (typeof triggerResqpawsVoice === 'function') {
            triggerResqpawsVoice('case_resolved', {});
        }
    } else if (status === 'CANCELLED') {
        if (typeof triggerResqpawsVoice === 'function') {
            triggerResqpawsVoice('case_cancelled', {});
        }
    }
}


/* =========================================================
   CLEANUP ON PAGE EXIT
   ========================================================= */

window.addEventListener('beforeunload', () => {
    if (trackingInterval) {
        clearInterval(trackingInterval);
    }
    if (socket) {
        socket.close();
    }
});