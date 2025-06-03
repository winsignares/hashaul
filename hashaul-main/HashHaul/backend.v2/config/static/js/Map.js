
class MapController {
    constructor() {
        this.API_BASE_URL = window.location.origin + '/api';
        this.token = localStorage.getItem('hashhaul_token');
        this.currentUser = null;
        this.map = null;
        this.markers = [];
        this.routePolyline = null;
        this.currentRoute = null;
        this.userRoutes = [];
        this.checkpoints = [];
        this.trackingInterval = null;
        this.isTracking = false;
        
        this.init();
    }

    async init() {
        if (!this.token) {
            this.redirectToLogin();
            return;
        }

        try {
            await this.verifyToken();
            this.setupEventListeners();
            this.initializeMap();
            await this.loadUserRoutes();
        } catch (error) {
            console.error('Error inicializando mapa:', error);
            this.redirectToLogin();
        }
    }

 
    async verifyToken() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/auth/verify`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error('Token inválido');
            }

            const data = await response.json();
            this.currentUser = data.usuario;
            this.updateUserInfo();
            
        } catch (error) {
            localStorage.removeItem('hashhaul_token');
            throw error;
        }
    }

    updateUserInfo() {
        document.getElementById('userName').textContent = this.currentUser.nombre;
        document.getElementById('userRole').textContent = this.currentUser.rol;

       
        const adminLink = document.getElementById('adminLink');
        if (['administrador', 'supervisor'].includes(this.currentUser.rol)) {
            adminLink.style.display = 'flex';
        } else {
            adminLink.style.display = 'none';
        }
    }

    redirectToLogin() {
        window.location.href = '/';
    }

  
    setupEventListeners() {
    
        document.getElementById('logoutBtn').addEventListener('click', () => {
            localStorage.removeItem('hashhaul_token');
            this.redirectToLogin();
        });

      
        document.getElementById('routeSelector').addEventListener('change', (e) => {
            const routeId = e.target.value;
            if (routeId) {
                this.loadRoute(parseInt(routeId));
            } else {
                this.clearRoute();
            }
        });

     
        document.getElementById('refreshMapBtn').addEventListener('click', () => {
            this.refreshMap();
        });

        document.getElementById('centerMapBtn').addEventListener('click', () => {
            this.centerOnUserLocation();
        });

        document.getElementById('toggleTrafficBtn').addEventListener('click', () => {
            this.toggleTraffic();
        });

        document.getElementById('toggleSatelliteBtn').addEventListener('click', () => {
            this.toggleSatellite();
        });

        document.getElementById('fullscreenBtn').addEventListener('click', () => {
            this.toggleFullscreen();
        });

      
        document.getElementById('trackingToggle').addEventListener('click', () => {
            this.toggleTracking();
        });

       
        this.setupModalListeners();
    }

    setupModalListeners() {
       
        const checkpointModal = document.getElementById('checkpointModal');
        document.getElementById('closeCheckpointModal').addEventListener('click', () => {
            checkpointModal.style.display = 'none';
        });
        document.getElementById('closeCheckpointBtn').addEventListener('click', () => {
            checkpointModal.style.display = 'none';
        });

        
        const incidentModal = document.getElementById('incidentModal');
        document.getElementById('closeIncidentModal').addEventListener('click', () => {
            incidentModal.style.display = 'none';
        });
        document.getElementById('cancelIncidentBtn').addEventListener('click', () => {
            incidentModal.style.display = 'none';
        });

       
        document.getElementById('incidentForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitIncident(e);
        });

      
        window.addEventListener('click', (e) => {
            if (e.target === checkpointModal) checkpointModal.style.display = 'none';
            if (e.target === incidentModal) incidentModal.style.display = 'none';
        });
    }


    initializeMap() {
        try {
          
            this.map = L.map('map').setView([10.9685, -74.7813], 13);

          
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                maxZoom: 19
            }).addTo(this.map);

           
            this.map.on('click', (e) => {
                this.onMapClick(e);
            });

           
            this.showLoading(false);

        } catch (error) {
            console.error('Error inicializando mapa:', error);
            this.showMessage('Error inicializando el mapa', 'error');
        }
    }

    onMapClick(e) {
        const lat = e.latlng.lat.toFixed(6);
        const lng = e.latlng.lng.toFixed(6);
        
        
        L.popup()
            .setLatLng(e.latlng)
            .setContent(`<div style="color: black; font-size: 12px;">
                <strong>Coordenadas:</strong><br>
                Lat: ${lat}<br>
                Lng: ${lng}
            </div>`)
            .openOn(this.map);
    }

 
    async apiRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            }
        };

        const response = await fetch(`${this.API_BASE_URL}${url}`, {
            ...defaultOptions,
            ...options,
            headers: { ...defaultOptions.headers, ...options.headers }
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Error en la solicitud' }));
            throw new Error(errorData.error || `Error ${response.status}: ${response.statusText}`);
        }

        return response.json();
    }

    async loadUserRoutes() {
    try {
        this.showLoading(true);
        console.log(' Cargando rutas del usuario...');

        let allRoutes = [];
        
        
        if (['administrador', 'supervisor'].includes(this.currentUser.rol)) {
            console.log(' Usuario admin - cargando todas las rutas');
            allRoutes = await this.apiRequest('/admin/rutas');
            console.log(' Rutas cargadas (admin):', allRoutes.length);
        } else {
            console.log(' Usuario conductor - cargando rutas específicas');
            allRoutes = await this.apiRequest(`/conductor/${this.currentUser.id}/rutas`);
            console.log(' Rutas específicas cargadas:', allRoutes.length);
        }

        this.userRoutes = allRoutes;
        console.log(' Rutas finales cargadas:', this.userRoutes.length);
        
        this.populateRouteSelector();

    } catch (error) {
        console.error(' Error general cargando rutas:', error);
        this.showMessage(`Error cargando rutas: ${error.message}`, 'error');
        
        // Si hay error, limpiamos las rutas
        this.userRoutes = [];
        this.populateRouteSelector();
    } finally {
        this.showLoading(false);
    }
}

    populateRouteSelector() {
        const selector = document.getElementById('routeSelector');
        selector.innerHTML = '<option value="">Selecciona una ruta</option>';

        console.log('🔧 Poblando selector con', this.userRoutes.length, 'rutas');

        this.userRoutes.forEach(route => {
            const option = document.createElement('option');
            option.value = route.id;
            
           
            let routeName = route.nombre || `Ruta ${route.id}`;
            let routeInfo = '';
            
            if (route.origen && route.destino) {
                routeInfo = ` - ${route.origen} → ${route.destino}`;
            } else if (route.trip) {
                routeInfo = ` - Viaje #${route.viaje_id}`;
            }
            
            option.textContent = routeName + routeInfo;
            selector.appendChild(option);
        });

        if (this.userRoutes.length === 0) {
            const option = document.createElement('option');
            option.textContent = 'No hay rutas disponibles';
            option.disabled = true;
            selector.appendChild(option);
        }

        console.log(' Selector poblado con', selector.children.length - 1, 'opciones');
    }

    async loadRoute(routeId) {
        try {
            this.showLoading(true);
            console.log(' Cargando ruta ID:', routeId);

            
            this.currentRoute = this.userRoutes.find(r => r.id === routeId);
            if (!this.currentRoute) {
                throw new Error('Ruta no encontrada en los datos locales');
            }

            console.log(' Ruta encontrada:', this.currentRoute);

          
            await this.loadCheckpoints(routeId);

            
            this.updateRouteInfo();
            this.renderCheckpoints();
            this.renderMapRoute();

            this.showMessage('Ruta cargada exitosamente', 'success');

        } catch (error) {
            console.error(' Error cargando ruta:', error);
            this.showMessage(`Error cargando ruta: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async loadCheckpoints(routeId) {
        try {
            console.log('Cargando checkpoints para ruta:', routeId);
            
            
            try {
                this.checkpoints = await this.apiRequest(`/rutas/${routeId}/checkpoints`);
                console.log(' Checkpoints cargados (ruta específica):', this.checkpoints.length);
            } catch (error) {
                console.log(' Ruta específica no disponible, usando método general');
                const allCheckpoints = await this.apiRequest('/admin/checkpoints');
                this.checkpoints = allCheckpoints.filter(checkpoint => checkpoint.ruta_id === routeId);
                console.log(' Checkpoints filtrados:', this.checkpoints.length);
            }
            
           
            this.checkpoints.sort((a, b) => (a.orden || 0) - (b.orden || 0));

        } catch (error) {
            console.error(' Error loading checkpoints:', error);
            this.checkpoints = [];
            this.showMessage('No se pudieron cargar los checkpoints', 'warning');
        }
    }

   
    updateRouteInfo() {
        if (!this.currentRoute) return;

        console.log('🔧 Actualizando info de ruta:', this.currentRoute);

       
        const statusIndicator = document.querySelector('.route-status .status-indicator');
        const statusText = document.querySelector('.route-status .status-text');
        
        if (this.currentRoute.activa) {
            statusIndicator.className = 'status-indicator active';
            statusText.textContent = 'Ruta Activa';
        } else {
            statusIndicator.className = 'status-indicator';
            statusText.textContent = 'Ruta Inactiva';
        }

        
        const origen = this.currentRoute.origen || this.currentRoute.trip?.origen || 'No especificado';
        const destino = this.currentRoute.destino || this.currentRoute.trip?.destino || 'No especificado';
        const distancia = this.currentRoute.distancia_km || this.currentRoute.distancia_total;
        const tiempo = this.currentRoute.tiempo_estimado_hrs || this.currentRoute.tiempo_estimado;

        document.getElementById('routeOrigin').textContent = origen;
        document.getElementById('routeDestination').textContent = destino;
        document.getElementById('routeDistance').textContent = distancia ? `${distancia} km` : 'No especificado';
        
        if (tiempo) {
           
            if (this.currentRoute.tiempo_estimado_hrs) {
                document.getElementById('routeTime').textContent = `${tiempo.toFixed(1)} horas`;
            } else {
               
                document.getElementById('routeTime').textContent = `${Math.round(tiempo / 60)} horas`;
            }
        } else {
            document.getElementById('routeTime').textContent = 'No especificado';
        }
    }

    renderCheckpoints() {
        const container = document.getElementById('checkpointsList');
        
        console.log('🔧 Renderizando checkpoints:', this.checkpoints.length);
        
        if (this.checkpoints.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-map-pin"></i>
                    <p>No hay checkpoints en esta ruta</p>
                </div>
            `;
            document.getElementById('checkpointCounter').textContent = '0/0';
            return;
        }

        const completedCount = this.checkpoints.filter(cp => cp.estado === 'completado' || cp.estado === 'alcanzado').length;
        document.getElementById('checkpointCounter').textContent = `${completedCount}/${this.checkpoints.length}`;

        container.innerHTML = this.checkpoints.map((checkpoint, index) => {
            
            let displayEstado = checkpoint.estado;
            if (checkpoint.estado === 'alcanzado') displayEstado = 'completado';
            
            return `
                <div class="checkpoint-item ${displayEstado}" onclick="mapController.showCheckpointDetail(${checkpoint.id})">
                    <div class="checkpoint-header">
                        <div class="checkpoint-title">
                            <i class="fas fa-map-pin"></i>
                            Checkpoint #${checkpoint.orden || index + 1}
                        </div>
                        <div class="checkpoint-status ${displayEstado}">${displayEstado}</div>
                    </div>
                    <div class="checkpoint-address">${checkpoint.direccion}</div>
                    <div class="checkpoint-actions">
                        <button class="checkpoint-btn primary" onclick="mapController.centerOnCheckpoint(${checkpoint.id}); event.stopPropagation();">
                            <i class="fas fa-eye"></i> Ver en Mapa
                        </button>
                        ${checkpoint.estado === 'pendiente' ? `
                            <button class="checkpoint-btn danger" onclick="mapController.reportIncident(${checkpoint.id}); event.stopPropagation();">
                                <i class="fas fa-exclamation-triangle"></i> Reportar
                            </button>
                        ` : ''}
                    </div>
                </div>
            `;
        }).join('');
    }

    renderMapRoute() {
       
        this.clearMapElements();

        if (this.checkpoints.length === 0) {
            console.log(' No hay checkpoints para mostrar en el mapa');
            return;
        }

        console.log(' Renderizando', this.checkpoints.length, 'checkpoints en el mapa');

       
        this.checkpoints.forEach((checkpoint, index) => {
          
            let iconEstado = checkpoint.estado;
            if (checkpoint.estado === 'alcanzado') iconEstado = 'completado';
            
            const icon = this.getCheckpointIcon(iconEstado);
            
            const marker = L.marker([checkpoint.latitud, checkpoint.longitud], { icon })
                .addTo(this.map)
                .bindPopup(`
                    <div style="color: black; font-size: 12px; min-width: 200px;">
                        <h4 style="margin: 0 0 8px 0; color: #1a365d;">Checkpoint #${checkpoint.orden || index + 1}</h4>
                        <p style="margin: 4px 0;"><strong>Estado:</strong> ${iconEstado}</p>
                        <p style="margin: 4px 0;"><strong>Dirección:</strong> ${checkpoint.direccion}</p>
                        <button onclick="mapController.showCheckpointDetail(${checkpoint.id})" 
                                style="margin-top: 8px; padding: 4px 8px; background: #3182ce; color: white; border: none; border-radius: 4px; cursor: pointer;">
                            Ver Detalles
                        </button>
                    </div>
                `);

            this.markers.push(marker);
        });

       
        if (this.checkpoints.length > 1) {
            const routeCoords = this.checkpoints.map(cp => [cp.latitud, cp.longitud]);
            
            this.routePolyline = L.polyline(routeCoords, {
                color: '#3182ce',
                weight: 4,
                opacity: 0.8
            }).addTo(this.map);

           
            const group = new L.featureGroup(this.markers);
            this.map.fitBounds(group.getBounds().pad(0.1));
        } else if (this.checkpoints.length === 1) {
          
            this.map.setView([this.checkpoints[0].latitud, this.checkpoints[0].longitud], 15);
        }

        console.log(' Mapa renderizado con', this.markers.length, 'marcadores');
    }

    getCheckpointIcon(estado) {
        let color = '#6b7280'; 
        
        switch (estado) {
            case 'completado':
            case 'alcanzado':
                color = '#10b981'; 
                break;
            case 'llegada':
                color = '#3b82f6'; 
                break;
            case 'pendiente':
                color = '#f59e0b'; 
                break;
            case 'saltado':
                color = '#ef4444';
                break;
        }

        return L.divIcon({
            className: 'custom-checkpoint-icon',
            html: `<div style="
                background-color: ${color};
                width: 20px;
                height: 20px;
                border-radius: 50%;
                border: 3px solid white;
                box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            "></div>`,
            iconSize: [20, 20],
            iconAnchor: [10, 10]
        });
    }

    clearMapElements() {
        
        this.markers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.markers = [];

        
        if (this.routePolyline) {
            this.map.removeLayer(this.routePolyline);
            this.routePolyline = null;
        }
    }

    clearRoute() {
        this.currentRoute = null;
        this.checkpoints = [];
        this.clearMapElements();
        
      
        document.getElementById('routeOrigin').textContent = '-';
        document.getElementById('routeDestination').textContent = '-';
        document.getElementById('routeDistance').textContent = '-';
        document.getElementById('routeTime').textContent = '-';
        document.getElementById('checkpointCounter').textContent = '0/0';
        
        const statusIndicator = document.querySelector('.route-status .status-indicator');
        const statusText = document.querySelector('.route-status .status-text');
        statusIndicator.className = 'status-indicator';
        statusText.textContent = 'Sin ruta seleccionada';

        document.getElementById('checkpointsList').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-map-pin"></i>
                <p>Selecciona una ruta para ver los checkpoints</p>
            </div>
        `;
    }

   
    refreshMap() {
        this.showMessage('Actualizando mapa...', 'info');
        this.loadUserRoutes();
    }

    centerOnUserLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    
                    this.map.setView([lat, lng], 16);
                    
                   
                    const userIcon = L.divIcon({
                        className: 'user-location-icon',
                        html: '<div style="background-color: #3b82f6; width: 12px; height: 12px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);"></div>',
                        iconSize: [12, 12],
                        iconAnchor: [6, 6]
                    });

                    L.marker([lat, lng], { icon: userIcon })
                        .addTo(this.map)
                        .bindPopup('Tu ubicación actual')
                        .openPopup();

                    this.showMessage('Ubicación encontrada', 'success');
                },
                (error) => {
                    this.showMessage('No se pudo obtener tu ubicación', 'warning');
                }
            );
        } else {
            this.showMessage('Geolocalización no soportada', 'warning');
        }
    }

    toggleTraffic() {
        this.showMessage('Funcionalidad de tráfico próximamente disponible', 'info');
    }

    toggleSatellite() {
        const btn = document.getElementById('toggleSatelliteBtn');
        
        if (btn.classList.contains('active')) {
            this.map.eachLayer((layer) => {
                if (layer._url && layer._url.includes('satellite')) {
                    this.map.removeLayer(layer);
                }
            });
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(this.map);
            
            btn.classList.remove('active');
        } else {
            this.map.eachLayer((layer) => {
                if (layer._url && layer._url.includes('openstreetmap')) {
                    this.map.removeLayer(layer);
                }
            });
            
            L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                attribution: '&copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
            }).addTo(this.map);
            
            btn.classList.add('active');
        }
    }

    toggleFullscreen() {
        const mapContainer = document.getElementById('mapContainer');
        
        if (document.fullscreenElement) {
            document.exitFullscreen();
        } else {
            mapContainer.requestFullscreen().then(() => {
                setTimeout(() => {
                    this.map.invalidateSize();
                }, 100);
            });
        }
    }

   
    centerOnCheckpoint(checkpointId) {
        const checkpoint = this.checkpoints.find(cp => cp.id === checkpointId);
        if (checkpoint) {
            this.map.setView([checkpoint.latitud, checkpoint.longitud], 17);
            
            
            const marker = this.markers.find(m => 
                Math.abs(m.getLatLng().lat - checkpoint.latitud) < 0.0001 && 
                Math.abs(m.getLatLng().lng - checkpoint.longitud) < 0.0001
            );
            if (marker) {
                marker.openPopup();
            }
        }
    }

    showCheckpointDetail(checkpointId) {
        const checkpoint = this.checkpoints.find(cp => cp.id === checkpointId);
        if (!checkpoint) return;

        this.renderCheckpointModal(checkpoint);
        document.getElementById('checkpointModal').style.display = 'block';
    }

    renderCheckpointModal(checkpoint) {
        document.getElementById('checkpointModalTitle').textContent = 
            `Checkpoint #${checkpoint.orden} - Detalles`;

        const content = document.getElementById('checkpointModalContent');
        
        
        const hashValue = checkpoint.hash_local || checkpoint.hash || 'No disponible';
        
        content.innerHTML = `
            <div class="checkpoint-detail">
                <div class="checkpoint-detail-section">
                    <h3><i class="fas fa-info-circle"></i> Información General</h3>
                    <div class="checkpoint-detail-grid">
                        <div class="checkpoint-detail-item">
                            <span class="detail-label">ID:</span>
                            <span class="detail-value">${checkpoint.id}</span>
                        </div>
                        <div class="checkpoint-detail-item">
                            <span class="detail-label">Orden:</span>
                            <span class="detail-value">#${checkpoint.orden}</span>
                        </div>
                        <div class="checkpoint-detail-item">
                            <span class="detail-label">Estado:</span>
                            <span class="detail-value checkpoint-status ${checkpoint.estado}">${checkpoint.estado}</span>
                        </div>
                        <div class="checkpoint-detail-item">
                            <span class="detail-label">Ruta ID:</span>
                            <span class="detail-value">${checkpoint.ruta_id}</span>
                        </div>
                    </div>
                </div>

                <div class="checkpoint-detail-section">
                    <h3><i class="fas fa-map-marker-alt"></i> Ubicación</h3>
                    <div class="checkpoint-detail-grid">
                        <div class="checkpoint-detail-item" style="grid-column: span 2;">
                            <span class="detail-label">Dirección:</span>
                            <span class="detail-value">${checkpoint.direccion}</span>
                        </div>
                        <div class="checkpoint-detail-item">
                            <span class="detail-label">Latitud:</span>
                            <span class="detail-value">${checkpoint.latitud}</span>
                        </div>
                        <div class="checkpoint-detail-item">
                            <span class="detail-label">Longitud:</span>
                            <span class="detail-value">${checkpoint.longitud}</span>
                        </div>
                    </div>
                </div>

                ${hashValue !== 'No disponible' ? `
                <div class="checkpoint-detail-section">
                    <h3><i class="fas fa-fingerprint"></i> Hash Blockchain</h3>
                    <div class="hash-display">${hashValue}</div>
                    ${checkpoint.blockchain_tx_hash ? `
                        <div style="margin-top: 10px;">
                            <span class="detail-label">Hash de Transacción:</span>
                            <div class="hash-display">${checkpoint.blockchain_tx_hash}</div>
                        </div>
                    ` : ''}
                </div>
                ` : ''}

                ${checkpoint.tiempo_estimado_llegada || checkpoint.tiempo_real_llegada || checkpoint.timestamp_alcanzado ? `
                <div class="checkpoint-detail-section">
                    <h3><i class="fas fa-clock"></i> Tiempos</h3>
                    <div class="checkpoint-detail-grid">
                        ${checkpoint.tiempo_estimado_llegada ? `
                        <div class="checkpoint-detail-item">
                            <span class="detail-label">Tiempo Estimado:</span>
                            <span class="detail-value">${this.formatDate(checkpoint.tiempo_estimado_llegada)}</span>
                        </div>
                        ` : ''}
                        ${checkpoint.tiempo_real_llegada || checkpoint.timestamp_alcanzado ? `
                        <div class="checkpoint-detail-item">
                            <span class="detail-label">Tiempo Real:</span>
                            <span class="detail-value">${this.formatDate(checkpoint.tiempo_real_llegada || checkpoint.timestamp_alcanzado)}</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
                ` : ''}
            </div>
        `;

       
        const markBtn = document.getElementById('markCheckpointBtn');
        if (checkpoint.estado === 'pendiente') {
            markBtn.style.display = 'flex';
            markBtn.onclick = () => this.markCheckpointCompleted(checkpoint.id);
        } else {
            markBtn.style.display = 'none';
        }
    }

    
    async markCheckpointCompleted(checkpointId) {
    try {
        console.log(`🔍 Marcando checkpoint ${checkpointId} como completado...`);
        
       
        await this.apiRequest(`/conductor/checkpoints/${checkpointId}/completar`, {
            method: 'PUT',
            body: JSON.stringify({
                tiempo_real_llegada: new Date().toISOString()
            })
        });

        this.showMessage('Checkpoint marcado como completado', 'success');
        document.getElementById('checkpointModal').style.display = 'none';
        
        
        if (this.currentRoute) {
            await this.loadRoute(this.currentRoute.id);
        }

    } catch (error) {
        console.error(' Error marcando checkpoint:', error);
        this.showMessage(`Error actualizando checkpoint: ${error.message}`, 'error');
    }
}

    reportIncident(checkpointId) {
        document.getElementById('incidentCheckpointId').value = checkpointId;
        document.getElementById('incidentModal').style.display = 'block';
    }

    async submitIncident(e) {
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        this.showButtonLoading(submitBtn, true);

        try {
            const formData = new FormData(form);
            const data = {};
            
            for (let [key, value] of formData.entries()) {
                if (value.trim()) {
                    data[key] = value.trim();
                }
            }

            await this.apiRequest(`/conductor/checkpoints/${data.checkpoint_id}/incidentes`, {
                method: 'POST',
                body: JSON.stringify({
                    descripcion: data.descripcion,
                    tipo: data.tipo,
                    gravedad: data.gravedad
                })
            });

            this.showMessage('Incidente reportado exitosamente', 'success');
            document.getElementById('incidentModal').style.display = 'none';
            form.reset();

           
            if (this.currentRoute) {
                await this.loadRoute(this.currentRoute.id);
            }

        } catch (error) {
            this.showMessage(`Error reportando incidente: ${error.message}`, 'error');
        } finally {
            this.showButtonLoading(submitBtn, false);
        }
    }

   
    toggleTracking() {
        const btn = document.getElementById('trackingToggle');
        const icon = btn.querySelector('i');
        
        if (this.isTracking) {
            
            this.stopTracking();
            btn.classList.remove('active');
            icon.className = 'fas fa-play';
            const textNode = btn.childNodes[btn.childNodes.length - 1];
            if (textNode && textNode.nodeType === Node.TEXT_NODE) {
                textNode.textContent = 'Iniciar';
            }
        } else {
          
            this.startTracking();
            btn.classList.add('active');
            icon.className = 'fas fa-stop';
            const textNode = btn.childNodes[btn.childNodes.length - 1];
            if (textNode && textNode.nodeType === Node.TEXT_NODE) {
                textNode.textContent = 'Detener';
            }
        }
    }

    startTracking() {
        this.isTracking = true;
        
       
        this.updateTrackingStatus();
        
       
        this.trackingInterval = setInterval(() => {
            this.updateTrackingStatus();
        }, 30000);
        
        this.showMessage('Seguimiento en vivo iniciado', 'success');
    }

    stopTracking() {
        this.isTracking = false;
        
        if (this.trackingInterval) {
            clearInterval(this.trackingInterval);
            this.trackingInterval = null;
        }
        
       
        document.getElementById('vehicleStatus').textContent = 'Detenido';
        document.getElementById('vehicleSpeed').textContent = '0 km/h';
        
        this.showMessage('Seguimiento en vivo detenido', 'info');
    }

    updateTrackingStatus() {
      
        const statuses = ['En movimiento', 'Detenido', 'En checkpoint'];
        const speeds = [0, 25, 45, 60, 35, 80];
        
        const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
        const randomSpeed = speeds[Math.floor(Math.random() * speeds.length)];
        
        document.getElementById('vehicleStatus').textContent = randomStatus;
        document.getElementById('vehicleSpeed').textContent = `${randomSpeed} km/h`;
        document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString('es-ES');
    }

   
    formatDate(dateString) {
        if (!dateString) return 'No especificado';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleString('es-ES', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (error) {
            return dateString;
        }
    }

   
    showMessage(message, type = 'info') {
        const container = document.getElementById('messageContainer');
        container.textContent = message;
        container.className = `message-container ${type}`;
        container.classList.remove('hidden');

        setTimeout(() => {
            container.classList.add('hidden');
        }, 5000);
    }

    showLoading(show) {
        const spinner = document.getElementById('loadingSpinner');
        if (show) {
            spinner.classList.remove('hidden');
        } else {
            spinner.classList.add('hidden');
        }
    }

    showButtonLoading(button, show) {
        const btnText = button.querySelector('.btn-text');
        const spinner = button.querySelector('.spinner');
        
        if (show) {
            if (btnText) btnText.style.display = 'none';
            if (spinner) spinner.classList.remove('hidden');
            button.disabled = true;
        } else {
            if (btnText) btnText.style.display = 'inline';
            if (spinner) spinner.classList.add('hidden');
            button.disabled = false;
        }
    }
}


let mapController;

document.addEventListener('DOMContentLoaded', () => {
    mapController = new MapController();
});