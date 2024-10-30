from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
from dotenv import load_dotenv
from urllib.parse import parse_qs
import subprocess
import shutil

# Load environment variables
load_dotenv()

# Get configuration from environment
SERVER_HOST = os.getenv('SERVER_HOST', 'localhost')
SERVER_PORT = int(os.getenv('SERVER_PORT', 8000))
IMAGE_DIR = os.getenv('IMAGE_DIR', 'img')
SOURCE_FILE = os.getenv('SOURCE_FILE', 'source.txt')
TARGET_FILE = os.getenv('TARGET_FILE', 'target.txt')
EXTENSIONS_FILE = os.getenv('EXTENSIONS_FILE', 'extensions.txt')

# Add file editor section to the HTML template
FILE_EDITOR = """
    <div class="editor-section">
        <div class="editor-group">
            <h3>Edit Names List</h3>
            <div class="editor-container">
                <textarea id="namesEditor" rows="10" placeholder="Enter names (one per line)"></textarea>
                <button onclick="saveNames()">Save Names</button>
            </div>
            <div id="namesEditorMessage" class="message"></div>
        </div>
        
        <div class="editor-group">
            <h3>Edit Extensions List</h3>
            <div class="editor-container">
                <textarea id="extensionsEditor" rows="10" placeholder="Enter extensions (one per line)"></textarea>
                <button onclick="saveExtensions()">Save Extensions</button>
            </div>
            <div id="extensionsEditorMessage" class="message"></div>
        </div>
    </div>
"""

# Update management buttons section
MANAGEMENT_BUTTONS = """
    <div class="management-section">
        <div class="button-group">
            <button class="danger-button" onclick="removeAllImages()">Remove All Images</button>
            <button class="danger-button" onclick="removeAllDomains()">Remove All Domains</button>
            <button class="danger-button" onclick="removeAllNames()">Remove All Names</button>
        </div>
        <div class="button-group" style="margin-top: 10px;">
            <button class="action-button" onclick="regenerateScreenshots()">Regenerate All Screenshots</button>
        </div>
        <div id="managementMessage" class="message"></div>
    </div>
"""

# Add regeneration script
REGENERATE_SCRIPT = """
    async function regenerateScreenshots() {
        if (!confirm('Are you sure you want to regenerate all screenshots? This may take some time.')) {
            return;
        }
        
        try {
            showMessage('managementMessage', 'Starting screenshot regeneration...', true);
            const response = await fetch('/regenerate-screenshots', { method: 'POST' });
            const result = await response.json();
            showMessage('managementMessage', result.message, result.success);
            if (result.success) {
                updateGallery();
            }
        } catch (error) {
            showMessage('managementMessage', 'Error regenerating screenshots', false);
        }
    }
"""

# Add editor scripts
EDITOR_SCRIPTS = """
    async function loadFileContent() {
        try {
            const [namesResponse, extensionsResponse] = await Promise.all([
                fetch('/file-content?file=source'),
                fetch('/file-content?file=extensions')
            ]);
            
            const namesContent = await namesResponse.text();
            const extensionsContent = await extensionsResponse.text();
            
            document.getElementById('namesEditor').value = namesContent;
            document.getElementById('extensionsEditor').value = extensionsContent;
        } catch (error) {
            console.error('Error loading file content:', error);
        }
    }
    
    async function saveNames() {
        const content = document.getElementById('namesEditor').value;
        await saveFileContent('source', content, 'namesEditorMessage');
    }
    
    async function saveExtensions() {
        const content = document.getElementById('extensionsEditor').value;
        await saveFileContent('extensions', content, 'extensionsEditorMessage');
    }
    
    async function saveFileContent(fileType, content, messageId) {
        try {
            const response = await fetch('/save-file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `file=${fileType}&content=${encodeURIComponent(content)}`
            });
            
            const result = await response.json();
            showMessage(messageId, result.message, result.success);
            
            if (result.success && fileType === 'source') {
                // Regenerate domains after saving names
                await fetch('/regenerate-domains', { method: 'POST' });
            }
        } catch (error) {
            showMessage(messageId, 'Error saving file', false);
        }
    }
    
    // Load file content when page loads
    document.addEventListener('DOMContentLoaded', loadFileContent);
"""

# Add new style for action button
ACTION_BUTTON_STYLE = """
    .action-button {
        padding: 10px 20px;
        background: #28a745;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
    }
    .action-button:hover {
        background: #218838;
    }
    .editor-section {
        display: flex;
        gap: 20px;
        margin-bottom: 20px;
    }
    .editor-group {
        flex: 1;
        background: #fff;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .editor-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    textarea {
        width: 100%;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-family: monospace;
        resize: vertical;
    }
    .refresh-button {
        padding: 5px 10px;
        background: #28a745;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.9em;
    }
    .refresh-button:hover {
        background: #218838;
    }
"""

# Update the original HTML template to include new button and styles
VIEWER_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Screenshot Viewer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f0f0f0;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: #fff;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .stats {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-box {
            background: #fff;
            padding: 15px;
            border-radius: 5px;
            flex: 1;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .input-section {
            background: #fff;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            display: flex;
            gap: 20px;
        }
        .input-group {
            flex: 1;
            padding: 15px;
            background: #f8f8f8;
            border-radius: 5px;
        }
        .input-group h3 {
            margin-top: 0;
        }
        .input-form {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            padding: 8px 15px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background: #0056b3;
        }
        .message {
            margin-top: 10px;
            padding: 10px;
            border-radius: 4px;
            display: none;
        }
        .success {
            background: #d4edda;
            color: #155724;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
        }
        .image-card {
            background: #fff;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .image-card img {
            width: 100%;
            height: auto;
            border-radius: 3px;
        }
        .image-card .title {
            margin-top: 10px;
            font-size: 14px;
            color: #666;
            text-align: center;
            word-break: break-all;
        }
        """ + ACTION_BUTTON_STYLE + """
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Screenshot Viewer</h1>
            <p>Auto-refreshing every second</p>
        </div>
        
        """ + FILE_EDITOR + """
        
        <div class="input-section">
            <div class="input-group">
                <h3>Add Domain Name</h3>
                <div class="input-form">
                    <input type="text" id="domainInput" placeholder="Enter domain (e.g., example.com)">
                    <button onclick="addDomain()">Add Domain</button>
                </div>
                <div id="domainMessage" class="message"></div>
            </div>
            
            <div class="input-group">
                <h3>Add Base Name</h3>
                <div class="input-form">
                    <input type="text" id="nameInput" placeholder="Enter name (e.g., example)">
                    <button onclick="addName()">Add Name</button>
                </div>
                <div id="nameMessage" class="message"></div>
            </div>
        </div>
        
        """ + MANAGEMENT_BUTTONS + """
        
        <div class="stats">
            <div class="stat-box">
                <h3>Total Screenshots</h3>
                <div id="totalCount">0</div>
            </div>
            <div class="stat-box">
                <h3>Last Update</h3>
                <div id="lastUpdate">-</div>
            </div>
        </div>
        
        <div class="gallery" id="imageGallery"></div>
    </div>

    <script>
        const IMAGE_DIR = '""" + IMAGE_DIR + """';
        
        function showMessage(elementId, message, isSuccess) {
            const element = document.getElementById(elementId);
            element.textContent = message;
            element.className = `message ${isSuccess ? 'success' : 'error'}`;
            element.style.display = 'block';
            setTimeout(() => {
                element.style.display = 'none';
            }, 3000);
        }
        
        function updateGallery() {
            fetch('/images')
                .then(response => response.json())
                .then(images => {
                    const gallery = document.getElementById('imageGallery');
                    const totalCount = document.getElementById('totalCount');
                    const lastUpdate = document.getElementById('lastUpdate');
                    
                    totalCount.textContent = images.length;
                    lastUpdate.textContent = new Date().toLocaleTimeString();
                    
                    gallery.innerHTML = '';
                    
                    images.forEach(image => {
                        const card = document.createElement('div');
                        card.className = 'image-card';
                        
                        const img = document.createElement('img');
                        img.src = `${IMAGE_DIR}/${image}`;
                        img.alt = image;
                        
                        const title = document.createElement('div');
                        title.className = 'title';
                        title.textContent = image.replace(/_/g, '.').replace('.png', '');
                        
                        card.appendChild(img);
                        card.appendChild(title);
                        gallery.appendChild(card);
                    });
                })
                .catch(error => console.error('Error:', error));
        }
        
        """ + EDITOR_SCRIPTS + """
        """ + REGENERATE_SCRIPT + """

        updateGallery();
        setInterval(updateGallery, 1000);
    </script>
</body>
</html>
"""

class ImageListHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(VIEWER_HTML.encode())
            
        elif self.path == '/images':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            image_list = []
            if os.path.exists(IMAGE_DIR):
                image_list = [f for f in os.listdir(IMAGE_DIR) if f.endswith('.png')]
                image_list.sort()
            
            self.wfile.write(json.dumps(image_list).encode())
            
        elif self.path.startswith('/file-content'):
            params = parse_qs(self.path.split('?')[1])
            file_type = params.get('file', [''])[0]
            
            file_path = ''
            if file_type == 'source':
                file_path = SOURCE_FILE
            elif file_type == 'extensions':
                file_path = EXTENSIONS_FILE
                
            if file_path and os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(content.encode())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''
        params = parse_qs(post_data)
        
        response = {'success': False, 'message': 'Invalid request'}
        
        if self.path == '/regenerate-screenshots':
            try:
                # Clear existing screenshots
                if os.path.exists(IMAGE_DIR):
                    shutil.rmtree(IMAGE_DIR)
                    os.makedirs(IMAGE_DIR)
                
                # Run screenshot script
                result = subprocess.run(['python3', 'screenshot.py'], 
                                     capture_output=True, 
                                     text=True)
                
                if result.returncode == 0:
                    response = {
                        'success': True,
                        'message': 'Screenshots regenerated successfully'
                    }
                else:
                    response = {
                        'success': False,
                        'message': f'Error regenerating screenshots: {result.stderr}'
                    }
            except Exception as e:
                response = {
                    'success': False,
                    'message': f'Error regenerating screenshots: {str(e)}'
                }
                
        elif self.path == '/save-file':
            file_type = params.get('file', [''])[0]
            content = params.get('content', [''])[0]
            
            file_path = ''
            if file_type == 'source':
                file_path = SOURCE_FILE
            elif file_type == 'extensions':
                file_path = EXTENSIONS_FILE
                
            if file_path:
                try:
                    with open(file_path, 'w') as f:
                        f.write(content)
                    response = {'success': True, 'message': f'File saved successfully'}
                except Exception as e:
                    response = {'success': False, 'message': f'Error saving file: {str(e)}'}
                    
        elif self.path == '/regenerate-domains':
            try:
                subprocess.run(['python3', 'domaingen.py'])
                response = {'success': True, 'message': 'Domains regenerated successfully'}
            except Exception as e:
                response = {'success': False, 'message': f'Error regenerating domains: {str(e)}'}
                
        elif self.path == '/remove-images':
            try:
                if os.path.exists(IMAGE_DIR):
                    shutil.rmtree(IMAGE_DIR)
                    os.makedirs(IMAGE_DIR)
                response = {'success': True, 'message': 'All images removed successfully'}
            except Exception as e:
                response = {'success': False, 'message': f'Error removing images: {str(e)}'}
                
        elif self.path == '/remove-domains':
            try:
                with open(TARGET_FILE, 'w') as f:
                    f.write('')
                response = {'success': True, 'message': 'All domains removed successfully'}
            except Exception as e:
                response = {'success': False, 'message': f'Error removing domains: {str(e)}'}
                
        elif self.path == '/remove-names':
            try:
                with open(SOURCE_FILE, 'w') as f:
                    f.write('')
                with open(TARGET_FILE, 'w') as f:
                    f.write('')
                response = {'success': True, 'message': 'All names and generated domains removed successfully'}
            except Exception as e:
                response = {'success': False, 'message': f'Error removing names: {str(e)}'}
                
        elif self.path == '/add-domain':
            domain = params.get('domain', [''])[0].strip()
            if domain:
                try:
                    with open(TARGET_FILE, 'a') as f:
                        f.write(f"{domain}\n")
                    response = {'success': True, 'message': f'Domain {domain} added successfully'}
                except Exception as e:
                    response = {'success': False, 'message': f'Error adding domain: {str(e)}'}
            else:
                response = {'success': False, 'message': 'Domain cannot be empty'}
                
        elif self.path == '/add-name':
            name = params.get('name', [''])[0].strip()
            if name:
                try:
                    with open(SOURCE_FILE, 'a') as f:
                        f.write(f"{name}\n")
                    subprocess.run(['python3', 'domaingen.py'])
                    response = {'success': True, 'message': f'Name {name} added and domains generated'}
                except Exception as e:
                    response = {'success': False, 'message': f'Error adding name: {str(e)}'}
            else:
                response = {'success': False, 'message': 'Name cannot be empty'}
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

def run_server():
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
        
    server = HTTPServer((SERVER_HOST, SERVER_PORT), ImageListHandler)
    print(f"Server started at http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"View the gallery at http://{SERVER_HOST}:{SERVER_PORT}/")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
