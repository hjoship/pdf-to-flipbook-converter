# PDF to HTML5 Flipbook Converter

Convert your PDF files into beautiful, self-contained HTML5 flipbooks that work offline!

## Features

- 📄 **High-Quality Extraction**: Extracts PDF pages at 300 DPI for crisp images
- 📖 **Interactive Flipbook**: Smooth page-turning animations with keyboard navigation
- 🌐 **Offline Support**: No internet required - all assets included locally
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- 📦 **Self-Contained**: Everything packaged in a single ZIP file
- ⚡ **Easy to Use**: Simple web interface or command-line tool

## Quick Start

### Option 1: Web Interface (Recommended)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Web Server**:
   ```bash
   python web_interface.py
   ```

3. **Open Your Browser**:
   - Go to `http://localhost:5000`
   - Upload your PDF file
   - Download the generated flipbook ZIP

### Option 2: Command Line

```bash
# Install dependencies
pip install -r requirements.txt

# Convert a PDF
python pdf_to_flipbook.py your_document.pdf

# Custom output directory and DPI
python pdf_to_flipbook.py your_document.pdf -o my_flipbook -d 300
```

## Output Structure

The generated flipbook contains:

```
flipbook_output/
├── index.html          # Main flipbook viewer
├── assets/
│   ├── css/
│   │   └── page-flip.css
│   └── js/
│       └── page-flip.js
└── pages/
    ├── page001.jpg
    ├── page002.jpg
    └── ...
```

## Usage Instructions

1. **Double-click `index.html`** to open the flipbook in your browser
2. **Navigation**:
   - Use arrow keys (← →) to turn pages
   - Click the Previous/Next buttons
   - View page counter to track progress

3. **If Browser Blocks Local Files**:
   ```bash
   cd flipbook_output
   python3 -m http.server 8000
   ```
   Then open `http://localhost:8000`

## Requirements

- Python 3.7+
- PyMuPDF (for PDF processing)
- Pillow (for image handling)
- Flask (for web interface)
- Requests (for downloading libraries)

## Browser Compatibility

- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 12+
- ✅ Edge 79+

## Troubleshooting

### Common Issues

1. **"Module not found" error**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Browser security restrictions**:
   - Use the local server method: `python3 -m http.server`
   - Or upload to a web server

3. **Large PDF files**:
   - Reduce DPI: `python pdf_to_flipbook.py file.pdf -d 150`
   - Split large PDFs into smaller sections

4. **Memory issues**:
   - Close other applications
   - Use lower DPI settings
   - Process PDFs in smaller batches

### Performance Tips

- **Optimal DPI**: 300 DPI for print quality, 150 DPI for web viewing
- **File Size**: Keep individual PDFs under 100MB for best performance
- **Browser**: Use Chrome or Firefox for best flipbook performance

## Advanced Usage

### Custom Styling

Edit `assets/css/page-flip.css` to customize:
- Colors and themes
- Page dimensions
- Animation speed
- Button styles

### Adding Features

The flipbook uses a simple JavaScript class that can be extended:
- Add zoom functionality
- Include search capabilities
- Add bookmarks
- Implement fullscreen mode

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed
3. Verify your PDF is not corrupted
4. Try with a smaller test PDF first

---

**Your flipbook is ready! 🎉**

Simply run the converter and enjoy your beautiful HTML5 flipbook!
