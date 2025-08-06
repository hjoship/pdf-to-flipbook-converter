#!/usr/bin/env python3
"""
Simplified PDF to HTML5 Flipbook Converter
Works without PyMuPDF by using alternative PDF processing methods.
"""

import os
import sys
import zipfile
import shutil
import argparse
from pathlib import Path
import subprocess
import tempfile
from PIL import Image
import requests

class SimpleFlipbookConverter:
    def __init__(self, pdf_path, output_dir="flipbook_output"):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.pages_dir = self.output_dir / "pages"
        self.assets_dir = self.output_dir / "assets"
        self.js_dir = self.assets_dir / "js"
        self.css_dir = self.assets_dir / "css"
        
    def create_directories(self):
        """Create the required directory structure."""
        for directory in [self.output_dir, self.pages_dir, self.js_dir, self.css_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
    def extract_pdf_pages_with_poppler(self):
        """Extract PDF pages using poppler-utils (pdftoppm)."""
        print(f"Extracting pages from {self.pdf_path} using poppler...")
        
        try:
            # Use pdftoppm to convert PDF to images (with full path)
            pdftoppm_path = "/opt/homebrew/bin/pdftoppm"  # Homebrew install path
            if not os.path.exists(pdftoppm_path):
                pdftoppm_path = "pdftoppm"  # Fallback to PATH
            
            cmd = [
                pdftoppm_path, 
                str(self.pdf_path), 
                str(self.pages_dir / "page"),
                "-jpeg", 
                "-r", "300"  # 300 DPI
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"pdftoppm failed: {result.stderr}")
                
            # Count generated pages
            page_files = list(self.pages_dir.glob("page-*.jpg"))
            
            # Rename files to match expected format
            for i, page_file in enumerate(sorted(page_files), 1):
                new_name = f"page{i:03d}.jpg"
                page_file.rename(self.pages_dir / new_name)
                
            print(f"Extracted {len(page_files)} pages")
            return len(page_files)
            
        except FileNotFoundError:
            print("pdftoppm not found. Please install poppler-utils:")
            print("  macOS: brew install poppler")
            print("  Ubuntu: sudo apt-get install poppler-utils")
            return self.extract_pdf_pages_fallback()
            
    def extract_pdf_pages_fallback(self):
        """Fallback method using Python libraries."""
        print("Using fallback PDF extraction method...")
        
        try:
            import pdf2image
            from pdf2image import convert_from_path
            
            # Convert PDF to images
            images = convert_from_path(self.pdf_path, dpi=300)
            
            for i, image in enumerate(images, 1):
                page_filename = f"page{i:03d}.jpg"
                page_path = self.pages_dir / page_filename
                image.save(page_path, "JPEG", quality=95, optimize=True)
                print(f"Extracted page {i}/{len(images)}")
                
            return len(images)
            
        except ImportError:
            print("pdf2image not available. Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pdf2image"], check=True)
            return self.extract_pdf_pages_fallback()
            
    def create_flipbook_library(self):
        """Create a lightweight flipbook implementation."""
        print("Creating flipbook library...")
        
        # Enhanced CSS with better animations
        css_content = """
/* Enhanced Flipbook Styles */
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.flipbook-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.header {
    text-align: center;
    color: white;
    margin-bottom: 30px;
}

.header h1 {
    margin: 0;
    font-size: 2.5em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.header p {
    margin: 10px 0;
    opacity: 0.9;
}

.flipbook-wrapper {
    position: relative;
    background: white;
    border-radius: 15px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.2);
    overflow: hidden;
}

.flipbook {
    position: relative;
    width: 100%;
    height: 70vh;
    min-height: 500px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f8f9fa;
}

.page-container {
    position: relative;
    width: 90%;
    height: 90%;
    max-width: 800px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    overflow: hidden;
    transition: transform 0.3s ease;
}

.page-container:hover {
    transform: scale(1.02);
}

.page {
    width: 100%;
    height: 100%;
    display: none;
    align-items: center;
    justify-content: center;
}

.page.active {
    display: flex;
}

.page img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    border-radius: 4px;
}

.controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 30px;
    background: white;
    border-top: 1px solid #e9ecef;
}

.nav-btn {
    background: #667eea;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 25px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 500;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 8px;
}

.nav-btn:hover:not(:disabled) {
    background: #5a6fd8;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.nav-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

.page-info {
    display: flex;
    align-items: center;
    gap: 15px;
    color: #495057;
    font-weight: 500;
}

.page-counter {
    font-size: 18px;
}

.progress-bar {
    width: 200px;
    height: 6px;
    background: #e9ecef;
    border-radius: 3px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: #667eea;
    border-radius: 3px;
    transition: width 0.3s ease;
}

.footer {
    text-align: center;
    color: white;
    margin-top: 30px;
    opacity: 0.8;
}

.footer p {
    margin: 5px 0;
}

.footer code {
    background: rgba(255,255,255,0.2);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Monaco', 'Menlo', monospace;
}

/* Responsive Design */
@media (max-width: 768px) {
    .flipbook-container {
        padding: 10px;
    }
    
    .header h1 {
        font-size: 2em;
    }
    
    .flipbook {
        height: 60vh;
        min-height: 400px;
    }
    
    .controls {
        padding: 15px 20px;
        flex-direction: column;
        gap: 15px;
    }
    
    .page-info {
        flex-direction: column;
        gap: 10px;
    }
    
    .progress-bar {
        width: 150px;
    }
}

/* Loading Animation */
.loading {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #666;
    font-size: 18px;
}

.loading::after {
    content: '';
    width: 20px;
    height: 20px;
    border: 2px solid #ddd;
    border-top: 2px solid #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-left: 10px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
"""
        
        # Enhanced JavaScript with better functionality
        js_content = """
class EnhancedFlipbook {
    constructor(container, pages) {
        this.container = container;
        this.pages = pages;
        this.currentPage = 0;
        this.totalPages = pages.length;
        this.isLoading = false;
        this.preloadedImages = new Map();
        
        this.init();
    }
    
    init() {
        this.createHTML();
        this.bindEvents();
        this.preloadImages();
        this.updateDisplay();
    }
    
    createHTML() {
        this.container.innerHTML = `
            <div class="flipbook-wrapper">
                <div class="flipbook" id="flipbook">
                    <div class="page-container">
                        ${this.pages.map((page, index) => `
                            <div class="page" data-page="${index}">
                                <img src="${page}" alt="Page ${index + 1}" loading="lazy" />
                            </div>
                        `).join('')}
                        <div class="page loading" id="loading-page">
                            Loading page...
                        </div>
                    </div>
                </div>
                <div class="controls">
                    <button class="nav-btn" id="prev-btn">
                        <span>←</span> Previous
                    </button>
                    <div class="page-info">
                        <div class="page-counter">
                            <span id="current-page">1</span> / <span id="total-pages">${this.totalPages}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="progress-fill"></div>
                        </div>
                    </div>
                    <button class="nav-btn" id="next-btn">
                        Next <span>→</span>
                    </button>
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        document.getElementById('prev-btn').addEventListener('click', () => this.prevPage());
        document.getElementById('next-btn').addEventListener('click', () => this.nextPage());
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                e.preventDefault();
                this.prevPage();
            }
            if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
                e.preventDefault();
                this.nextPage();
            }
            if (e.key === 'Home') {
                e.preventDefault();
                this.goToPage(0);
            }
            if (e.key === 'End') {
                e.preventDefault();
                this.goToPage(this.totalPages - 1);
            }
        });
        
        // Touch/swipe support
        let startX = 0;
        let startY = 0;
        
        this.container.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        this.container.addEventListener('touchend', (e) => {
            if (!startX || !startY) return;
            
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            
            const diffX = startX - endX;
            const diffY = startY - endY;
            
            // Only handle horizontal swipes
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                if (diffX > 0) {
                    this.nextPage(); // Swipe left = next page
                } else {
                    this.prevPage(); // Swipe right = previous page
                }
            }
            
            startX = 0;
            startY = 0;
        });
    }
    
    preloadImages() {
        // Preload current and next few images
        const preloadCount = Math.min(3, this.totalPages);
        for (let i = 0; i < preloadCount; i++) {
            this.preloadImage(i);
        }
    }
    
    preloadImage(index) {
        if (index >= 0 && index < this.totalPages && !this.preloadedImages.has(index)) {
            const img = new Image();
            img.onload = () => {
                this.preloadedImages.set(index, true);
            };
            img.src = this.pages[index];
        }
    }
    
    nextPage() {
        if (this.currentPage < this.totalPages - 1) {
            this.goToPage(this.currentPage + 1);
        }
    }
    
    prevPage() {
        if (this.currentPage > 0) {
            this.goToPage(this.currentPage - 1);
        }
    }
    
    goToPage(pageIndex) {
        if (pageIndex >= 0 && pageIndex < this.totalPages && pageIndex !== this.currentPage) {
            this.currentPage = pageIndex;
            this.updateDisplay();
            
            // Preload nearby pages
            this.preloadImage(pageIndex + 1);
            this.preloadImage(pageIndex + 2);
            this.preloadImage(pageIndex - 1);
        }
    }
    
    updateDisplay() {
        // Hide all pages
        const pages = document.querySelectorAll('.page[data-page]');
        pages.forEach(page => page.classList.remove('active'));
        
        // Show current page
        const currentPageElement = document.querySelector(`[data-page="${this.currentPage}"]`);
        if (currentPageElement) {
            currentPageElement.classList.add('active');
        }
        
        // Update controls
        document.getElementById('current-page').textContent = this.currentPage + 1;
        document.getElementById('prev-btn').disabled = this.currentPage === 0;
        document.getElementById('next-btn').disabled = this.currentPage === this.totalPages - 1;
        
        // Update progress bar
        const progress = ((this.currentPage + 1) / this.totalPages) * 100;
        document.getElementById('progress-fill').style.width = progress + '%';
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Flipbook initializing...');
});
"""
        
        # Save files
        with open(self.css_dir / "flipbook.css", "w", encoding="utf-8") as f:
            f.write(css_content)
            
        with open(self.js_dir / "flipbook.js", "w", encoding="utf-8") as f:
            f.write(js_content)
            
        print("Flipbook library created successfully")
        
    def generate_html(self, total_pages):
        """Generate the main HTML file for the flipbook."""
        print("Generating HTML flipbook viewer...")
        
        # Get list of page images
        page_images = [f"pages/page{i+1:03d}.jpg" for i in range(total_pages)]
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Flipbook Viewer</title>
    <link rel="stylesheet" href="assets/css/flipbook.css">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📖</text></svg>">
</head>
<body>
    <div class="flipbook-container">
        <div class="header">
            <h1>📖 PDF Flipbook</h1>
            <p>Navigate with arrow keys, swipe, or use the buttons below</p>
        </div>
        
        <div id="flipbook-container"></div>
        
        <div class="footer">
            <p>Generated with PDF to Flipbook Converter</p>
            <p><small>If this doesn't work due to browser security, run: <code>python3 -m http.server</code></small></p>
        </div>
    </div>
    
    <script src="assets/js/flipbook.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const pages = {page_images};
            const container = document.getElementById('flipbook-container');
            
            // Initialize the enhanced flipbook
            const flipbook = new EnhancedFlipbook(container, pages);
            
            console.log('Enhanced Flipbook initialized with', pages.length, 'pages');
            
            // Add some helpful console messages
            console.log('Keyboard shortcuts:');
            console.log('  ← → : Navigate pages');
            console.log('  Home/End : Go to first/last page');
            console.log('Touch devices: Swipe left/right to navigate');
        }});
    </script>
</body>
</html>"""
        
        html_path = self.output_dir / "index.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"Generated {html_path}")
        
    def create_zip(self):
        """Create a zip file of the entire flipbook."""
        zip_path = self.output_dir.parent / f"{self.output_dir.name}.zip"
        
        print(f"Creating zip file: {zip_path}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    file_path = Path(root) / file
                    arc_path = file_path.relative_to(self.output_dir)
                    zipf.write(file_path, arc_path)
                    
        print(f"Zip file created: {zip_path}")
        return zip_path
        
    def convert(self):
        """Main conversion process."""
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
            
        print(f"Converting {self.pdf_path} to flipbook...")
        
        # Create directory structure
        self.create_directories()
        
        # Try different PDF extraction methods
        try:
            total_pages = self.extract_pdf_pages_with_poppler()
        except Exception as e:
            print(f"Poppler extraction failed: {e}")
            total_pages = self.extract_pdf_pages_fallback()
        
        if total_pages == 0:
            raise Exception("No pages could be extracted from the PDF")
        
        # Create flipbook library
        self.create_flipbook_library()
        
        # Generate HTML
        self.generate_html(total_pages)
        
        # Create zip file
        zip_path = self.create_zip()
        
        print(f"\n✅ Conversion complete!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📦 Zip file: {zip_path}")
        print(f"🌐 Open {self.output_dir / 'index.html'} in your browser")
        
        return zip_path


def main():
    parser = argparse.ArgumentParser(description="Convert PDF to HTML5 Flipbook (Simplified)")
    parser.add_argument("pdf_file", help="Path to the PDF file")
    parser.add_argument("-o", "--output", default="flipbook_output", 
                       help="Output directory name (default: flipbook_output)")
    
    args = parser.parse_args()
    
    try:
        converter = SimpleFlipbookConverter(args.pdf_file, args.output)
        zip_path = converter.convert()
        
        print(f"\n🎉 Your flipbook is ready!")
        print(f"📥 Download: {zip_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
