#!/usr/bin/env python3
"""
PDF to HTML5 Flipbook Converter
Converts a PDF file into a self-contained HTML5 flipbook with offline support.
"""

import os
import sys
import zipfile
import shutil
import argparse
from pathlib import Path
import requests
from io import BytesIO

try:
    import fitz  # PyMuPDF
    from PIL import Image
except ImportError:
    print("Required packages not installed. Please run:")
    print("pip install PyMuPDF Pillow requests")
    sys.exit(1)


class PDFToFlipbook:
    def __init__(self, pdf_path, output_dir="flipbook_output", dpi=300):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.dpi = dpi
        self.pages_dir = self.output_dir / "pages"
        self.assets_dir = self.output_dir / "assets"
        self.js_dir = self.assets_dir / "js"
        self.css_dir = self.assets_dir / "css"
        
    def create_directories(self):
        """Create the required directory structure."""
        for directory in [self.output_dir, self.pages_dir, self.js_dir, self.css_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
    def extract_pdf_pages(self):
        """Extract each page of the PDF as high-resolution images."""
        print(f"Extracting pages from {self.pdf_path}...")
        
        doc = fitz.open(self.pdf_path)
        total_pages = len(doc)
        
        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            
            # Create a matrix for high-resolution rendering
            mat = fitz.Matrix(self.dpi / 72, self.dpi / 72)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image for better quality control
            img_data = pix.tobytes("png")
            img = Image.open(BytesIO(img_data))
            
            # Save as high-quality JPEG
            page_filename = f"page{page_num + 1:03d}.jpg"
            page_path = self.pages_dir / page_filename
            img.save(page_path, "JPEG", quality=95, optimize=True)
            
            print(f"Extracted page {page_num + 1}/{total_pages}")
            
        doc.close()
        return total_pages
        
    def download_flipbook_library(self):
        """Download and save the StPageFlip library locally."""
        print("Downloading StPageFlip library...")
        
        # StPageFlip library (lightweight and modern)
        js_url = "https://unpkg.com/page-flip@2.0.7/dist/js/page-flip.browser.js"
        css_url = "https://unpkg.com/page-flip@2.0.7/dist/css/page-flip.css"
        
        try:
            # Download JS
            js_response = requests.get(js_url, timeout=30)
            js_response.raise_for_status()
            with open(self.js_dir / "page-flip.js", "w", encoding="utf-8") as f:
                f.write(js_response.text)
                
            # Download CSS
            css_response = requests.get(css_url, timeout=30)
            css_response.raise_for_status()
            with open(self.css_dir / "page-flip.css", "w", encoding="utf-8") as f:
                f.write(css_response.text)
                
            print("Successfully downloaded StPageFlip library")
            return True
            
        except Exception as e:
            print(f"Failed to download library: {e}")
            print("Using fallback embedded library...")
            return self.create_fallback_library()
            
    def create_fallback_library(self):
        """Create a simple fallback flipbook implementation."""
        # Simple CSS-based flipbook
        css_content = """
/* Simple Flipbook Styles */
.flipbook-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 20px;
    font-family: Arial, sans-serif;
}

.flipbook {
    position: relative;
    width: 100%;
    height: 600px;
    margin: 0 auto;
    perspective: 1000px;
    background: #f0f0f0;
    border-radius: 10px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.page {
    position: absolute;
    width: 50%;
    height: 100%;
    background: white;
    border: 1px solid #ddd;
    transform-origin: left center;
    transition: transform 0.6s ease-in-out;
    backface-visibility: hidden;
}

.page img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    display: block;
}

.page.flipped {
    transform: rotateY(-180deg);
}

.page.right {
    right: 0;
    transform-origin: right center;
}

.page.right.flipped {
    transform: rotateY(180deg);
}

.controls {
    text-align: center;
    margin: 20px 0;
}

.btn {
    background: #007bff;
    color: white;
    border: none;
    padding: 10px 20px;
    margin: 0 10px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
}

.btn:hover {
    background: #0056b3;
}

.btn:disabled {
    background: #ccc;
    cursor: not-allowed;
}

.page-counter {
    margin: 20px 0;
    font-size: 18px;
    color: #333;
}
"""
        
        js_content = """
class SimpleFlipbook {
    constructor(container, pages) {
        this.container = container;
        this.pages = pages;
        this.currentPage = 0;
        this.totalPages = pages.length;
        this.init();
    }
    
    init() {
        this.createHTML();
        this.bindEvents();
        this.updateDisplay();
    }
    
    createHTML() {
        this.container.innerHTML = `
            <div class="flipbook-container">
                <div class="page-counter">
                    <span id="current-page">1</span> / <span id="total-pages">${this.totalPages}</span>
                </div>
                <div class="flipbook" id="flipbook">
                    ${this.pages.map((page, index) => `
                        <div class="page ${index % 2 === 1 ? 'right' : ''}" data-page="${index}">
                            <img src="${page}" alt="Page ${index + 1}" />
                        </div>
                    `).join('')}
                </div>
                <div class="controls">
                    <button class="btn" id="prev-btn">Previous</button>
                    <button class="btn" id="next-btn">Next</button>
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        document.getElementById('prev-btn').addEventListener('click', () => this.prevPage());
        document.getElementById('next-btn').addEventListener('click', () => this.nextPage());
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') this.prevPage();
            if (e.key === 'ArrowRight') this.nextPage();
        });
    }
    
    nextPage() {
        if (this.currentPage < this.totalPages - 1) {
            this.currentPage++;
            this.updateDisplay();
        }
    }
    
    prevPage() {
        if (this.currentPage > 0) {
            this.currentPage--;
            this.updateDisplay();
        }
    }
    
    updateDisplay() {
        const pages = document.querySelectorAll('.page');
        pages.forEach((page, index) => {
            if (index <= this.currentPage) {
                page.classList.add('flipped');
            } else {
                page.classList.remove('flipped');
            }
        });
        
        document.getElementById('current-page').textContent = this.currentPage + 1;
        document.getElementById('prev-btn').disabled = this.currentPage === 0;
        document.getElementById('next-btn').disabled = this.currentPage === this.totalPages - 1;
    }
}
"""
        
        # Save fallback files
        with open(self.css_dir / "page-flip.css", "w", encoding="utf-8") as f:
            f.write(css_content)
            
        with open(self.js_dir / "page-flip.js", "w", encoding="utf-8") as f:
            f.write(js_content)
            
        return True
        
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
    <link rel="stylesheet" href="assets/css/page-flip.css">
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 20px;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .main-container {{
            width: 100%;
            max-width: 1200px;
            padding: 20px;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 20px;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="main-container">
        <div class="header">
            <h1>📖 PDF Flipbook</h1>
            <p>Use arrow keys or buttons to navigate</p>
        </div>
        
        <div id="flipbook-container"></div>
        
        <div class="footer">
            <p>Generated with PDF to Flipbook Converter</p>
            <p><small>If this doesn't work due to browser security, run: <code>python3 -m http.server</code></small></p>
        </div>
    </div>
    
    <script src="assets/js/page-flip.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const pages = {page_images};
            const container = document.getElementById('flipbook-container');
            
            // Initialize the flipbook
            const flipbook = new SimpleFlipbook(container, pages);
            
            console.log('Flipbook initialized with', pages.length, 'pages');
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
        
        # Extract PDF pages
        total_pages = self.extract_pdf_pages()
        
        # Download/create flipbook library
        self.download_flipbook_library()
        
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
    parser = argparse.ArgumentParser(description="Convert PDF to HTML5 Flipbook")
    parser.add_argument("pdf_file", help="Path to the PDF file")
    parser.add_argument("-o", "--output", default="flipbook_output", 
                       help="Output directory name (default: flipbook_output)")
    parser.add_argument("-d", "--dpi", type=int, default=300,
                       help="DPI for page extraction (default: 300)")
    
    args = parser.parse_args()
    
    try:
        converter = PDFToFlipbook(args.pdf_file, args.output, args.dpi)
        zip_path = converter.convert()
        
        print(f"\n🎉 Your flipbook is ready!")
        print(f"📥 Download: {zip_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
