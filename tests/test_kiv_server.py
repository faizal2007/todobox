#!/usr/bin/env python3
"""
Quick test server for KIV tab switching functionality
Run this and visit: http://localhost:8000
"""

from flask import Flask, render_template_string

app = Flask(__name__)

TEST_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>KIV Tab Switching Test</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/4.6.0/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h2>KIV Tab Switching Test</h2>
        
        <div class="alert alert-info">
            <strong>Testing Steps:</strong>
            <ol>
                <li>Open browser console (F12)</li>
                <li>Click "Simulate KIV Button Click" button</li>
                <li>Watch console messages</li>
                <li>See if tab switches automatically to KIV</li>
                <li>Or manually test: <a href="?tab=kiv">?tab=kiv</a></li>
            </ol>
        </div>
        
        <ul class="nav nav-tabs" id="taskTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <a class="nav-link active" id="uncompleted-tab" data-toggle="tab" href="#uncompleted" role="tab">
                    Uncompleted Tasks <span class="badge badge-secondary">3</span>
                </a>
            </li>
            <li class="nav-item" role="presentation">
                <a class="nav-link" id="kiv-tab" data-toggle="tab" href="#kiv" role="tab">
                    KIV <span class="badge badge-secondary">3</span>
                </a>
            </li>
        </ul>
        
        <div class="tab-content" id="taskTabsContent">
            <div class="tab-pane fade show active" id="uncompleted" role="tabpanel">
                <div class="mt-3">
                    <h4>Uncompleted Tasks</h4>
                    <button class="btn btn-warning" onclick="simulateKivClick()">Simulate KIV Button Click</button>
                </div>
            </div>
            
            <div class="tab-pane fade" id="kiv" role="tabpanel">
                <div class="mt-3">
                    <h4 class="text-success">✅ KIV Tab Active - Success!</h4>
                    <div class="alert alert-success">You're now viewing the KIV tab.</div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/4.6.0/js/bootstrap.bundle.min.js"></script>
    
    <script>
        function simulateKivClick() {
            console.log('🔄 Starting KIV simulation...');
            
            const newUrl = window.location.origin + window.location.pathname + '?tab=kiv';
            console.log('📍 Simulating redirect to:', newUrl);
            
            window.history.pushState({}, '', newUrl);
            console.log('✅ URL updated');
            
            setTimeout(function() {
                const urlParams = new URLSearchParams(window.location.search);
                const activeTab = urlParams.get('tab');
                console.log('🔍 Detected tab:', activeTab);
                
                if (activeTab === 'kiv') {
                    const kivTab = document.getElementById('kiv-tab');
                    console.log('📋 KIV tab element:', kivTab);
                    
                    if (kivTab) {
                        console.log('🔧 Using Bootstrap tab API...');
                        $(kivTab).tab('show');
                        console.log('✅ Tab switch executed');
                        
                        setTimeout(() => {
                            console.log('🧹 Cleaning URL...');
                            window.history.replaceState({}, '', window.location.pathname);
                        }, 300);
                    }
                }
            }, 100);
        }
        
        // Auto-switch on page load if tab=kiv
        $(document).ready(function() {
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('tab') === 'kiv') {
                console.log('🚀 Auto-switching to KIV tab...');
                simulateKivClick();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def test_kiv():
    # Ensure an application context exists when invoked directly by pytest
    with app.app_context():
        return render_template_string(TEST_HTML)

if __name__ == '__main__':
    print("🧪 Starting KIV tab test server...")
    print("📋 Visit: http://localhost:8000")
    print("📋 Test URL: http://localhost:8000?tab=kiv")
    app.run(host='localhost', port=8000, debug=False)