#!/usr/bin/env python3
"""
Create a simple test PDF without external dependencies
"""

import os
from pathlib import Path

def create_simple_pdf():
    """Create a simple PDF using built-in tools"""
    # Create HTML content
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Test PDF</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 40px; }
        .page { page-break-after: always; height: 100vh; }
        h1 { color: #667eea; text-align: center; }
    </style>
</head>
<body>
    <div class="page">
        <h1>Test PDF - Page 1</h1>
        <p>This is a test PDF to verify the flipbook converter works correctly.</p>
        <p>Features being tested:</p>
        <ul>
            <li>PDF page extraction</li>
            <li>Image conversion</li>
            <li>HTML flipbook generation</li>
        </ul>
    </div>
    
    <div class="page">
        <h1>Test PDF - Page 2</h1>
        <p>This is the second page of the test document.</p>
        <p>The converter should extract this page as a high-resolution image.</p>
    </div>
    
    <div class="page">
        <h1>Test PDF - Page 3</h1>
        <p>Final page of the test document.</p>
        <p>If you can see this in the flipbook, the conversion was successful!</p>
    </div>
</body>
</html>
"""
    
    # Save HTML file
    html_path = Path("test_document.html")
    with open(html_path, "w") as f:
        f.write(html_content)
    
    # Convert HTML to PDF using system tools
    pdf_path = Path("test_document.pdf")
    
    # Try different methods to create PDF
    try:
        # Method 1: Use wkhtmltopdf if available
        result = os.system(f"wkhtmltopdf {html_path} {pdf_path}")
        if result == 0:
            print(f"Created PDF using wkhtmltopdf: {pdf_path}")
            return pdf_path
    except:
        pass
    
    try:
        # Method 2: Use Chrome/Chromium headless
        result = os.system(f"google-chrome --headless --disable-gpu --print-to-pdf={pdf_path} {html_path}")
        if result == 0:
            print(f"Created PDF using Chrome: {pdf_path}")
            return pdf_path
    except:
        pass
    
    try:
        # Method 3: Use Safari (macOS)
        result = os.system(f"safari {html_path}")
        print("Please manually save the HTML as PDF using Safari's Print -> Save as PDF")
        return None
    except:
        pass
    
    print("Could not automatically create PDF. Please manually convert test_document.html to PDF")
    return html_path

if __name__ == "__main__":
    create_simple_pdf()
