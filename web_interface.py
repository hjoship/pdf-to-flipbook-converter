#!/usr/bin/env python3
"""
Web Interface for PDF to HTML5 Flipbook Converter
Provides a simple web UI for uploading PDFs and downloading flipbooks.
"""

import os
import tempfile
import shutil
from pathlib import Path
from flask import Flask, request, render_template_string, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from simple_flipbook_converter import SimpleFlipbookConverter

app = Flask(__name__)
app.secret_key = 'flipbook_converter_secret_key'
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max file size

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF to Flipbook Converter</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 600px;
            width: 100%;
            text-align: center;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .upload-area {
            border: 3px dashed #ddd;
            border-radius: 10px;
            padding: 40px 20px;
            margin: 30px 0;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .upload-area:hover {
            border-color: #667eea;
            background: #f8f9ff;
        }
        
        .upload-area.dragover {
            border-color: #667eea;
            background: #f0f4ff;
        }
        
        .upload-icon {
            font-size: 3em;
            color: #ddd;
            margin-bottom: 20px;
        }
        
        .upload-text {
            color: #666;
            font-size: 1.1em;
            margin-bottom: 15px;
        }
        
        .file-input {
            display: none;
        }
        
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s ease;
            margin: 10px;
        }
        
        .btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .progress {
            display: none;
            margin: 20px 0;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: #667eea;
            width: 0%;
            transition: width 0.3s ease;
            border-radius: 10px;
        }
        
        .alert {
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
            font-weight: bold;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .features {
            text-align: left;
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .features h3 {
            color: #333;
            margin-bottom: 15px;
        }
        
        .features ul {
            list-style: none;
            padding: 0;
        }
        
        .features li {
            padding: 5px 0;
            color: #666;
        }
        
        .features li:before {
            content: "✓ ";
            color: #28a745;
            font-weight: bold;
        }
        
        .file-info {
            background: #e9ecef;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            text-align: left;
        }
        
        .download-link {
            display: inline-block;
            background: #28a745;
            color: white;
            text-decoration: none;
            padding: 15px 30px;
            border-radius: 25px;
            margin: 20px 0;
            transition: all 0.3s ease;
        }
        
        .download-link:hover {
            background: #218838;
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📖 PDF to Flipbook</h1>
        <p class="subtitle">Convert your PDF into a beautiful HTML5 flipbook</p>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'success' if category == 'success' else 'error' }}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form id="uploadForm" method="post" enctype="multipart/form-data">
            <div class="upload-area" onclick="document.getElementById('file').click()">
                <div class="upload-icon">📄</div>
                <div class="upload-text">Click here or drag and drop your PDF file</div>
                <div class="upload-subtext">Maximum file size: 200MB</div>
                <input type="file" id="file" name="file" class="file-input" accept=".pdf">
            </div>
            
            <div class="file-info" id="fileInfo" style="display: none;">
                <strong>Selected file:</strong> <span id="fileName"></span><br>
                <strong>Size:</strong> <span id="fileSize"></span>
            </div>
            
            <button type="submit" class="btn" id="convertBtn">Convert to Flipbook</button>
        </form>
        
        <div class="progress" id="progress">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div id="progressText">Processing...</div>
        </div>
        
        <div class="features">
            <h3>Features:</h3>
            <ul>
                <li>High-resolution page extraction (300 DPI)</li>
                <li>Responsive HTML5 flipbook viewer</li>
                <li>Offline support - no internet required</li>
                <li>Keyboard navigation (arrow keys)</li>
                <li>Self-contained ZIP download</li>
                <li>Works on all modern browsers</li>
            </ul>
        </div>
    </div>
    
    <script>
        const uploadArea = document.querySelector('.upload-area');
        const fileInput = document.getElementById('file');
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const uploadForm = document.getElementById('uploadForm');
        const convertBtn = document.getElementById('convertBtn');
        const progress = document.getElementById('progress');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        // Drag and drop functionality
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].type === 'application/pdf') {
                fileInput.files = files;
                showFileInfo(files[0]);
            }
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                showFileInfo(e.target.files[0]);
            }
        });
        
        function showFileInfo(file) {
            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);
            fileInfo.style.display = 'block';
        }
        
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        uploadForm.addEventListener('submit', (e) => {
            if (!fileInput.files.length) {
                e.preventDefault();
                alert('Please select a PDF file first.');
                return;
            }
            
            convertBtn.disabled = true;
            convertBtn.textContent = 'Converting...';
            progress.style.display = 'block';
            
            // Simulate progress with proper completion
            let progressValue = 0;
            const progressInterval = setInterval(() => {
                progressValue += Math.random() * 10 + 5; // Faster progress
                if (progressValue > 95) {
                    progressValue = 95;
                    progressText.textContent = 'Finalizing...';
                }
                progressFill.style.width = progressValue + '%';
                
                if (progressValue < 25) {
                    progressText.textContent = 'Extracting PDF pages...';
                } else if (progressValue < 50) {
                    progressText.textContent = 'Processing images...';
                } else if (progressValue < 75) {
                    progressText.textContent = 'Generating flipbook...';
                } else if (progressValue < 95) {
                    progressText.textContent = 'Creating ZIP file...';
                }
            }, 300);
            
            // Store interval ID for cleanup
            window.conversionProgressInterval = progressInterval;
        });
        
        // Reset form function
        function resetForm() {
            convertBtn.disabled = false;
            convertBtn.textContent = 'Convert to Flipbook';
            progress.style.display = 'none';
            fileInfo.style.display = 'none';
            fileInput.value = '';
            progressFill.style.width = '0%';
            progressText.textContent = 'Processing...';
            
            // Clear any running progress interval
            if (window.conversionProgressInterval) {
                clearInterval(window.conversionProgressInterval);
                window.conversionProgressInterval = null;
            }
        }
        
        // Auto-reset form after successful download or error
        // This will be triggered when the page reloads or redirects
        window.addEventListener('beforeunload', () => {
            if (window.conversionProgressInterval) {
                clearInterval(window.conversionProgressInterval);
            }
        });
        
        // Reset form when page loads (in case of redirect back)
        window.addEventListener('load', () => {
            resetForm();
        });
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and file.filename.lower().endswith('.pdf'):
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                upload_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(upload_path)
                
                # Convert to flipbook
                output_name = f"flipbook_{filename[:-4]}"
                output_dir = os.path.join(OUTPUT_FOLDER, output_name)
                
                converter = SimpleFlipbookConverter(upload_path, output_dir)
                zip_path = converter.convert()
                
                # Clean up uploaded file
                os.remove(upload_path)
                
                # Store the zip file path in session for download
                from flask import session
                session['download_file'] = str(zip_path)
                session['download_name'] = f"{output_name}.zip"
                
                flash('Conversion successful! Your flipbook is ready for download.', 'success')
                return redirect(url_for('success', filename=f"{output_name}.zip"))
                
            except Exception as e:
                flash(f'Conversion failed: {str(e)}', 'error')
                # Clean up on error
                if os.path.exists(upload_path):
                    os.remove(upload_path)
                return redirect(request.url)
        else:
            flash('Please upload a valid PDF file', 'error')
            return redirect(request.url)
    
    return render_template_string(HTML_TEMPLATE)

@app.route('/success/<filename>')
def success(filename):
    """Success page with download link and auto-reset"""
    success_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Conversion Complete - PDF to Flipbook</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 20px;
        }
        .success-container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 500px;
            width: 100%;
            text-align: center;
        }
        .success-icon {
            font-size: 4em;
            color: #28a745;
            margin-bottom: 20px;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        .download-btn {
            background: #28a745;
            color: white;
            text-decoration: none;
            padding: 15px 30px;
            border-radius: 25px;
            display: inline-block;
            margin: 20px 0;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .download-btn:hover {
            background: #218838;
            transform: translateY(-2px);
        }
        .back-btn {
            background: #667eea;
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 20px;
            display: inline-block;
            margin: 10px;
            transition: all 0.3s ease;
        }
        .back-btn:hover {
            background: #5a6fd8;
        }
        .info {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="success-container">
        <div class="success-icon">🎉</div>
        <h1>Conversion Complete!</h1>
        <p>Your PDF has been successfully converted to an interactive HTML5 flipbook.</p>
        
        <a href="{{ url_for('download_file') }}" class="download-btn">📥 Download {{ filename }}</a>
        
        <div class="info">
            <h3>What's included:</h3>
            <ul>
                <li><strong>index.html</strong> - Double-click to view your flipbook</li>
                <li><strong>assets/</strong> - CSS and JavaScript files</li>
                <li><strong>pages/</strong> - High-resolution page images</li>
            </ul>
            
            <h3>How to use:</h3>
            <ol>
                <li>Extract the ZIP file</li>
                <li>Double-click <code>index.html</code></li>
                <li>Use arrow keys or buttons to navigate</li>
            </ol>
        </div>
        
        <a href="{{ url_for('index') }}" class="back-btn">Convert Another PDF</a>
    </div>
    
    <script>
        // Auto-download after 2 seconds
        setTimeout(function() {
            window.location.href = '{{ url_for("download_file") }}';
        }, 2000);
    </script>
</body>
</html>
    """
    return render_template_string(success_template, filename=filename)

@app.route('/download')
def download_file():
    from flask import session
    
    if 'download_file' not in session:
        flash('No file available for download.', 'error')
        return redirect(url_for('index'))
    
    download_path = session.pop('download_file')
    download_name = session.pop('download_name', 'flipbook.zip')
    
    if not os.path.exists(download_path):
        flash('Download file not found.', 'error')
        return redirect(url_for('index'))
    
    return send_file(download_path, as_attachment=True, download_name=download_name)

@app.errorhandler(413)
def too_large(e):
    flash('File too large! Please upload a PDF smaller than 200MB.', 'error')
    return redirect(url_for('index'))

@app.route('/health')
def health():
    return {'status': 'healthy', 'message': 'PDF to Flipbook Converter is running'}

if __name__ == '__main__':
    import os
    
    # Get port from environment variable (for deployment) or default to 8080
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("🚀 Starting PDF to Flipbook Converter Web Interface")
    if debug:
        print(f"📱 Open your browser and go to: http://localhost:{port}")
    print("📄 Upload a PDF file and get a beautiful HTML5 flipbook!")
    print("\nPress Ctrl+C to stop the server")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
