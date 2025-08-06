#!/usr/bin/env python3
"""
Create a sample PDF for testing the flipbook converter
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
import os

def create_sample_pdf():
    filename = "sample_document.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Page 1 - Title Page
    c.setFillColor(HexColor('#667eea'))
    c.rect(0, 0, width, height, fill=1)
    
    c.setFillColor(HexColor('#ffffff'))
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredText(width/2, height-150, "Sample Document")
    
    c.setFont("Helvetica", 18)
    c.drawCentredText(width/2, height-200, "PDF to Flipbook Converter")
    
    c.setFont("Helvetica", 14)
    c.drawCentredText(width/2, height-250, "This is a sample PDF to demonstrate")
    c.drawCentredText(width/2, height-270, "the flipbook conversion process")
    
    c.showPage()
    
    # Page 2 - Features
    c.setFillColor(HexColor('#f8f9fa'))
    c.rect(0, 0, width, height, fill=1)
    
    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height-80, "Features")
    
    c.setFont("Helvetica", 14)
    features = [
        "• High-resolution page extraction (300 DPI)",
        "• Interactive HTML5 flipbook viewer",
        "• Offline support - no internet required",
        "• Keyboard navigation with arrow keys",
        "• Responsive design for all devices",
        "• Self-contained ZIP download",
        "• Beautiful page-turning animations"
    ]
    
    y_pos = height - 120
    for feature in features:
        c.drawString(70, y_pos, feature)
        y_pos -= 25
    
    c.showPage()
    
    # Page 3 - Instructions
    c.setFillColor(HexColor('#e9ecef'))
    c.rect(0, 0, width, height, fill=1)
    
    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height-80, "How to Use")
    
    c.setFont("Helvetica", 14)
    instructions = [
        "1. Upload your PDF file using the web interface",
        "2. Wait for the conversion process to complete",
        "3. Download the generated ZIP file",
        "4. Extract the ZIP file to a folder",
        "5. Double-click index.html to view your flipbook",
        "",
        "Navigation:",
        "• Use arrow keys (← →) to turn pages",
        "• Click Previous/Next buttons",
        "• View page counter for progress"
    ]
    
    y_pos = height - 120
    for instruction in instructions:
        if instruction.startswith("Navigation:"):
            c.setFont("Helvetica-Bold", 14)
        else:
            c.setFont("Helvetica", 14)
        c.drawString(70, y_pos, instruction)
        y_pos -= 20
    
    c.showPage()
    
    # Page 4 - Technical Details
    c.setFillColor(HexColor('#fff3cd'))
    c.rect(0, 0, width, height, fill=1)
    
    c.setFillColor(HexColor('#856404'))
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height-80, "Technical Details")
    
    c.setFont("Helvetica", 12)
    details = [
        "PDF Processing: PyMuPDF library for high-quality extraction",
        "Image Format: JPEG with 95% quality for optimal file size",
        "Resolution: 300 DPI for crisp, print-quality images",
        "Flipbook Library: Custom lightweight JavaScript implementation",
        "Browser Support: Chrome 60+, Firefox 55+, Safari 12+, Edge 79+",
        "",
        "Output Structure:",
        "├── index.html (main viewer)",
        "├── assets/",
        "│   ├── css/ (styling)",
        "│   └── js/ (flipbook logic)",
        "└── pages/ (extracted images)",
        "",
        "File Sizes:",
        "• Typical page: 200-500 KB (depending on content)",
        "• Complete flipbook: 2-10 MB for average documents"
    ]
    
    y_pos = height - 120
    for detail in details:
        if detail.startswith("Output Structure:") or detail.startswith("File Sizes:"):
            c.setFont("Helvetica-Bold", 12)
        else:
            c.setFont("Helvetica", 12)
        c.drawString(70, y_pos, detail)
        y_pos -= 15
    
    c.showPage()
    
    # Page 5 - Final Page
    c.setFillColor(HexColor('#d1ecf1'))
    c.rect(0, 0, width, height, fill=1)
    
    c.setFillColor(HexColor('#0c5460'))
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredText(width/2, height-150, "🎉 Conversion Complete!")
    
    c.setFont("Helvetica", 16)
    c.drawCentredText(width/2, height-200, "Your PDF has been successfully converted")
    c.drawCentredText(width/2, height-220, "to a beautiful HTML5 flipbook")
    
    c.setFont("Helvetica", 14)
    c.drawCentredText(width/2, height-280, "Enjoy your interactive flipbook experience!")
    
    c.save()
    print(f"Sample PDF created: {filename}")
    return filename

if __name__ == "__main__":
    try:
        create_sample_pdf()
    except ImportError:
        print("ReportLab not installed. Installing...")
        os.system("pip install reportlab")
        create_sample_pdf()
