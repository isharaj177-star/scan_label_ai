# ScanLabel AI Frontend

Simple, mobile-optimized frontend for ScanLabel AI.

## Features

- ✅ Mobile-first responsive design
- ✅ Clean, minimal UI
- ✅ Real-time product scanning
- ✅ Health analysis display
- ✅ Nutrition facts visualization
- ✅ Allergen and additive detection

## Usage

1. **Start the backend API:**
   ```bash
   cd ..
   uvicorn main:app --reload
   ```

2. **Open the frontend:**
   - Simply open `index.html` in a web browser
   - Or serve it with a local server:
     ```bash
     python -m http.server 8080
     ```
   - Then open: http://localhost:8080

3. **Update API URL (if needed):**
   - Edit `app.js` and change `API_BASE_URL` if your backend runs on a different port

## Mobile Optimization

- Touch-friendly buttons (min 44px height)
- No zoom on input focus (prevents iOS keyboard issues)
- Responsive grid layouts
- Optimized font sizes for mobile
- Fast loading and smooth animations

## Browser Support

- Chrome/Edge (latest)
- Safari (iOS 12+)
- Firefox (latest)
- Mobile browsers

## Files

- `index.html` - Main HTML structure
- `styles.css` - All styling (mobile-first)
- `app.js` - JavaScript logic and API integration








