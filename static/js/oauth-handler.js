// OAuth Handler para capturar tokens desde fragmentos URL
(function() {
    'use strict';
    
    function handleOAuthCallback() {
        const hash = window.location.hash;
        if (hash && hash.includes('access_token')) {
            // Parsear los parámetros del fragmento
            const params = new URLSearchParams(hash.substring(1));
            const accessToken = params.get('access_token');
            const refreshToken = params.get('refresh_token');
            
            if (accessToken) {
                // Enviar el token al servidor
                fetch('/auth/callback-js', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        access_token: accessToken,
                        refresh_token: refreshToken
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = data.redirect_url;
                    } else {
                        window.location.href = '/register';
                    }
                })
                .catch(error => {
                    console.error('Error en OAuth:', error);
                    window.location.href = '/register';
                });
            }
        }
    }
    
    // Ejecutar cuando la página cargue
    document.addEventListener('DOMContentLoaded', handleOAuthCallback);
})();
