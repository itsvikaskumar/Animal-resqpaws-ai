/* =========================================================
   ResQPaws AI Emergency Scan + GPS + Front/Back Camera + Voice
   ========================================================= */

let map, marker;

let currentLat = 30.3165;
let currentLng = 78.0322;

let selectedFile = null;
let nearestFacilityName = null;

// Camera stream & lens tracker ('environment' = Back Camera, 'user' = Front Camera)
let cameraStream = null;
let currentCameraMode = 'environment';


/* =========================================================
   PAGE INITIALIZATION
   ========================================================= */

document.addEventListener('DOMContentLoaded', () => {

    initReportMap();

    // Voice announcement for reporting process
    if (typeof triggerResqpawsVoice === 'function') {
        triggerResqpawsVoice('report_started', {});
    }

    getUserGPSLocation();

    // Turn off camera when modal is closed
    const cameraModalEl = document.getElementById('cameraModal');
    if (cameraModalEl) {
        cameraModalEl.addEventListener('hidden.bs.modal', stopInjuredAnimalCamera);
    }
});


/* =========================================================
   MAP INITIALIZATION
   ========================================================= */

function initReportMap() {

    const mapElement = document.getElementById('reportMap');
    if (!mapElement) return;

    map = L.map('reportMap').setView([currentLat, currentLng], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    marker = L.marker([currentLat, currentLng], { draggable: true }).addTo(map);

    marker.on('dragend', (e) => {
        const pos = e.target.getLatLng();
        setCoordinates(pos.lat, pos.lng, true);
    });
}


/* =========================================================
   SET GPS COORDINATES
   ========================================================= */

function setCoordinates(lat, lng, announce = false) {

    currentLat = lat;
    currentLng = lng;

    const latInput = document.getElementById('formLat');
    const lngInput = document.getElementById('formLng');
    if (latInput) latInput.value = lat;
    if (lngInput) lngInput.value = lng;

    if (announce && typeof triggerResqpawsVoice === 'function') {
        triggerResqpawsVoice('location_detected', {
            latitude: lat,
            longitude: lng
        });
    }

    fetchNearestShelter(lat, lng);
}


/* =========================================================
   GET USER GPS LOCATION
   ========================================================= */

function getUserGPSLocation() {

    if (!navigator.geolocation) {
        console.warn('Geolocation is not supported by this browser.');
        if (typeof triggerResqpawsVoice === 'function') {
            triggerResqpawsVoice('location_detected', { fallback: true });
        }
        fetchNearestShelter(currentLat, currentLng);
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;

            currentLat = lat;
            currentLng = lng;

            if (map) map.setView([lat, lng], 15);
            if (marker) marker.setLatLng([lat, lng]);

            const latInput = document.getElementById('formLat');
            const lngInput = document.getElementById('formLng');
            if (latInput) latInput.value = lat;
            if (lngInput) lngInput.value = lng;

            if (typeof triggerResqpawsVoice === 'function') {
                triggerResqpawsVoice('location_detected', {
                    latitude: lat,
                    longitude: lng
                });
            }

            fetchNearestShelter(lat, lng);
        },
        (err) => {
            console.warn('GPS unavailable:', err.message);
            fetchNearestShelter(currentLat, currentLng);
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 }
    );
}


/* =========================================================
   FIND NEAREST RESCUE FACILITY
   ========================================================= */

async function fetchNearestShelter(lat, lng) {

    try {
        if (typeof triggerResqpawsVoice === 'function') {
            triggerResqpawsVoice('searching_rescue_center', {});
        }

        const res = await fetch(`/api/find-nearest-shelter/?lat=${lat}&lng=${lng}`);
        const data = await res.json();

        if (data.success && data.nearest) {
            const n = data.nearest;
            nearestFacilityName = n.name;

            const nameEl = document.getElementById('shelterName');
            const distEl = document.getElementById('shelterDist');
            const btnEl = document.getElementById('shelterActionButtons');

            if (nameEl) nameEl.innerText = n.name;
            if (distEl) distEl.innerText = `${n.distance_km} km away | ${n.address}`;

            const phone = n.phone || '';
            const whatsapp = n.whatsapp || '';

            if (btnEl) {
                btnEl.innerHTML = `
                    ${whatsapp ? `<a href="https://wa.me/${whatsapp.replace(/\D/g, '')}" target="_blank" rel="noopener" class="btn btn-sm btn-success"><i class="fa-brands fa-whatsapp"></i></a>` : ''}
                    ${phone ? `<a href="tel:${phone}" class="btn btn-sm btn-outline-dark"><i class="fa-solid fa-phone"></i></a>` : ''}
                `;
            }

            if (typeof triggerResqpawsVoice === 'function') {
                triggerResqpawsVoice('rescue_center_found', {
                    name: n.name,
                    distance_km: n.distance_km,
                    address: n.address
                });
            }
        } else {
            const nameEl = document.getElementById('shelterName');
            const distEl = document.getElementById('shelterDist');
            if (nameEl) nameEl.innerText = 'No nearby rescue center found';
            if (distEl) distEl.innerText = 'Please continue with the emergency report.';
        }
    } catch (e) {
        console.error('Nearest facility error:', e);
        const nameEl = document.getElementById('shelterName');
        if (nameEl) nameEl.innerText = 'Unable to locate rescue center';
    }
}


/* =========================================================
   FRONT & BACK CAMERA ENGINE FOR INJURED ANIMALS
   ========================================================= */

/**
 * Starts or switches the camera lens
 * @param {'environment' | 'user'} mode - 'environment' for Back Camera, 'user' for Front Camera
 */
async function openInjuredAnimalCamera(mode = 'environment') {
    try {
        currentCameraMode = mode;

        // Stop existing stream if any
        if (cameraStream) {
            cameraStream.getTracks().forEach(track => track.stop());
            cameraStream = null;
        }

        const video = document.getElementById('cameraStream');
        if (!video) {
            alert('Camera display element not found.');
            return;
        }

        // Request chosen camera lens
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: { ideal: currentCameraMode },
                width: { ideal: 1280 },
                height: { ideal: 720 }
            },
            audio: false
        });

        video.srcObject = cameraStream;
        await video.play();

        // Update active camera badge
        const badge = document.getElementById('activeCameraBadge');
        if (badge) {
            badge.innerText = currentCameraMode === 'environment' ? 'Back Camera (Animal)' : 'Front Camera (Selfie)';
            badge.className = currentCameraMode === 'environment' ? 'badge bg-warning text-dark' : 'badge bg-info text-dark';
        }

        // Show Modal
        const modalEl = document.getElementById('cameraModal');
        if (modalEl && window.bootstrap) {
            const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
            modal.show();
        }

    } catch (err) {
        console.error('Camera access error:', err);
        alert('Could not access ' + (mode === 'environment' ? 'Back Camera' : 'Front Camera') + '. Please check camera permissions.');
    }
}

/**
 * Toggle / Flip camera between front and rear lenses
 */
function toggleCameraFacingMode() {
    currentCameraMode = currentCameraMode === 'environment' ? 'user' : 'environment';
    openInjuredAnimalCamera(currentCameraMode);
}

/**
 * Stop camera stream completely
 */
function stopInjuredAnimalCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }
    const video = document.getElementById('cameraStream');
    if (video) video.srcObject = null;
}

/**
 * Capture photo from live camera, create File, update preview, and show AI Scan button
 */
function captureInjuredAnimalPhoto() {
    const video = document.getElementById('cameraStream');
    if (!video || !cameraStream) {
        alert('Camera stream is not active.');
        return;
    }

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const ctx = canvas.getContext('2d');

    // Mirror image if front camera is used
    if (currentCameraMode === 'user') {
        ctx.translate(canvas.width, 0);
        ctx.scale(-1, 1);
    }

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
        if (!blob) {
            alert('Failed to capture photo.');
            return;
        }

        const fileName = `injured_animal_${currentCameraMode}_${Date.now()}.jpg`;
        selectedFile = new File([blob], fileName, { type: 'image/jpeg' });

        // Update preview image
        const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
        const imagePreview = document.getElementById('imagePreview');
        if (imagePreview) imagePreview.src = dataUrl;

        // Toggle UI containers
        const dropzone = document.getElementById('dropzonePlaceholder');
        if (dropzone) dropzone.classList.add('d-none');

        const previewContainer = document.getElementById('previewContainer');
        if (previewContainer) previewContainer.classList.remove('d-none');

        const btnScanAI = document.getElementById('btnScanAI');
        if (btnScanAI) btnScanAI.classList.remove('d-none');

        const aiResultCard = document.getElementById('aiResultCard');
        if (aiResultCard) aiResultCard.classList.add('d-none');

        // Close camera modal
        const modalEl = document.getElementById('cameraModal');
        if (modalEl && window.bootstrap) {
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
        }

        stopInjuredAnimalCamera();

        if (typeof triggerResqpawsVoice === 'function') {
            triggerResqpawsVoice('image_selected', { fileName: fileName });
        }
    }, 'image/jpeg', 0.9);
}


/* =========================================================
   FILE PICKER IMAGE SELECTION
   ========================================================= */

function handleImageSelected(input) {

    if (input.files && input.files[0]) {
        selectedFile = input.files[0];

        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.getElementById('imagePreview');
            if (preview) preview.src = e.target.result;

            const dropzone = document.getElementById('dropzonePlaceholder');
            if (dropzone) dropzone.classList.add('d-none');

            const previewContainer = document.getElementById('previewContainer');
            if (previewContainer) previewContainer.classList.remove('d-none');

            const btnScan = document.getElementById('btnScanAI');
            if (btnScan) btnScan.classList.remove('d-none');

            const aiResultCard = document.getElementById('aiResultCard');
            if (aiResultCard) aiResultCard.classList.add('d-none');

            if (typeof triggerResqpawsVoice === 'function') {
                triggerResqpawsVoice('image_selected', { fileName: selectedFile.name });
            }
        };

        reader.readAsDataURL(selectedFile);
    }
}


/* =========================================================
   RESET IMAGE
   ========================================================= */

function resetImageUpload() {

    selectedFile = null;

    const input = document.getElementById('imageInput');
    if (input) input.value = '';

    const dropzone = document.getElementById('dropzonePlaceholder');
    if (dropzone) dropzone.classList.remove('d-none');

    const previewContainer = document.getElementById('previewContainer');
    if (previewContainer) previewContainer.classList.add('d-none');

    const btnScan = document.getElementById('btnScanAI');
    if (btnScan) btnScan.classList.add('d-none');

    const aiResultCard = document.getElementById('aiResultCard');
    if (aiResultCard) aiResultCard.classList.add('d-none');
}


/* =========================================================
   RUN AI IMAGE SCAN
   ========================================================= */

async function runAIScan() {

    if (!selectedFile) {
        alert('Please snap or select an animal photo first.');
        return;
    }

    const btn = document.getElementById('btnScanAI');
    const loader = document.getElementById('scanLoading');

    if (btn) btn.classList.add('d-none');
    if (loader) loader.classList.remove('d-none');

    if (typeof triggerResqpawsVoice === 'function') {
        triggerResqpawsVoice('image_analysis_started', {});
    }

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
        const res = await fetch('/api/analyze-image/', {
            method: 'POST',
            body: formData
        });

        const data = await res.json();
        if (loader) loader.classList.add('d-none');

        if (data.success) {
            const aiCard = document.getElementById('aiResultCard');
            if (aiCard) aiCard.classList.remove('d-none');

            const animalEl = document.getElementById('resAnimal');
            if (animalEl) animalEl.innerText = data.animal_type || 'Unknown';

            const injuriesEl = document.getElementById('resInjuries');
            if (injuriesEl) {
                injuriesEl.innerText = Array.isArray(data.injuries)
                    ? data.injuries.join(', ')
                    : (data.injuries || 'No visible condition detected');
            }

            const sevTextEl = document.getElementById('resSeverityText');
            if (sevTextEl) {
                sevTextEl.innerText = data.severity_text || data.severity_code || 'Unknown';
            }

            const firstAidEl = document.getElementById('resFirstAid');
            if (firstAidEl) {
                firstAidEl.innerText = data.first_aid_guidance || 'Please wait for professional animal rescue assistance.';
            }

            const badge = document.getElementById('severityBadge');
            if (badge) {
                badge.innerText = data.severity_code || 'UNKNOWN';
                badge.className = data.severity_code === 'CRITICAL'
                    ? 'badge bg-danger px-3 py-1'
                    : 'badge bg-warning text-dark px-3 py-1';
            }

            if (data.processed_image_url) {
                const imgPrev = document.getElementById('imagePreview');
                if (imgPrev) imgPrev.src = data.processed_image_url;
            }

            // Sync hidden inputs
            const fAnimal = document.getElementById('formAnimal');
            const fInjuries = document.getElementById('formInjuries');
            const fSeverity = document.getElementById('formSeverity');
            const fFirstAid = document.getElementById('formFirstAid');
            const fIsAnimal = document.getElementById('formIsAnimal');

            if (fIsAnimal) fIsAnimal.value = data.is_animal ? 'true' : 'false';
            if (fAnimal) fAnimal.value = data.animal_type || 'Unknown';
            if (fInjuries) fInjuries.value = Array.isArray(data.injuries) ? data.injuries.join(', ') : (data.injuries || 'None detected');
            if (fSeverity) fSeverity.value = data.severity_code || 'UNKNOWN';
            if (fFirstAid) fFirstAid.value = data.first_aid_guidance || '';

            if (typeof triggerResqpawsVoice === 'function') {
                if (!data.is_animal) {
                    triggerResqpawsVoice('animal_not_confirmed', {});
                } else {
                    triggerResqpawsVoice('image_analyzed', {
                        animal: data.animal_type,
                        severity: data.severity_code,
                        injuries: Array.isArray(data.injuries) ? data.injuries.join(', ') : data.injuries
                    });
                }
            }
        } else {
            alert('Scan error: ' + (data.error || 'Unable to analyze image.'));
            if (btn) btn.classList.remove('d-none');
        }
    } catch (e) {
        console.error('AI scan error:', e);
        if (loader) loader.classList.add('d-none');
        if (btn) btn.classList.remove('d-none');
        alert('Server connection error.');
    }
}


/* =========================================================
   SUBMIT EMERGENCY REPORT
   ========================================================= */

async function submitEmergencyReport(e) {

    e.preventDefault();

    const form = document.getElementById('emergencyReportForm');
    const submitBtn = document.getElementById('btnSubmitReport');

    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span> Submitting Emergency Report...`;

    if (typeof triggerResqpawsVoice === 'function') {
        triggerResqpawsVoice('report_submitting', {});
    }

    const formData = new FormData(form);

    if (selectedFile) {
        formData.append('image', selectedFile);
    }

    try {
        const res = await fetch('/api/submit-emergency/', {
            method: 'POST',
            body: formData
        });

        const data = await res.json();

        if (data.success) {
            if (typeof setResqpawsReportId === 'function') {
                setResqpawsReportId(data.report_id);
            }

            if (typeof triggerResqpawsVoice === 'function') {
                triggerResqpawsVoice('report_submitted', {
                    reportId: data.short_id || data.report_id,
                    status: data.status,
                    hospital: data.hospital_name || nearestFacilityName,
                    ambulanceAssigned: data.ambulance_assigned === true
                });
            }

            window.location.href = `/track-report/?report_id=${encodeURIComponent(data.short_id || data.report_id)}`;
        } else {
            alert('Error: ' + (data.error || 'Unable to submit emergency report.'));
            submitBtn.disabled = false;
            submitBtn.innerHTML = `<i class="fa-solid fa-truck-medical me-2"></i> SUBMIT & DISPATCH AMBULANCE`;
        }
    } catch (err) {
        console.error('Emergency submission error:', err);
        alert('Failed to submit emergency report.');
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa-solid fa-truck-medical me-2"></i> SUBMIT & DISPATCH AMBULANCE`;
    }
}