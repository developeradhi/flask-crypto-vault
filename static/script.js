document.addEventListener('DOMContentLoaded', () => {

    // ==========================================
    // AUTO-LOCK (IDLE DETECTION)
    // ==========================================
    let idleTime = 0;
    const idleTimeout = 3 * 60; // 3 minutes in seconds
    
    // Only apply idle detection if we are on the dashboard (not login screen)
    if(document.getElementById('main-tools')) {
        const resetIdle = () => { idleTime = 0; };
        window.addEventListener('mousemove', resetIdle);
        window.addEventListener('keypress', resetIdle);
        window.addEventListener('scroll', resetIdle);
        
        setInterval(() => {
            idleTime++;
            if(idleTime >= idleTimeout && !document.getElementById('lock-overlay')) {
                // Trigger Lock
                const overlay = document.createElement('div');
                overlay.id = 'lock-overlay';
                overlay.style.position = 'fixed';
                overlay.style.top = '0'; overlay.style.left = '0'; overlay.style.width = '100%'; overlay.style.height = '100%';
                overlay.style.backdropFilter = 'blur(20px)';
                overlay.style.backgroundColor = 'rgba(0,0,0,0.8)';
                overlay.style.zIndex = '9999';
                overlay.style.display = 'flex'; overlay.style.flexDirection = 'column'; overlay.style.justifyContent = 'center'; overlay.style.alignItems = 'center';
                
                overlay.innerHTML = `
                    <h2 style="font-size: 2.5rem; margin-bottom: 20px; font-weight: 800;">🔒 Vault Locked</h2>
                    <p style="color: var(--text-muted); margin-bottom: 30px;">You were idle for 3 minutes. Please unlock to continue.</p>
                    <input type="password" id="unlock-pwd" class="input-field" placeholder="Enter Password" style="max-width: 300px;">
                    <button id="unlock-btn" class="btn primary-btn mt-3" style="max-width: 300px;">Unlock</button>
                    <p id="unlock-error" class="error-message hidden" style="max-width: 300px;"></p>
                `;
                document.body.appendChild(overlay);
                
                document.getElementById('unlock-btn').addEventListener('click', async () => {
                    const pwd = document.getElementById('unlock-pwd').value;
                    const errEl = document.getElementById('unlock-error');
                    // Simple check against backend
                    try {
                        const res = await fetch('/api/auth/login', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ username: document.querySelector('.sidebar-header strong').innerText, password: pwd })
                        });
                        if(res.ok) {
                            document.body.removeChild(overlay);
                            resetIdle();
                        } else {
                            errEl.innerText = "Incorrect Password";
                            errEl.classList.remove('hidden');
                        }
                    } catch(e) {}
                });
            }
        }, 1000);
    }

    function showError(el, msg) {
        el.innerText = msg;
        el.classList.remove('hidden');
    }

    // ==========================================
    // AUTHENTICATION LOGIC & ZXCVBN
    // ==========================================
    const pwdInput = document.getElementById('password');
    if (pwdInput && document.getElementById('password-strength-container')) {
        pwdInput.addEventListener('input', () => {
            const val = pwdInput.value;
            const container = document.getElementById('password-strength-container');
            if(!val) { container.style.display = 'none'; return; }
            container.style.display = 'block';
            
            const result = zxcvbn(val);
            const bar = document.getElementById('password-strength-bar');
            const timeLabel = document.getElementById('password-crack-time');
            
            const colors = ['#ef4444', '#f97316', '#eab308', '#84cc16', '#22c55e'];
            bar.style.width = ((result.score + 1) * 20) + '%';
            bar.style.background = colors[result.score];
            timeLabel.innerText = "Crack time: " + result.crack_times_display.offline_slow_hashing_1e4_per_second;
        });
    }

    const authBtn = document.getElementById('auth-btn');
    if (authBtn) {
        authBtn.addEventListener('click', async () => {
            const username = document.getElementById('username').value;
            const pwd = document.getElementById('password').value;
            const errEl = document.getElementById('auth-error');
            const action = authBtn.dataset.action || (document.getElementById('email') ? 'register' : 'login');
            
            let email = '';
            if (action === 'register') {
                const emailInput = document.getElementById('email');
                if (emailInput) {
                    email = emailInput.value.trim();
                    if (!email) { showError(errEl, 'Email is required.'); return; }
                }
            }
            
            if (!username || !pwd) { showError(errEl, 'Username and password required.'); return; }
            
            errEl.classList.add('hidden');
            authBtn.disabled = true;
            authBtn.innerText = 'Processing...';

            try {
                const endpoint = action === 'register' ? '/api/auth/register' : '/api/auth/login';
                
                let bodyData = { username, password: pwd };
                if (action === 'register') {
                    const emailInput = document.getElementById('email');
                    if (emailInput) bodyData.email = emailInput.value.trim();
                }
                
                const res = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(bodyData)
                });
                const data = await res.json();
                
                if (res.ok) {
                    if (data.requires_2fa) {
                        window.location.href = '/2fa';
                    } else {
                        window.location.href = '/';
                    }
                } else {
                    showError(errEl, data.error || 'Authentication failed');
                    authBtn.disabled = false;
                    authBtn.innerText = action === 'register' ? 'Register & Generate Keys' : 'Login';
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
    // THEME SWITCHER
    // ==========================================
    const themeSwitcher = document.getElementById('theme-switcher');
    if(themeSwitcher) {
        themeSwitcher.addEventListener('change', (e) => {
            document.body.className = 'dashboard-body';
            if(e.target.value !== 'glass') {
                document.body.classList.add(`theme-${e.target.value}`);
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

    async function handleTextProcess(action) {
        const text = chatInput.value.trim();
        if(!text) return;
        chatError.classList.add('hidden');
        
        // DLP SCANNER (Data Loss Prevention)
        if(action === 'encrypt') {
            const ccRegex = /\b(?:\d[ -]*?){13,16}\b/g;
            const ssnRegex = /\b\d{3}-\d{2}-\d{4}\b/g;
            const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
            
            let warnings = [];
            if(ccRegex.test(text)) warnings.push("Credit Card Number");
            if(ssnRegex.test(text)) warnings.push("Social Security Number");
            if(emailRegex.test(text)) warnings.push("Email Address");
            
            if(warnings.length > 0) {
                const proceed = confirm(`DLP WARNING:\nWe detected sensitive information (${warnings.join(', ')}) in your text.\nAre you sure you want to encrypt and share this?`);
                if(!proceed) return;
            }
        }
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

    // ==========================================
    // BURN-NOTE (EPHEMERAL MESSAGES)
    // ==========================================
    const burnCreateBtn = document.getElementById('burn-create-btn');
    if(burnCreateBtn) {
        burnCreateBtn.addEventListener('click', async () => {
            const text = document.getElementById('burn-input').value.trim();
            const err = document.getElementById('burn-error');
            const resCont = document.getElementById('burn-result-container');
            const urlInput = document.getElementById('burn-url');
            if(!text) return;
            
            err.classList.add('hidden');
            burnCreateBtn.disabled = true;
            burnCreateBtn.innerText = 'Generating...';
            
            try {
                const res = await fetch('/api/burn/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text})
                });
                const data = await res.json();
                if(res.ok) {
                    urlInput.value = data.url;
                    resCont.classList.remove('hidden');
                } else {
                    showError(err, data.error);
                }
            } catch(e) {
                showError(err, "Connection error.");
            }
            burnCreateBtn.disabled = false;
            burnCreateBtn.innerText = 'Generate Burn Link';
        });
    }

    // ==========================================
    // RSA DIGITAL SIGNATURES
    // ==========================================
    const rsaSignBtn = document.getElementById('rsa-sign-btn');
    const rsaVerifyBtn = document.getElementById('rsa-verify-btn');
    const rsaInput = document.getElementById('rsa-input');
    const rsaSignature = document.getElementById('rsa-signature');
    const rsaResultCont = document.getElementById('rsa-result-container');
    const rsaResult = document.getElementById('rsa-result');
    const rsaError = document.getElementById('rsa-error');

    async function handleRsaProcess(action) {
        const message = rsaInput.value.trim();
        if(!message) return;
        rsaError.classList.add('hidden');
        
        let payload = { action, message };
        if (action === 'verify') {
            payload.signature = rsaSignature.value.trim();
            if(!payload.signature) { showError(rsaError, "Signature is required for verification"); return; }
        }

        try {
            const res = await fetch('/api/rsa', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if(res.ok) {
                rsaResult.value = data.result;
                rsaResultCont.classList.remove('hidden');
            } else {
                showError(rsaError, data.error);
                rsaResultCont.classList.add('hidden');
            }
        } catch(e) {
            showError(rsaError, 'Connection error');
        }
    }
    if(rsaSignBtn) rsaSignBtn.addEventListener('click', () => handleRsaProcess('sign'));
    if(rsaVerifyBtn) rsaVerifyBtn.addEventListener('click', () => handleRsaProcess('verify'));

    // ==========================================
    // HMAC FILE INTEGRITY
    // ==========================================
    const hmacTabs = document.querySelectorAll('.hmac-tab');
    const hmacHashGroup = document.getElementById('hmac-hash-group');
    const hmacActionBtn = document.getElementById('hmac-action-btn');
    const hmacFile = document.getElementById('hmac-file');
    const hmacExpected = document.getElementById('hmac-expected');
    const hmacStatus = document.getElementById('hmac-status');
    let currentHmacAction = 'generate';

    if(hmacTabs.length > 0) {
        hmacTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                hmacTabs.forEach(t => { t.classList.remove('active'); t.style.border='none'; t.style.color='var(--text-muted)'; });
                tab.classList.add('active');
                tab.style.color='white';
                
                currentHmacAction = tab.dataset.action;
                hmacStatus.classList.add('hidden');
                
                if(currentHmacAction === 'generate') {
                    hmacHashGroup.classList.add('hidden');
                    hmacActionBtn.innerText = 'Generate Hash';
                } else {
                    hmacHashGroup.classList.remove('hidden');
                    hmacActionBtn.innerText = 'Verify File';
                }
            });
        });

        hmacActionBtn.addEventListener('click', async () => {
            if(!hmacFile.files[0]) {
                showError(hmacStatus, 'Please select a file.');
                return;
            }
            if(currentHmacAction === 'verify' && !hmacExpected.value.trim()) {
                showError(hmacStatus, 'Please enter the expected hash.');
                return;
            }

            hmacStatus.classList.add('hidden');
            hmacActionBtn.disabled = true;
            hmacActionBtn.innerText = 'Processing...';

            const formData = new FormData();
            formData.append('file', hmacFile.files[0]);
            formData.append('action', currentHmacAction);
            if(currentHmacAction === 'verify') formData.append('hmac', hmacExpected.value.trim());

            try {
                const response = await fetch('/api/hmac', { method: 'POST', body: formData });
                const data = await response.json();
                
                if(response.ok) {
                    if (currentHmacAction === 'generate') {
                        hmacStatus.innerHTML = `<span style="color: #4ade80">Generated HMAC:</span><br><code style="background: rgba(0,0,0,0.5); padding: 5px; border-radius: 4px;">${data.result}</code>`;
                    } else {
                        hmacStatus.innerHTML = `<span style="color: #4ade80">✓ ${data.result}</span>`;
                    }
                } else {
                    hmacStatus.innerHTML = `<span style="color: #ef4444">❌ ${data.error}</span>`;
                }
                hmacStatus.classList.remove('hidden');
            } catch (err) {
                hmacStatus.innerHTML = `<span style="color: #ef4444">Connection Error</span>`;
                hmacStatus.classList.remove('hidden');
            }
            hmacActionBtn.disabled = false;
            hmacActionBtn.innerText = currentHmacAction === 'generate' ? 'Generate Hash' : 'Verify File';
        });
    }

    // ==========================================
    // 2FA SETUP
    // ==========================================
    const setup2FaBtn = document.getElementById('setup-2fa-btn');
    if(setup2FaBtn) {
        setup2FaBtn.addEventListener('click', async () => {
            setup2FaBtn.disabled = true;
            try {
                const res = await fetch('/api/auth/enable-2fa', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({}) });
                const data = await res.json();
                if(res.ok) {
                    document.getElementById('2fa-setup-area').classList.remove('hidden');
                    setup2FaBtn.classList.add('hidden');
                    
                    // Generate QR
                    new QRCode(document.getElementById("qrcode"), {
                        text: data.uri,
                        width: 150,
                        height: 150
                    });
                }
            } catch(e) {}
        });
    }

    const enable2FaBtn = document.getElementById('enable-2fa-btn');
    if(enable2FaBtn) {
        enable2FaBtn.addEventListener('click', async () => {
            const code = document.getElementById('2fa-verify-code').value;
            const errEl = document.getElementById('2fa-setup-error');
            if(!code) return;
            
            try {
                const res = await fetch('/api/auth/enable-2fa', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ code })
                });
                const data = await res.json();
                if(res.ok) {
                    location.reload(); // Reload to show 2FA as enabled
                } else {
                    showError(errEl, data.error);
                }
            } catch(e) {}
        });
    }

});
