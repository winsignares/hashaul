

class Dashboard {
    constructor() {
        this.API_BASE_URL = window.location.origin + '/api';
        this.token = localStorage.getItem('hashhaul_token');
        this.currentUser = null;
        this.userTrips = {
            historial: [],
            proximos: []
        };
        this.userCamiones = [];
        this.estadisticas = {};
        
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
            await this.loadDashboardData();
        } catch (error) {
            console.error('Error inicializando dashboard:', error);
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
    
        const userName = document.getElementById('userName');
        const userRole = document.getElementById('userRole');
        
        if (userName) userName.textContent = this.currentUser.nombre;
        if (userRole) userRole.textContent = this.currentUser.rol;
        
      
        const profileName = document.getElementById('profileName');
        const profileRole = document.getElementById('profileRole');
        const profileEmail = document.getElementById('profileEmail');
        const profilePhone = document.getElementById('profilePhone');
        const profileSince = document.getElementById('profileSince');
        
        if (profileName) profileName.textContent = this.currentUser.nombre;
        if (profileRole) profileRole.textContent = this.currentUser.rol;
        if (profileEmail) profileEmail.textContent = this.currentUser.correo;
        if (profilePhone) profilePhone.textContent = this.currentUser.telefono || 'No disponible';
        
    
        if (this.currentUser.fecha_registro && profileSince) {
            const date = new Date(this.currentUser.fecha_registro);
            profileSince.textContent = date.toLocaleDateString('es-ES', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }

       
        const adminLink = document.getElementById('adminLink');
        if (adminLink) {
            if (['administrador', 'supervisor', 'admin'].includes(this.currentUser.rol)) {
                adminLink.style.display = 'flex';
            } else {
                adminLink.style.display = 'none';
            }
        }
    }

    redirectToLogin() {
        window.location.href = '/';
    }

    
    setupEventListeners() {
       
        
       
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                localStorage.removeItem('hashhaul_token');
                this.redirectToLogin();
            });
        }

      
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadDashboardData();
            });
        }

     
        const adminLink = document.getElementById('adminLink');
        if (adminLink) {
            adminLink.addEventListener('click', (e) => {
                e.preventDefault();
                window.location.href = '/admin';
            });
        }

       const mapLink = document.getElementById('mapLink');
if (mapLink) {
    
    
    
 
    mapLink.addEventListener('click', (e) => {
        
        console.log('Navegando al mapa...'); 
        
    });
}


const viewMapBtn = document.getElementById('viewMapBtn');
if (viewMapBtn) {
    viewMapBtn.addEventListener('click', () => {
        window.location.href = '/map'; 
    });
}

        const reportIncidentBtn = document.getElementById('reportIncidentBtn');
        if (reportIncidentBtn) {
            reportIncidentBtn.addEventListener('click', () => {
                this.openIncidentModal();
            });
        }

        const viewProfileBtn = document.getElementById('viewProfileBtn');
        if (viewProfileBtn) {
            viewProfileBtn.addEventListener('click', () => {
                this.showMessage('Funcionalidad de editar perfil próximamente disponible', 'info');
            });
        }

        const contactSupportBtn = document.getElementById('contactSupportBtn');
        if (contactSupportBtn) {
            contactSupportBtn.addEventListener('click', () => {
                this.showMessage('Para soporte contacta: soporte@hashhaul.com', 'info');
            });
        }

      
        const viewAllHistoryBtn = document.getElementById('viewAllHistoryBtn');
        if (viewAllHistoryBtn) {
            viewAllHistoryBtn.addEventListener('click', () => {
                this.showAllTrips('historial');
            });
        }

        const refreshTripsBtn = document.getElementById('refreshTripsBtn');
        if (refreshTripsBtn) {
            refreshTripsBtn.addEventListener('click', () => {
                this.loadUpcomingTrips();
            });
        }

    
        this.setupModalListeners();
    }

    setupModalListeners() {
        
        
        
        const tripModal = document.getElementById('tripDetailModal');
        const closeTripModal = document.getElementById('closeTripModal');
        const closeTripDetailBtn = document.getElementById('closeTripDetailBtn');
        
        if (closeTripModal) {
            closeTripModal.addEventListener('click', () => {
                if (tripModal) tripModal.style.display = 'none';
            });
        }
        
        if (closeTripDetailBtn) {
            closeTripDetailBtn.addEventListener('click', () => {
                if (tripModal) tripModal.style.display = 'none';
            });
        }

       
        const incidentModal = document.getElementById('incidentModal');
        const closeIncidentModal = document.getElementById('closeIncidentModal');
        const cancelIncidentBtn = document.getElementById('cancelIncidentBtn');
        
        if (closeIncidentModal) {
            closeIncidentModal.addEventListener('click', () => {
                if (incidentModal) incidentModal.style.display = 'none';
            });
        }
        
        if (cancelIncidentBtn) {
            cancelIncidentBtn.addEventListener('click', () => {
                if (incidentModal) incidentModal.style.display = 'none';
            });
        }

        
        const incidentForm = document.getElementById('incidentForm');
        if (incidentForm) {
            incidentForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitIncident(e);
            });
        }

       
        window.addEventListener('click', (e) => {
            if (e.target === tripModal) tripModal.style.display = 'none';
            if (e.target === incidentModal) incidentModal.style.display = 'none';
        });
    }

   
    async loadDashboardData() {
        this.showLoading(true);
        
        try {
            await Promise.all([
                this.loadEstadisticas(),
                this.loadUserTrips(),
                this.loadUserCamiones()
            ]);
            
            this.renderDashboard();
            const dashboardContent = document.getElementById('dashboardContent');
            if (dashboardContent) dashboardContent.style.display = 'block';
            
        } catch (error) {
            this.showMessage(`Error cargando datos: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
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
            let errorData;
            try {
                errorData = await response.json();
            } catch {
                errorData = { error: 'Error en la solicitud' };
            }
            throw new Error(errorData.error || errorData.message || 'Error en la solicitud');
        }

        return response.json();
    }

    async loadEstadisticas() {
        try {
            const response = await this.apiRequest('/dashboard/estadisticas');
            if (response.success) {
                this.estadisticas = response.data;
                console.log('Estadísticas cargadas:', this.estadisticas);
            }
        } catch (error) {
            console.error('Error loading estadisticas:', error);
            this.estadisticas = {
                total_viajes: 0,
                viajes_completados: 0,
                viajes_pendientes: 0,
                total_usuarios: 0
            };
        }
    }

    async loadUserTrips() {
        try {
          
            const completedResponse = await this.apiRequest('/dashboard/viajes_completos');
            if (completedResponse.success) {
                this.userTrips.historial = completedResponse.data;
                console.log('Viajes completados cargados:', this.userTrips.historial);
            }

            
            const pendingResponse = await this.apiRequest('/dashboard/viajes_pendientes');
            if (pendingResponse.success) {
                this.userTrips.proximos = pendingResponse.data;
                console.log('Viajes pendientes cargados:', this.userTrips.proximos);
            }
        } catch (error) {
            console.error('Error loading user trips:', error);
            this.userTrips.historial = [];
            this.userTrips.proximos = [];
        }
    }

    async loadUserCamiones() {
        try {
            
            this.userCamiones = [];
        } catch (error) {
            console.log('No hay camiones asignados disponibles');
            this.userCamiones = [];
        }
    }

    async loadUpcomingTrips() {
        try {
            this.showMessage('Actualizando viajes próximos...', 'info');
            
            const response = await this.apiRequest('/dashboard/viajes_pendientes');
            if (response.success) {
                this.userTrips.proximos = response.data;
                this.renderUpcomingTrips();
                this.showMessage('Viajes actualizados correctamente', 'success');
            }
        } catch (error) {
            this.showMessage(`Error actualizando viajes: ${error.message}`, 'error');
        }
    }


    renderDashboard() {
        this.updateTripStats();
        this.renderAssignedTruck();
        this.renderTripHistory();
        this.renderUpcomingTrips();
    }

    updateTripStats() {
       
        const totalTripsEl = document.getElementById('totalTrips');
        const completedTripsEl = document.getElementById('completedTrips');
        const pendingTripsEl = document.getElementById('pendingTrips');
        
        if (totalTripsEl) totalTripsEl.textContent = this.estadisticas.total_viajes || 0;
        if (completedTripsEl) completedTripsEl.textContent = this.estadisticas.viajes_completados || 0;
        if (pendingTripsEl) pendingTripsEl.textContent = this.estadisticas.viajes_pendientes || 0;
    }

    renderAssignedTruck() {
       
        if (this.userCamiones.length > 0) {
            const truck = this.userCamiones[0];
            const profileTruck = document.getElementById('profileTruck');
            const assignedTruckContainer = document.getElementById('assignedTruckContainer');
            
            if (profileTruck && truck) {
                profileTruck.textContent = `${truck.placa} - ${truck.modelo}`;
                if (assignedTruckContainer) assignedTruckContainer.style.display = 'flex';
            }
        }
    }

    renderTripHistory() {
    const historyContent = document.getElementById('historyContent');
    if (!historyContent) return;

    if (this.userTrips.historial.length === 0) {
        historyContent.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-route"></i>
                <p>No hay viajes completados aún</p>
            </div>
        `;
        return;
    }

        
    const tripsList = document.createElement('ul');
    tripsList.className = 'trips-list';
    
    this.userTrips.historial.forEach(trip => {
        const li = document.createElement('li');
        li.className = 'trip-item';
        li.innerHTML = `
            <div class="trip-info">
                <span class="trip-id">Viaje #${trip.id} - ${trip.codigo || 'Sin código'}</span>
                <span class="trip-route">${trip.origen || 'Origen'} → ${trip.destino || 'Destino'}</span>
                <span class="trip-date">${trip.fecha_inicio ? new Date(trip.fecha_inicio).toLocaleDateString() : 'Sin fecha'}</span>
                <span class="trip-status status-${trip.estado}">${trip.estado}</span>
                <span class="trip-conductor">Conductor: ${trip.conductor || 'No asignado'}</span>
            </div>
        `;
        li.addEventListener('click', () => this.showTripDetail(trip));
        tripsList.appendChild(li);
    });
    
    historyContent.innerHTML = '';
    historyContent.appendChild(tripsList);
}

    renderUpcomingTrips() {
    const upcomingContent = document.getElementById('upcomingContent');
    if (!upcomingContent) return;

    if (this.userTrips.proximos.length === 0) {
        upcomingContent.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-calendar-plus"></i>
                <p>No hay viajes programados</p>
            </div>
        `;
        return;
    }

    const tripsList = document.createElement('ul');
    tripsList.className = 'trips-list';
    
    this.userTrips.proximos.forEach(trip => {
        const li = document.createElement('li');
        li.className = 'trip-item';
        li.innerHTML = `
            <div class="trip-info">
                <span class="trip-id">Viaje #${trip.id} - ${trip.codigo || 'Sin código'}</span>
                <span class="trip-route">${trip.origen || 'Origen'} → ${trip.destino || 'Destino'}</span>
                <span class="trip-date">${trip.fecha_inicio ? new Date(trip.fecha_inicio).toLocaleDateString() : 'Sin fecha'}</span>
                <span class="trip-status status-${trip.estado}">${trip.estado}</span>
                <span class="trip-conductor">Conductor: ${trip.conductor || 'No asignado'}</span>
            </div>
        `;
        li.addEventListener('click', () => this.showTripDetail(trip));
        tripsList.appendChild(li);
    });
    
    upcomingContent.innerHTML = '';
    upcomingContent.appendChild(tripsList);
}

  
    showTripDetail(trip) {
    const tripDetailContent = document.getElementById('tripDetailContent');
    if (tripDetailContent) {
        tripDetailContent.innerHTML = `
            <div class="trip-detail">
                <p><strong>ID:</strong> ${trip.id}</p>
                <p><strong>Código:</strong> ${trip.codigo || 'No especificado'}</p>
                <p><strong>Origen:</strong> ${trip.origen || 'No especificado'}</p>
                <p><strong>Destino:</strong> ${trip.destino || 'No especificado'}</p>
                <p><strong>Fecha Inicio:</strong> ${trip.fecha_inicio ? new Date(trip.fecha_inicio).toLocaleString() : 'No especificada'}</p>
                <p><strong>Fecha Fin:</strong> ${trip.fecha_fin ? new Date(trip.fecha_fin).toLocaleString() : 'No especificada'}</p>
                <p><strong>Estado:</strong> <span class="status-${trip.estado}">${trip.estado}</span></p>
                <p><strong>Conductor:</strong> ${trip.conductor || 'No asignado'}</p>
                <p><strong>Usuario ID:</strong> ${trip.usuario_id || 'No asignado'}</p>
                <p><strong>Camión:</strong> ${trip.camion_placa || `ID: ${trip.camion_id}` || 'No asignado'}</p>
                ${trip.observaciones ? `<p><strong>Observaciones:</strong> ${trip.observaciones}</p>` : ''}
            </div>
        `;
    }
    
    const tripModal = document.getElementById('tripDetailModal');
    if (tripModal) tripModal.style.display = 'block';
}


    openIncidentModal() {
        const incidentModal = document.getElementById('incidentModal');
        if (incidentModal) incidentModal.style.display = 'block';
    }

    async submitIncident(e) {
    const tipo = document.getElementById('incidentType').value;
    const gravedad = document.getElementById('incidentGravity').value;
    const descripcion = document.getElementById('incidentDescription').value;
    const checkpointId = document.getElementById('checkpointId').value;
    
    if (!tipo || !gravedad || !descripcion || !checkpointId) {
        alert('Por favor, completa todos los campos obligatorios.');
        return;
    }

    try {
        
        const response = await this.apiRequest('/dashboard/incidentes', {
            method: 'POST',
            body: JSON.stringify({
                tipo: tipo,
                gravedad: gravedad,
                descripcion: descripcion,
                checkpoint_id: checkpointId
            })
        });

        this.showMessage('Incidente reportado exitosamente', 'success');
        const incidentForm = document.getElementById('incidentForm');
        if (incidentForm) incidentForm.reset();
        
        const incidentModal = document.getElementById('incidentModal');
        if (incidentModal) incidentModal.style.display = 'none';

    } catch (error) {
        this.showMessage(`Error reportando incidente: ${error.message}`, 'error');
    }
}

    showAllTrips(tipo) {
        if (tipo === 'historial') {
            this.showMessage('Mostrando todos los viajes completados', 'info');
            
        } else if (tipo === 'proximos') {
            this.showMessage('Mostrando todos los viajes próximos', 'info');
            
        }
    }

    
    showLoading(show) {
        const loadingElem = document.getElementById('loadingSpinner');
        if (loadingElem) {
            loadingElem.style.display = show ? 'flex' : 'none';
        }
    }

    showMessage(msg, type = 'info') {
        const messageContainer = document.getElementById('messageContainer');
        if (!messageContainer) {
            
            console.log(`${type.toUpperCase()}: ${msg}`);
            return;
        }
        
        messageContainer.textContent = msg;
        messageContainer.className = 'message-container'; 
        
        if (type === 'error') {
            messageContainer.classList.add('message-error');
        } else if (type === 'success') {
            messageContainer.classList.add('message-success');
        } else {
            messageContainer.classList.add('message-info');
        }
        
        messageContainer.classList.remove('hidden');

        setTimeout(() => {
            messageContainer.classList.add('hidden');
        }, 5000);
    }
}


document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});
