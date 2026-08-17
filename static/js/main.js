/**
 * ResQPaws AI - Main Interactive JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss bootstrap alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 6000);
    });

    // Image Upload Preview handler
    const imageInput = document.getElementById('id_image');
    const imagePreview = document.getElementById('image-preview');
    const previewContainer = document.getElementById('image-preview-container');

    if (imageInput && imagePreview && previewContainer) {
        imageInput.addEventListener('change', function(e) {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    imagePreview.src = event.target.result;
                    previewContainer.classList.remove('d-none');
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Camera capture module via HTML5 WebRTC
    const startCamBtn = document.getElementById('btn-start-camera');
    const snapBtn = document.getElementById('btn-snap-photo');
    const camVideo = document.getElementById('camera-stream');
    const camModal = document.getElementById('cameraModal');
    let streamObj = null;

    if (startCamBtn && camVideo) {
        startCamBtn.addEventListener('click', async () => {
            try {
                streamObj = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
                camVideo.srcObject = streamObj;
                camVideo.play();
            } catch (err) {
                alert('Camera access could not be established. Please upload a saved image instead: ' + err.message);
            }
        });

        if (snapBtn) {
            snapBtn.addEventListener('click', () => {
                const canvas = document.createElement('canvas');
                canvas.width = camVideo.videoWidth || 640;
                canvas.height = camVideo.videoHeight || 480;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(camVideo, 0, 0, canvas.width, canvas.height);

                canvas.toBlob((blob) => {
                    const file = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    if (imageInput) {
                        imageInput.files = dataTransfer.files;
                        imagePreview.src = canvas.toDataURL('image/jpeg');
                        previewContainer.classList.remove('d-none');
                    }
                    // Stop tracks
                    if (streamObj) {
                        streamObj.getTracks().forEach(track => track.stop());
                    }
                    const modalInstance = bootstrap.Modal.getInstance(camModal);
                    if (modalInstance) modalInstance.hide();
                }, 'image/jpeg', 0.9);
            });
        }

        if (camModal) {
            camModal.addEventListener('hidden.bs.modal', () => {
                if (streamObj) {
                    streamObj.getTracks().forEach(track => track.stop());
                }
            });
        }
    }
});
