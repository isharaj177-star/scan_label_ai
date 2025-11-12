// API Configuration
const API_BASE_URL = 'http://localhost:8001';

// DOM Elements
const barcodeInput = document.getElementById('barcodeInput');
const scanButton = document.getElementById('scanButton');
const loadingIndicator = document.getElementById('loadingIndicator');
const errorMessage = document.getElementById('errorMessage');
const resultCard = document.getElementById('resultCard');
const quickButtons = document.querySelectorAll('.quick-btn');
const tabButtons = document.querySelectorAll('.tab-btn');
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const uploadPreview = document.getElementById('uploadPreview');
const foodFileInput = document.getElementById('foodFileInput');
const foodUploadArea = document.getElementById('foodUploadArea');
const foodPreview = document.getElementById('foodPreview');
const startCameraBtn = document.getElementById('startCameraBtn');
const stopCameraBtn = document.getElementById('stopCameraBtn');
const cameraPreview = document.getElementById('cameraPreview');
const startFoodCameraBtn = document.getElementById('startFoodCameraBtn');
const stopFoodCameraBtn = document.getElementById('stopFoodCameraBtn');
const foodCameraPreview = document.getElementById('foodCameraPreview');
const foodVideo = document.getElementById('foodVideo');
const captureFoodBtn = document.getElementById('captureFoodBtn');

// State
let stream = null;
let scanning = false;
let lastScannedCode = null;
let scanConfidence = 0;
let quaggaInitialized = false;
let scanAttempts = 0;
const MAX_SCAN_ATTEMPTS = 5;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Tab switching
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.getAttribute('data-tab');
            switchTab(tab);
        });
    });

    // Manual input
    barcodeInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            scanProduct();
        }
    });
    scanButton.addEventListener('click', scanProduct);

    // Quick buttons
    quickButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const barcode = btn.getAttribute('data-barcode');
            barcodeInput.value = barcode;
            scanProduct();
        });
    });

    // File upload
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#007AFF';
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = '';
    });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '';
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    // Camera
    startCameraBtn.addEventListener('click', startCamera);
    stopCameraBtn.addEventListener('click', stopCamera);

    // Food image upload
    foodUploadArea.addEventListener('click', () => foodFileInput.click());
    foodUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        foodUploadArea.style.borderColor = '#007AFF';
    });
    foodUploadArea.addEventListener('dragleave', () => {
        foodUploadArea.style.borderColor = '';
    });
    foodUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        foodUploadArea.style.borderColor = '';
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFoodFile(files[0]);
        }
    });
    foodFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFoodFile(e.target.files[0]);
        }
    });

    // Food camera
    startFoodCameraBtn.addEventListener('click', startFoodCamera);
    stopFoodCameraBtn.addEventListener('click', stopFoodCamera);
    captureFoodBtn.addEventListener('click', captureFoodPhoto);
});

// Tab switching
function switchTab(tabName) {
    // Stop food camera if switching away from food tab
    if (tabName !== 'food' && foodStream) {
        stopFoodCamera();
    }
    
    // Update buttons
    tabButtons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-tab') === tabName) {
            btn.classList.add('active');
        }
    });

    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}Tab`).classList.add('active');

    // Stop camera if switching away
    if (tabName !== 'camera') {
        stopCamera();
    }
}

// Start camera
async function startCamera() {
    try {
        // Request higher quality camera
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'environment',
                width: { ideal: 1920, min: 1280 },
                height: { ideal: 1080, min: 720 },
                focusMode: 'continuous',
                exposureMode: 'continuous'
            }
        });

        const video = document.createElement('video');
        video.srcObject = stream;
        video.setAttribute('autoplay', '');
        video.setAttribute('playsinline', '');
        video.setAttribute('muted', '');
        cameraPreview.innerHTML = '';
        cameraPreview.appendChild(video);

        startCameraBtn.classList.add('hidden');
        stopCameraBtn.classList.remove('hidden');

        // Wait for video to be ready
        video.addEventListener('loadedmetadata', () => {
            // Initialize Quagga for live scanning
            initializeQuagga();
        });

        // Start scanning
        scanning = true;
        lastScannedCode = null;
        scanConfidence = 0;
        scanAttempts = 0;
        
        // Show scanning indicator
        const indicator = document.getElementById('scanningIndicator');
        if (indicator) {
            indicator.classList.remove('hidden');
        }
    } catch (error) {
        showError('Camera access denied. Please allow camera access and try again.');
        console.error('Camera error:', error);
    }
}

// Initialize Quagga for better barcode detection
function initializeQuagga() {
    if (quaggaInitialized) return;
    
    // Use manual scanning approach with improved Quagga settings
    // This is more reliable than LiveStream mode
    scanBarcodeFromCamera();
}

// Validate EAN-13 checksum (professional-grade validation)
function validateEAN13Checksum(code) {
    if (code.length !== 13) return false;
    
    const digits = code.split('').map(Number);
    let sum = 0;
    
    for (let i = 0; i < 12; i++) {
        sum += digits[i] * (i % 2 === 0 ? 1 : 3);
    }
    
    const checkDigit = (10 - (sum % 10)) % 10;
    return checkDigit === digits[12];
}

// Validate EAN-8 checksum
function validateEAN8Checksum(code) {
    if (code.length !== 8) return false;
    
    const digits = code.split('').map(Number);
    let sum = 0;
    
    for (let i = 0; i < 7; i++) {
        sum += digits[i] * (i % 2 === 0 ? 3 : 1);
    }
    
    const checkDigit = (10 - (sum % 10)) % 10;
    return checkDigit === digits[7];
}

// Professional barcode validation
function validateBarcode(code) {
    code = code.replace(/\D/g, '').trim();
    
    if (!/^\d{8,13}$/.test(code)) {
        return { valid: false, reason: 'Invalid format' };
    }
    
    // Validate checksums for standard formats
    if (code.length === 13) {
        if (!validateEAN13Checksum(code)) {
            return { valid: false, reason: 'Invalid EAN-13 checksum' };
        }
        return { valid: true, format: 'EAN-13' };
    }
    
    if (code.length === 8) {
        if (!validateEAN8Checksum(code)) {
            return { valid: false, reason: 'Invalid EAN-8 checksum' };
        }
        return { valid: true, format: 'EAN-8' };
    }
    
    // UPC-A (12 digits) - same checksum as EAN-13
    if (code.length === 12) {
        const ean13 = '0' + code;
        if (validateEAN13Checksum(ean13)) {
            return { valid: true, format: 'UPC-A' };
        }
    }
    
    // For other lengths, accept if format is correct
    return { valid: true, format: 'Other' };
}

// Handle detected barcode with professional-grade validation
function handleBarcodeDetected(code, codeResult) {
    if (!code || !scanning) return;
    
    // Clean the code - remove all non-numeric characters
    code = code.replace(/\D/g, '').trim();
    
    // Professional validation with checksum
    const validation = validateBarcode(code);
    if (!validation.valid) {
        console.log('Invalid barcode:', code, validation.reason);
        return;
    }
    
    // Prefer validated 13-digit EAN-13 codes (most common for products)
    // Require higher confidence for shorter codes (might be partial scans)
    const requiredConfidence = code.length === 13 ? 2 : code.length === 8 ? 3 : 4;
    
    // Check if same code detected multiple times (confidence check)
    if (lastScannedCode === code) {
        scanConfidence++;
        if (scanConfidence >= requiredConfidence) {
            stopCamera();
            barcodeInput.value = code;
            switchTab('manual');
            
            // Show confirmation message
            showBarcodeConfirmation(code, validation.format);
            
            // Auto-scan after a brief delay
            setTimeout(() => {
                scanProduct();
            }, 500);
        }
    } else {
        lastScannedCode = code;
        scanConfidence = 1;
    }
}

// Show barcode confirmation with edit option
function showBarcodeConfirmation(code, format) {
    // Create a temporary confirmation message
    const confirmation = document.createElement('div');
    confirmation.className = 'barcode-confirmation';
    confirmation.innerHTML = `
        <p>Detected: <strong>${code}</strong> <span style="color: var(--color-text-tertiary); font-size: 12px;">(${format})</span></p>
        <button class="edit-barcode-btn" onclick="editBarcode()">Edit</button>
    `;
    
    // Insert before result card
    const container = document.querySelector('.scanner-section');
    container.insertAdjacentElement('afterend', confirmation);
    
    // Remove after 5 seconds
    setTimeout(() => {
        confirmation.remove();
    }, 5000);
}

// Edit barcode function
window.editBarcode = function() {
    const code = prompt('Edit barcode:', barcodeInput.value);
    if (code && /^\d{8,13}$/.test(code.trim())) {
        barcodeInput.value = code.trim();
        scanProduct();
    }
};

// Stop camera
function stopCamera() {
    scanning = false;
    lastScannedCode = null;
    scanConfidence = 0;
    scanAttempts = 0;
    
    // Stop Quagga if initialized
    if (quaggaInitialized) {
        try {
            Quagga.stop();
            quaggaInitialized = false;
        } catch (e) {
            console.log('Error stopping Quagga:', e);
        }
    }
    
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    cameraPreview.innerHTML = '';
    startCameraBtn.classList.remove('hidden');
    stopCameraBtn.classList.add('hidden');
    
    // Hide scanning indicator
    const indicator = document.getElementById('scanningIndicator');
    if (indicator) {
        indicator.classList.add('hidden');
    }
}

// Food camera functions
let foodStream = null;

async function startFoodCamera() {
    try {
        foodStream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'environment', // Use back camera if available
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        });
        
        foodVideo.srcObject = foodStream;
        foodCameraPreview.classList.remove('hidden');
        startFoodCameraBtn.classList.add('hidden');
        foodUploadArea.classList.add('hidden');
        
    } catch (error) {
        console.error('Error accessing camera:', error);
        showError('Could not access camera. Please check permissions and try again.');
    }
}

function stopFoodCamera() {
    if (foodStream) {
        foodStream.getTracks().forEach(track => track.stop());
        foodStream = null;
    }
    
    foodCameraPreview.classList.add('hidden');
    startFoodCameraBtn.classList.remove('hidden');
    foodUploadArea.classList.remove('hidden');
    if (foodVideo) {
        foodVideo.srcObject = null;
    }
}

function captureFoodPhoto() {
    if (!foodVideo || !foodStream) return;
    
    const canvas = document.createElement('canvas');
    canvas.width = foodVideo.videoWidth;
    canvas.height = foodVideo.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(foodVideo, 0, 0, canvas.width, canvas.height);
    
    // Convert to blob
    canvas.toBlob((blob) => {
        if (blob) {
            // Stop camera
            stopFoodCamera();
            
            // Show preview
            const img = document.createElement('img');
            img.src = URL.createObjectURL(blob);
            foodPreview.innerHTML = '';
            foodPreview.appendChild(img);
            foodPreview.classList.remove('hidden');
            
            // Create file from blob
            const file = new File([blob], 'food-photo.jpg', { type: 'image/jpeg' });
            
            // Scan food from captured image
            scanFoodFromImage(file);
        }
    }, 'image/jpeg', 0.9);
}

// Optimized professional-grade scanning
function scanBarcodeFromCamera() {
    if (!scanning) return;

    const video = cameraPreview.querySelector('video');
    if (!video || video.readyState !== video.HAVE_ENOUGH_DATA) {
        requestAnimationFrame(() => scanBarcodeFromCamera());
        return;
    }

    scanAttempts++;
    if (scanAttempts > MAX_SCAN_ATTEMPTS) {
        scanAttempts = 0;
    }

    const canvas = document.createElement('canvas');
    // Optimized resolution - balance between quality and speed
    const scale = 1.5; // Reduced from 2.5 for better performance
    canvas.width = video.videoWidth * scale;
    canvas.height = video.videoHeight * scale;
    const ctx = canvas.getContext('2d');
    
    // Fast image capture
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'medium'; // Changed from 'high' for speed
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Use faster image processing - only apply enhancement every 3rd frame
    if (scanAttempts % 3 === 0) {
        enhanceImageHighContrast(canvas);
    }

    // Try QR code first (fastest)
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const qrCode = jsQR(imageData.data, imageData.width, imageData.height);
    
    if (qrCode && qrCode.data) {
        const code = qrCode.data.trim();
        if (/^\d{8,13}$/.test(code)) {
            handleBarcodeDetected(code, { code });
            return;
        }
    }

    // Try Quagga with optimized settings
    try {
        // Use medium patch size for balance of speed and accuracy
        const patchSize = 'medium';
        
        Quagga.decodeSingle({
            decoder: {
                readers: [
                    'ean_reader',      // EAN-13 (13 digits) - prioritize this
                    'ean_8_reader',     // EAN-8 (8 digits)
                    'upc_reader',      // UPC-A (12 digits)
                    'upc_e_reader'     // UPC-E (8 digits)
                ],
                debug: {
                    drawBoundingBox: false,
                    showFrequency: false,
                    drawScanline: false,
                    showPattern: false
                }
            },
            locate: true,
            src: canvas.toDataURL('image/jpeg', 0.85), // Use JPEG with compression for speed
            numOfWorkers: 2, // Reduced from 4 for better performance
            patchSize: patchSize,
            halfSample: true // Always use half sample for speed
        }, (result) => {
            if (result && result.codeResult) {
                let code = result.codeResult.code;
                
                // Extract code properly - handle different formats
                if (typeof code === 'string') {
                    code = code.replace(/\D/g, '').trim();
                } else if (code && code.toString) {
                    code = code.toString().replace(/\D/g, '').trim();
                }
                
                // Validate and handle
                if (code && /^\d{8,13}$/.test(code)) {
                    console.log('Quagga detected:', code, 'Format:', result.codeResult.format);
                    handleBarcodeDetected(code, result.codeResult);
                }
            }
            
            // Continue scanning with optimized delay
            if (scanning) {
                setTimeout(() => scanBarcodeFromCamera(), 250); // Balanced delay
            }
        });
    } catch (error) {
        console.error('Scan error:', error);
        if (scanning) {
            setTimeout(() => scanBarcodeFromCamera(), 250);
        }
    }
}

// Professional image enhancement strategies
function enhanceImageStandard(canvas) {
    const ctx = canvas.getContext('2d');
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;
    const length = data.length;
    
    for (let i = 0; i < length; i += 4) {
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];
        const gray = Math.round(0.299 * r + 0.587 * g + 0.114 * b);
        
        data[i] = gray;
        data[i + 1] = gray;
        data[i + 2] = gray;
    }
    
    ctx.putImageData(imageData, 0, 0);
}

function enhanceImageHighContrast(canvas) {
    const ctx = canvas.getContext('2d');
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;
    const length = data.length;
    
    // Fast single-pass processing
    let sum = 0;
    const sampleSize = Math.floor(length / 100); // Sample every 100th pixel for speed
    
    // Quick average calculation
    for (let i = 0; i < length; i += sampleSize * 4) {
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];
        sum += Math.round(0.299 * r + 0.587 * g + 0.114 * b);
    }
    
    const avg = sum / (length / (sampleSize * 4));
    const threshold = avg * 0.9;
    
    // Fast high contrast binarization
    for (let i = 0; i < length; i += 4) {
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];
        const gray = Math.round(0.299 * r + 0.587 * g + 0.114 * b);
        const enhanced = gray > threshold ? 255 : 0;
        
        data[i] = enhanced;
        data[i + 1] = enhanced;
        data[i + 2] = enhanced;
    }
    
    ctx.putImageData(imageData, 0, 0);
}

// Removed adaptive thresholding - too slow
// Using only fast high-contrast method for better performance

// Handle file upload
function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        showError('Please upload an image file');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        const img = document.createElement('img');
        img.src = e.target.result;
        uploadPreview.innerHTML = '';
        uploadPreview.appendChild(img);
        uploadPreview.classList.remove('hidden');

        // Scan barcode from image
        scanBarcodeFromImage(e.target.result);
    };
    reader.readAsDataURL(file);
}

// Scan barcode/QR from image
function scanBarcodeFromImage(imageSrc) {
    showLoading();
    hideAll();

    const img = new Image();
    img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);

        // Try QR code first
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const qrCode = jsQR(imageData.data, imageData.width, imageData.height);
        
        if (qrCode && qrCode.data) {
            const code = qrCode.data.trim();
            if (/^\d{8,13}$/.test(code)) {
                hideLoading();
                barcodeInput.value = code;
                switchTab('manual');
                scanProduct();
                return;
            }
        }

        // Try barcode scanning
        try {
            Quagga.decodeSingle({
                decoder: {
                    readers: ['ean_reader', 'ean_8_reader', 'code_128_reader', 'upc_reader', 'upc_e_reader', 'code_39_reader', 'codabar_reader']
                },
                locate: true,
                src: imageSrc
            }, (result) => {
                hideLoading();
                if (result && result.codeResult) {
                    const code = result.codeResult.code;
                    if (code && (/^\d{8,13}$/.test(code) || /^[A-Z0-9]{6,20}$/i.test(code))) {
                        barcodeInput.value = code;
                        switchTab('manual');
                        scanProduct();
                    } else {
                        showError('Detected code but it\'s not a valid product barcode format.');
                    }
                } else {
                    showError('Could not detect a barcode or QR code in the image. Please ensure it\'s clear and try again.');
                }
            });
        } catch (error) {
            hideLoading();
            showError('Error scanning image: ' + error.message);
        }
    };
    img.src = imageSrc;
}

// Handle food image file
function handleFoodFile(file) {
    if (!file.type.startsWith('image/')) {
        showError('Please upload an image file');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        const img = document.createElement('img');
        img.src = e.target.result;
        foodPreview.innerHTML = '';
        foodPreview.appendChild(img);
        foodPreview.classList.remove('hidden');

        // Scan food from image
        scanFoodFromImage(file);
    };
    reader.readAsDataURL(file);
}

// Scan food from image
async function scanFoodFromImage(file) {
    hideAll();
    showLoading();
    
    console.log('Starting food image scan...');
    console.log('File:', file.name, 'Size:', file.size, 'Type:', file.type);
    console.log('API URL:', `${API_BASE_URL}/scan-image`);
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        console.log('Sending request to backend...');
        const response = await fetch(`${API_BASE_URL}/scan-image`, {
            method: 'POST',
            body: formData
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', Object.fromEntries(response.headers.entries()));
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status} error` }));
            console.error('Error response:', errorData);
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Success! Data received:', data);
        displayResult(data);
        
    } catch (error) {
        console.error('Scan error:', error);
        showError(error.message || 'Failed to recognize food. Please ensure the image shows a clear food item.');
    } finally {
        hideLoading();
    }
}

// Scan product function
async function scanProduct() {
    const barcode = barcodeInput.value.trim();
    
    if (!barcode) {
        showError('Please enter a barcode');
        return;
    }
    
    // Accept numeric barcodes (8-13 digits) or alphanumeric codes
    if (!/^\d{8,13}$/.test(barcode) && !/^[A-Z0-9]{6,20}$/i.test(barcode)) {
        showError('Please enter a valid barcode (8-13 digits) or product code');
        return;
    }
    
    hideAll();
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/scan?barcode=${encodeURIComponent(barcode)}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayResult(data);
        
    } catch (error) {
        showError(error.message || 'Failed to scan product. Please check your connection and try again.');
    } finally {
        hideLoading();
    }
}

// Display result
function displayResult(data) {
    document.getElementById('productName').textContent = data.product_name || 'Unknown Product';
    document.getElementById('productBrand').textContent = data.brand || 'Unknown';
    document.getElementById('productBarcode').textContent = data.barcode || (data.source === 'image_recognition' ? 'N/A (Food Image)' : '-');
    
    const healthBadge = document.getElementById('healthBadge');
    const healthLabel = healthBadge.querySelector('.health-status-label');
    healthLabel.textContent = data.health_prediction;
    healthBadge.className = `health-status ${data.health_prediction.toLowerCase()}`;
    
    document.getElementById('healthMessage').textContent = data.message || 'No health information available.';
    
    // Nutrition Score
    const score = data.nutrition_score || 50;
    document.getElementById('nutritionScore').textContent = score.toFixed(0);
    const scoreProgress = document.getElementById('scoreProgress');
    const circumference = 2 * Math.PI * 54;
    const offset = circumference - (score / 100) * circumference;
    scoreProgress.style.strokeDashoffset = offset;
    
    // Set score color based on value
    if (score >= 70) {
        scoreProgress.style.stroke = 'var(--color-healthy)';
    } else if (score >= 40) {
        scoreProgress.style.stroke = 'var(--color-moderate)';
    } else {
        scoreProgress.style.stroke = 'var(--color-unhealthy)';
    }
    
    // Daily Values and Nutrition
    const nutrients = data.nutrients;
    const dailyValues = data.daily_values || {};
    
    // Energy
    document.getElementById('energy').textContent = `${nutrients.energy_100g.toFixed(0)}`;
    document.getElementById('energyDV').textContent = `${dailyValues.energy?.toFixed(0) || 0}% DV`;
    document.getElementById('energyBar').style.width = `${Math.min(100, dailyValues.energy || 0)}%`;
    
    // Protein
    document.getElementById('proteins').textContent = `${nutrients.proteins_100g.toFixed(1)}`;
    document.getElementById('proteinsDV').textContent = `${dailyValues.protein?.toFixed(0) || 0}% DV`;
    document.getElementById('proteinsBar').style.width = `${Math.min(100, dailyValues.protein || 0)}%`;
    
    // Fat
    document.getElementById('fat').textContent = `${nutrients.fat_100g.toFixed(1)}`;
    document.getElementById('fatDV').textContent = `${dailyValues.fat?.toFixed(0) || 0}% DV`;
    document.getElementById('fatBar').style.width = `${Math.min(100, dailyValues.fat || 0)}%`;
    
    // Sugars
    document.getElementById('sugars').textContent = `${nutrients.sugars_100g.toFixed(1)}`;
    document.getElementById('sugarsDV').textContent = `${dailyValues.sugar?.toFixed(0) || 0}% DV`;
    document.getElementById('sugarsBar').style.width = `${Math.min(100, dailyValues.sugar || 0)}%`;
    
    // Fiber
    document.getElementById('fiber').textContent = `${nutrients.fiber_100g.toFixed(1)}`;
    document.getElementById('fiberDV').textContent = `${dailyValues.fiber?.toFixed(0) || 0}% DV`;
    document.getElementById('fiberBar').style.width = `${Math.min(100, dailyValues.fiber || 0)}%`;
    
    // Salt
    document.getElementById('salt').textContent = `${nutrients.salt_100g.toFixed(2)}`;
    document.getElementById('saltDV').textContent = `${dailyValues.salt?.toFixed(0) || 0}% DV`;
    document.getElementById('saltBar').style.width = `${Math.min(100, dailyValues.salt || 0)}%`;
    
    // Health Insights
    const insightsSection = document.getElementById('healthInsightsSection');
    const insightsList = document.getElementById('healthInsightsList');
    if (data.health_insights && data.health_insights.length > 0) {
        insightsList.innerHTML = data.health_insights
            .map(insight => `<div class="insight-item ${insight.type}">${insight.text}</div>`)
            .join('');
        insightsSection.classList.remove('hidden');
    } else {
        insightsSection.classList.add('hidden');
    }
    
    // Allergens
    const allergensSection = document.getElementById('allergensSection');
    const allergensList = document.getElementById('allergensList');
    if (data.detected_allergens && data.detected_allergens.length > 0) {
        allergensList.innerHTML = data.detected_allergens
            .map(allergen => `<span class="info-tag">${allergen}</span>`)
            .join('');
        allergensSection.classList.remove('hidden');
    } else {
        allergensSection.classList.add('hidden');
    }
    
    // Additives
    const additivesSection = document.getElementById('additivesSection');
    const additivesList = document.getElementById('additivesList');
    if (data.detected_additives && data.detected_additives.length > 0) {
        additivesList.innerHTML = data.detected_additives
            .map(additive => `<span class="info-tag">${additive}</span>`)
            .join('');
        additivesSection.classList.remove('hidden');
    } else {
        additivesSection.classList.add('hidden');
    }
    
    // Sugar indicators
    const sugarSection = document.getElementById('sugarSection');
    const sugarList = document.getElementById('sugarList');
    if (data.detected_sugar_indicators && data.detected_sugar_indicators.length > 0) {
        sugarList.innerHTML = data.detected_sugar_indicators
            .map(indicator => `<span class="info-tag">${indicator}</span>`)
            .join('');
        sugarSection.classList.remove('hidden');
    } else {
        sugarSection.classList.add('hidden');
    }
    
    resultCard.classList.remove('hidden');
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function showLoading() {
    loadingIndicator.classList.remove('hidden');
    scanButton.disabled = true;
}

function hideLoading() {
    loadingIndicator.classList.add('hidden');
    scanButton.disabled = false;
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function hideAll() {
    errorMessage.classList.add('hidden');
    resultCard.classList.add('hidden');
}
