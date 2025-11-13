// API Configuration - automatically use deployed URL or localhost
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : window.location.origin;

// Debug: Log API URL on load
console.log('ScanLabel AI initialized');
console.log('API URL:', API_BASE_URL);
console.log('Hostname:', window.location.hostname);
console.log('Origin:', window.location.origin);

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
let scanAttempts = 0;
const MAX_SCAN_ATTEMPTS = 10;

// Initialize ZXing (modern, accurate barcode reader)
let codeReader = null;
try {
    if (typeof ZXing !== 'undefined') {
        codeReader = new ZXing.BrowserMultiFormatReader();
        console.log('ZXing initialized successfully');
    }
} catch (error) {
    console.error('ZXing initialization failed:', error);
}

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
        if (!codeReader) {
            showError('Barcode scanner not initialized. Please refresh the page.');
            return;
        }

        // Create video element for ZXing
        const video = document.createElement('video');
        video.id = 'barcode-video';
        video.style.width = '100%';
        video.style.height = 'auto';
        video.setAttribute('autoplay', '');
        video.setAttribute('playsinline', '');

        // Create scanning animation overlay
        const scannerOverlay = document.createElement('div');
        scannerOverlay.className = 'scanner-overlay';
        scannerOverlay.innerHTML = `
            <div class="scanner-frame">
                <div class="scanner-corner top-left"></div>
                <div class="scanner-corner top-right"></div>
                <div class="scanner-corner bottom-left"></div>
                <div class="scanner-corner bottom-right"></div>
                <div class="scanner-line"></div>
            </div>
            <p class="scanner-hint">Align barcode within frame</p>
        `;

        cameraPreview.innerHTML = '';
        cameraPreview.appendChild(video);
        cameraPreview.appendChild(scannerOverlay);

        startCameraBtn.classList.add('hidden');
        stopCameraBtn.classList.remove('hidden');

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

        // Use ZXing to decode from camera
        console.log('Starting ZXing camera scanner...');
        codeReader.decodeFromVideoDevice(undefined, 'barcode-video', (result, err) => {
            if (result) {
                console.log('ZXing scan result:', result);
                const code = result.text.replace(/\D/g, '').trim();
                if (code && /^\d{8,13}$/.test(code)) {
                    console.log('Valid barcode detected:', code, 'Format:', result.format);
                    handleBarcodeDetected(code, { code, format: result.format });
                }
            }
            if (err && !(err instanceof ZXing.NotFoundException)) {
                console.error('ZXing error:', err);
            }
        });

        console.log('Camera started with ZXing scanner');
    } catch (error) {
        showError('Camera access denied. Please allow camera access and try again.');
        console.error('Camera error:', error);
    }
}

// ZXing scanner handles everything automatically via decodeFromVideoDevice

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
    
    // Lower confidence requirements for faster detection
    // Most barcodes are validated by checksum anyway
    const requiredConfidence = code.length === 13 ? 1 : code.length === 12 ? 1 : 2;
    
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

    // Reset ZXing
    if (codeReader) {
        try {
            codeReader.reset();
        } catch (e) {
            console.log('Error resetting ZXing:', e);
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

// ZXing continuous scanning is now handled by decodeFromVideoDevice callback in startCamera()

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
        const url = `${API_BASE_URL}/scan?barcode=${encodeURIComponent(barcode)}`;
        console.log('Fetching:', url);

        const response = await fetch(url);
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);

        if (!response.ok) {
            const errorData = await response.json();
            console.error('API Error:', errorData);
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('API Success:', data);
        displayResult(data);

    } catch (error) {
        console.error('Scan error:', error);
        showError(`Error: ${error.message}\n\nAPI: ${API_BASE_URL}\n\nPlease check your connection and try again.`);
    } finally {
        hideLoading();
    }
}

// Display result
function displayResult(data) {
    // Store product data for alternatives feature
    currentProductData = data;

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
    
    // Health Insights - Enhanced with categories
    const insightsSection = document.getElementById('healthInsightsSection');
    const insightsList = document.getElementById('healthInsightsList');
    if (data.health_insights && data.health_insights.length > 0) {
        // Categorize insights
        const categorized = {
            warning: data.health_insights.filter(i => i.type === 'warning'),
            caution: data.health_insights.filter(i => i.type === 'caution'),
            positive: data.health_insights.filter(i => i.type === 'positive'),
            info: data.health_insights.filter(i => i.type === 'info')
        };

        // Get category labels
        const getCategory = (type) => {
            const labels = {
                warning: 'Health Concern',
                caution: 'Moderate',
                positive: 'Benefit',
                info: 'Information'
            };
            return labels[type] || 'Info';
        };

        // Update insights count
        const countEl = document.getElementById('insightsCount');
        if (countEl) {
            const warnings = categorized.warning.length;
            const cautions = categorized.caution.length;
            const positives = categorized.positive.length;

            const parts = [];
            if (warnings > 0) parts.push(`${warnings} critical`);
            if (cautions > 0) parts.push(`${cautions} moderate`);
            if (positives > 0) parts.push(`${positives} positive`);

            countEl.textContent = parts.join(' • ') || `${data.health_insights.length} findings`;
        }

        // Severity level mappings
        const getSeverityData = (type) => {
            const severityMap = {
                warning: { badge: 'HIGH', label: 'Critical', level: 3 },
                caution: { badge: 'MED', label: 'Moderate', level: 2 },
                positive: { badge: 'LOW', label: 'Positive', level: 1 },
                info: { badge: 'INFO', label: 'Notice', level: 0 }
            };
            return severityMap[type] || severityMap.info;
        };

        // Extract metric from insight text if present
        const extractMetric = (text) => {
            // Look for patterns like "99.0g", "15%", etc.
            const match = text.match(/(\d+\.?\d*\s*g|\d+%|very high|high|moderate|low|very low)/i);
            return match ? match[0] : null;
        };

        insightsList.innerHTML = data.health_insights
            .map(insight => {
                const severity = getSeverityData(insight.type);
                const metric = extractMetric(insight.text);

                return `
                    <div class="insight-item ${insight.type}">
                        <div class="insight-severity">
                            <div class="severity-badge">${severity.badge}</div>
                            <div class="severity-label">${severity.label}</div>
                        </div>
                        <div class="insight-content">
                            <div class="insight-text">${insight.text}</div>
                            ${metric ? `<div class="insight-metric">Detected value: ${metric}</div>` : ''}
                        </div>
                    </div>
                `;
            })
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
    // Preserve line breaks by replacing \n with <br>
    errorMessage.innerHTML = message.replace(/\n/g, '<br>');
    errorMessage.classList.remove('hidden');
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function hideAll() {
    errorMessage.classList.add('hidden');
    resultCard.classList.add('hidden');
    // Hide alternatives section when scanning a new product
    const alternativesResults = document.getElementById('alternativesResults');
    if (alternativesResults) {
        alternativesResults.classList.add('hidden');
    }
}

// Store current product data for alternatives
let currentProductData = null;

// Get Healthier Alternatives functionality
document.addEventListener('DOMContentLoaded', () => {
    const getAlternativesBtn = document.getElementById('getAlternativesBtn');
    if (getAlternativesBtn) {
        getAlternativesBtn.addEventListener('click', getHealthierAlternatives);
    }
});

async function getHealthierAlternatives() {
    if (!currentProductData) {
        showError('No product data available. Please scan a product first.');
        return;
    }

    const alternativesBtn = document.getElementById('getAlternativesBtn');
    const alternativesResults = document.getElementById('alternativesResults');

    // Show loading state
    alternativesBtn.disabled = true;
    alternativesBtn.innerHTML = `
        <svg class="spinner-small" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
        </svg>
        Loading...
    `;

    try {
        const response = await fetch(`${API_BASE_URL}/recommend-alternatives`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(currentProductData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to get alternatives');
        }

        const data = await response.json();
        displayAlternatives(data);

        // Scroll to alternatives
        alternativesResults.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (error) {
        console.error('Alternatives error:', error);
        showError(`Failed to get alternatives: ${error.message}`);
    } finally {
        // Restore button
        alternativesBtn.disabled = false;
        alternativesBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            Get Healthier Alternatives
        `;
    }
}

function displayAlternatives(data) {
    const alternativesResults = document.getElementById('alternativesResults');
    const alternativesSource = document.getElementById('alternativesSource');
    const alternativesSummary = document.getElementById('alternativesSummary');
    const alternativesList = document.getElementById('alternativesList');
    const alternativesTips = document.getElementById('alternativesTips');
    const alternativesTipsList = document.getElementById('alternativesTipsList');

    // Show source
    const sourceText = data.source === 'ai_powered' ? 'Personalized Recommendations' : 'Smart Recommendations';
    alternativesSource.textContent = sourceText;

    // Show summary
    alternativesSummary.textContent = data.summary || 'Here are some healthier alternatives for you:';

    // Display alternatives
    if (data.alternatives && data.alternatives.length > 0) {
        alternativesList.innerHTML = data.alternatives.map((alt, index) => `
            <div class="alternative-card">
                <div class="alternative-header">
                    <div class="alternative-number">${index + 1}</div>
                    <div class="alternative-title">
                        <h4>${alt.name}</h4>
                        <span class="alternative-brand">${alt.brand}</span>
                    </div>
                </div>
                <p class="alternative-reason">${alt.why_better}</p>
                <div class="alternative-benefits">
                    ${alt.key_benefits.map(benefit => `
                        <span class="benefit-tag">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="20 6 9 17 4 12"></polyline>
                            </svg>
                            ${benefit}
                        </span>
                    `).join('')}
                </div>
                ${alt.estimated_improvements ? `
                    <div class="alternative-improvements">
                        ${Object.entries(alt.estimated_improvements).map(([key, value]) => `
                            <div class="improvement-item">
                                <span class="improvement-label">${key}:</span>
                                <span class="improvement-value">${value}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    // Display general tips
    if (data.general_tips && data.general_tips.length > 0) {
        alternativesTipsList.innerHTML = data.general_tips
            .map(tip => `<li>${tip}</li>`)
            .join('');
        alternativesTips.classList.remove('hidden');
    } else {
        alternativesTips.classList.add('hidden');
    }

    // Show results
    alternativesResults.classList.remove('hidden');
}
