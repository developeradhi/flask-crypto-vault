document.addEventListener('DOMContentLoaded', () => {

    // Helper: Show Error
    function showError(el, msg) {
        el.innerText = msg;
        el.classList.remove('hidden');
    }

    // ==========================================
    // AUTHENTICATION LOGIC
    // ==========================================
    const authBtn = document.getElementById('auth-btn');
    if (authBtn) {
        authBtn.addEventListener('click', async () => {
            const pwd = document.getElementById('password').value;
            const errEl = document.getElementById('auth-error');
            const action = authBtn.dataset.action;
            
            if (!pwd) { showError(errEl, 'Password is required.'); return; }
            
            errEl.classList.add('hidden');
            authBtn.disabled = true;
            authBtn.innerText = 'Processing...';

            try {
                const endpoint = action === 'setup' ? '/api/auth/setup' : '/api/auth/login';
                const res = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password: pwd })
                });
                const data = await res.json();
                
                if (res.ok) {
                    window.location.href = '/';
                } else {
                    showError(errEl, data.error || 'Authentication failed');
                    authBtn.disabled = false;
                    authBtn.innerText = action === 'setup' ? 'Set Password' : 'Unlock Vault';
                }
            } catch (e) {
                showError(errEl, 'Server connection error.');
                authBtn.disabled = false;
            }
        });
    }

    // ==========================================
    // DASHBOARD NAVIGATION
    // ==========================================
    const navItems = document.querySelectorAll('.nav-item');
    const toolSections = document.querySelectorAll('.tool-section');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            const targetId = item.dataset.target;
            toolSections.forEach(sec => {
                if(sec.id === targetId) sec.classList.remove('hidden');
                else sec.classList.add('hidden');
            });
        });
    });

    // ==========================================
    // KEY GENERATION
    // ==========================================
    const genKeyBtn = document.getElementById('generate-key-btn');
    if (genKeyBtn) {
        genKeyBtn.addEventListener('click', async () => {
            genKeyBtn.disabled = true;
            genKeyBtn.innerText = 'Generating...';
            try {
                const res = await fetch('/api/generate-key', { method: 'POST' });
                const data = await res.json();
                if (data.success) {
                    location.reload(); // Reload to show main tools
                } else {
                    document.getElementById('key-status-msg').innerText = data.message;
                    genKeyBtn.disabled = false;
                }
            } catch (e) {
                genKeyBtn.disabled = false;
            }
        });
    }

    // ==========================================
    // FILE VAULT (ENCRYPT/DECRYPT/SHRED)
    // ==========================================
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadStatus = document.getElementById('upload-status');
    const vaultError = document.getElementById('error-message');
    const modeRadios = document.querySelectorAll('input[name="mode"]');
    const shredContainer = document.getElementById('shredder-container');

    if (dropZone) {
        // Toggle shredder visibility based on mode
        modeRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                if(e.target.value === 'encrypt') shredContainer.classList.remove('hidden');
                else shredContainer.classList.add('hidden');
            });
        });

        dropZone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) processFile(e.target.files[0]);
        });
        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault(); dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) processFile(e.dataTransfer.files[0]);
        });

        async function processFile(file) {
            vaultError.classList.add('hidden');
            uploadStatus.classList.remove('hidden');
            
            const action = document.querySelector('input[name="mode"]:checked').value;
            const doShred = document.getElementById('shred-checkbox').checked;
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('action', action);
            if(doShred && action === 'encrypt') formData.append('shred', 'true');

            try {
                const response = await fetch('/api/process', { method: 'POST', body: formData });
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Unknown error occurred');
                }

                const blob = await response.blob();
                let filename = action === 'encrypt' ? file.name + '.enc' : file.name.replace('.enc', '');
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none'; a.href = url; a.download = filename;
                document.body.appendChild(a); a.click(); window.URL.revokeObjectURL(url);
                
                uploadStatus.innerHTML = '<span style="color: #4ade80">✓ Success! File downloaded.</span>';
                setTimeout(() => {
                    uploadStatus.classList.add('hidden');
                    uploadStatus.innerHTML = '<div class="spinner"></div><span>Processing...</span>';
                }, 3000);

            } catch (err) {
                uploadStatus.classList.add('hidden');
                showError(vaultError, err.message);
            }
            fileInput.value = '';
        }
    }

    // ==========================================
    // SECRET CHAT
    // ==========================================
    const chatEncryptBtn = document.getElementById('chat-encrypt-btn');
    const chatDecryptBtn = document.getElementById('chat-decrypt-btn');
    const chatInput = document.getElementById('chat-input');
    const chatResultCont = document.getElementById('chat-result-container');
    const chatResult = document.getElementById('chat-result');
    const chatError = document.getElementById('chat-error');
    const copyBtn = document.getElementById('copy-btn');

    async function handleTextProcess(action) {
        const text = chatInput.value.trim();
        if(!text) return;
        chatError.classList.add('hidden');
        try {
            const res = await fetch('/api/text', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action, text })
            });
            const data = await res.json();
            if(res.ok) {
                chatResult.value = data.result;
                chatResultCont.classList.remove('hidden');
            } else {
                showError(chatError, data.error);
                chatResultCont.classList.add('hidden');
            }
        } catch(e) {
            showError(chatError, 'Connection error');
        }
    }

    if(chatEncryptBtn) chatEncryptBtn.addEventListener('click', () => handleTextProcess('encrypt'));
    if(chatDecryptBtn) chatDecryptBtn.addEventListener('click', () => handleTextProcess('decrypt'));
    if(copyBtn) {
        copyBtn.addEventListener('click', () => {
            chatResult.select();
            document.execCommand('copy');
            copyBtn.innerText = 'Copied!';
            setTimeout(() => copyBtn.innerText = 'Copy to Clipboard', 2000);
        });
    }

    // ==========================================
    // STEGANOGRAPHY
    // ==========================================
    const stegoTabs = document.querySelectorAll('.stego-tab');
    const stegoTextGroup = document.getElementById('stego-text-group');
    const stegoResultGroup = document.getElementById('stego-result-group');
    const stegoActionBtn = document.getElementById('stego-action-btn');
    const stegoImage = document.getElementById('stego-image');
    const stegoText = document.getElementById('stego-text');
    const stegoExtracted = document.getElementById('stego-extracted-text');
    const stegoStatus = document.getElementById('stego-status');
    let currentStegoAction = 'hide';

    if(stegoTabs.length > 0) {
        stegoTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                stegoTabs.forEach(t => { t.classList.remove('active'); t.style.border='none'; t.style.color='var(--text-muted)'; });
                tab.classList.add('active');
                tab.style.color='white';
                
                currentStegoAction = tab.dataset.action;
                stegoStatus.classList.add('hidden');
                
                if(currentStegoAction === 'hide') {
                    stegoTextGroup.classList.remove('hidden');
                    stegoResultGroup.classList.add('hidden');
                    stegoActionBtn.innerText = 'Hide & Download';
                } else {
                    stegoTextGroup.classList.add('hidden');
                    stegoResultGroup.classList.add('hidden');
                    stegoActionBtn.innerText = 'Extract Data';
                }
            });
        });

        stegoActionBtn.addEventListener('click', async () => {
            if(!stegoImage.files[0]) {
                showError(stegoStatus, 'Please select a PNG image.');
                return;
            }
            if(currentStegoAction === 'hide' && !stegoText.value.trim()) {
                showError(stegoStatus, 'Please enter text to hide.');
                return;
            }

            stegoStatus.classList.add('hidden');
            stegoResultGroup.classList.add('hidden');
            stegoActionBtn.disabled = true;
            stegoActionBtn.innerText = 'Processing...';

            const formData = new FormData();
            formData.append('image', stegoImage.files[0]);
            formData.append('action', currentStegoAction);
            if(currentStegoAction === 'hide') formData.append('text', stegoText.value);

            try {
                const response = await fetch('/api/stego', { method: 'POST', body: formData });
                
                if(currentStegoAction === 'hide') {
                    if(!response.ok) {
                        const err = await response.json();
                        throw new Error(err.error);
                    }
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none'; a.href = url; a.download = 'secret_' + stegoImage.files[0].name;
                    document.body.appendChild(a); a.click(); window.URL.revokeObjectURL(url);
                    
                    stegoStatus.innerHTML = '<span style="color: #4ade80">✓ Image downloaded!</span>';
                    stegoStatus.classList.remove('hidden');
                } else {
                    const data = await response.json();
                    if(response.ok) {
                        stegoExtracted.value = data.result;
                        stegoResultGroup.classList.remove('hidden');
                    } else {
                        throw new Error(data.error);
                    }
                }
            } catch (err) {
                stegoStatus.innerHTML = `<span style="color: #ef4444">${err.message}</span>`;
                stegoStatus.classList.remove('hidden');
            }
            
            stegoActionBtn.disabled = false;
            stegoActionBtn.innerText = currentStegoAction === 'hide' ? 'Hide & Download' : 'Extract Data';
        });
    }

});
