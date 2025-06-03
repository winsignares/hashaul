
class AdminPanel {
    constructor() {
        this.API_BASE_URL = window.location.origin + '/api';
        this.token = localStorage.getItem('hashhaul_token');
        this.currentUser = null;
        this.currentTab = 'usuarios';
        this.data = {
            usuarios: [],
            camiones: [],
            viajes: [],
            rutas: [],
            checkpoints: [],
            incidentes: []
        };
        
        this.init();
    }

    getApiType(type) {
 
    const typeMapping = {
        'usuarios': 'usuarios',    
        'camiones': 'camiones',    
        'viajes': 'viajes',       
        'rutas': 'rutas',         
        'checkpoints': 'checkpoints', 
        'incidentes': 'incidentes'    
    };
    
    return typeMapping[type] || type;
}


    async init() {
        if (!this.token) {
            this.redirectToLogin();
            return;
        }

        try {
            await this.verifyToken();
            this.setupEventListeners();
            await this.loadInitialData();
        } catch (error) {
            console.error('Error inicializando admin panel:', error);
            this.showMessage('No autorizado o sesión expirada. Redirigiendo al inicio de sesión.', 'error');
            setTimeout(() => this.redirectToLogin(), 2000);
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
                const errorData = await response.json();
                throw new Error(errorData.error || 'Token inválido');
            }

            const data = await response.json();
            this.currentUser = data.usuario;

       
            if (!['administrador', 'supervisor'].includes(this.currentUser.rol)) {
                this.showMessage('No tienes permisos de administrador/supervisor', 'error');
                setTimeout(() => window.location.href = '/dashboard', 2000);
                return;
            }

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
                this.loadTabData(this.currentTab);
            });
        }

     
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.closest('.tab-btn').dataset.tab;
                this.switchTab(tab);
            });
        });

      
        document.querySelectorAll('.add-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const type = e.target.closest('.add-btn').id.replace('add-', '').replace('-btn', '');
                this.openFormModal(type);
            });
        });

        
        document.addEventListener('click', async (e) => {
            const target = e.target.closest('.action-btn');
            if (!target) return;
            
            if (target.classList.contains('view-btn')) {
                this.viewItem(target.dataset.type, target.dataset.id);
            } else if (target.classList.contains('edit-btn')) {
                this.editItem(target.dataset.type, target.dataset.id);
            } else if (target.classList.contains('delete-btn')) {
                this.deleteItem(target.dataset.type, target.dataset.id);
            } else if (target.classList.contains('resolve-btn')) {
                await this.resolveIncidente(target.dataset.id);
            }
        });

      
        this.setupModalListeners();
    }

    setupModalListeners() {
        const formModal = document.getElementById('form-modal');
        const viewModal = document.getElementById('view-modal');

  
        document.getElementById('closeFormModal').addEventListener('click', () => {
            formModal.classList.add('hidden');
        });

        document.getElementById('closeViewModal').addEventListener('click', () => {
            viewModal.classList.add('hidden');
        });

        document.querySelector('#form-modal .cancel-btn').addEventListener('click', () => { 
            formModal.classList.add('hidden');
        });

        document.querySelector('#view-modal .close-btn').addEventListener('click', () => { 
            viewModal.classList.add('hidden');
        });

        
        window.addEventListener('click', (e) => {
            if (e.target === formModal) formModal.classList.add('hidden');
            if (e.target === viewModal) viewModal.classList.add('hidden');
        });

      
        document.getElementById('data-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFormSubmit(e);
        });
    }

 
    switchTab(tabName) {
        this.currentTab = tabName;

      
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

   
        this.loadTabData(tabName);
    }

    
    async loadInitialData() {
        this.showLoading(true);
        try {
            await this.loadTabData('usuarios'); 
        } finally {
            this.showLoading(false);
        }
    }

    async loadTabData(tabName) {
        try {
            this.showLoading(true);
            
            switch (tabName) {
                case 'usuarios':
                    await this.loadUsuarios();
                    break;
                case 'camiones':
                    await this.loadCamiones();
                    break;
                case 'viajes':
                    await this.loadViajes();
                    break;
                case 'rutas':
                    await this.loadRutas();
                    break;
                case 'checkpoints':
                    await this.loadCheckpoints();
                    break;
                case 'incidentes':
                    await this.loadIncidentes();
                    break;
            }
        } catch (error) {
            console.error(`Error cargando ${tabName}:`, error);
            this.showMessage(`Error cargando ${tabName}: ${error.message}`, 'error');
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

    console.log(' API Request:', {
        url: `${this.API_BASE_URL}${url}`,
        method: options.method || 'GET',
        headers: { ...defaultOptions.headers, ...options.headers },
        body: options.body
    });

    try {
        const response = await fetch(`${this.API_BASE_URL}${url}`, {
            ...defaultOptions,
            ...options,
            headers: { ...defaultOptions.headers, ...options.headers }
        });

        console.log(' Response Status:', response.status, response.statusText);
        console.log(' Response Headers:', Object.fromEntries(response.headers.entries()));

      
        const responseText = await response.text();
        console.log(' Raw Response:', responseText);

        if (!response.ok) {
            let errorData;
            try {
              
                errorData = JSON.parse(responseText);
                console.log(' Error Data (JSON):', errorData);
            } catch (parseError) {
                
                console.log(' Error Data (Not JSON):', responseText);
                errorData = { 
                    error: `Error del servidor (${response.status}): ${responseText.slice(0, 200)}...` 
                };
            }
            throw new Error(errorData.error || `Error en la solicitud: ${response.status} ${response.statusText}`);
        }

        
        try {
            const jsonData = JSON.parse(responseText);
            console.log(' Success Data:', jsonData);
            return jsonData;
        } catch (parseError) {
            console.log(' Response is not JSON:', responseText);
           
            return { mensaje: responseText };
        }

    } catch (fetchError) {
        console.error(' Fetch Error:', fetchError);
        throw fetchError;
    }
}


    
    async loadUsuarios() {
        try {
            this.data.usuarios = await this.apiRequest('/admin/usuarios');
            this.renderUsuariosTable();
        } catch (error) {
            console.error('Error loading usuarios:', error);
            this.data.usuarios = []; 
            this.renderUsuariosTable();
        }
    }

    async loadCamiones() {
        try {
            this.data.camiones = await this.apiRequest('/admin/camiones');
            this.renderCamionesTable();
        } catch (error) {
            console.error('Error loading camiones:', error);
            this.data.camiones = [];
            this.renderCamionesTable();
        }
    }

    async loadViajes() {
        try {
            this.data.viajes = await this.apiRequest('/admin/viajes');
            this.renderViajesTable();
        } catch (error) {
            console.error('Error loading viajes:', error);
            this.data.viajes = [];
            this.renderViajesTable();
        }
    }

    async loadRutas() {
        try {
            this.data.rutas = await this.apiRequest('/admin/rutas');
            this.renderRutasTable();
        } catch (error) {
            console.error('Error loading rutas:', error);
            this.data.rutas = [];
            this.renderRutasTable();
        }
    }

   async loadCheckpoints() {
    try {
        console.log(' Cargando todos los checkpoints');
        
        // ✅ Cargar TODOS los checkpoints (sin filtrar)
        this.data.checkpoints = await this.apiRequest('/admin/checkpoints');
        console.log(' Checkpoints cargados:', this.data.checkpoints.length);
        
        // ✅ Renderizar la tabla
        this.renderCheckpointsTable();
        
    } catch (error) {
        console.error(' Error loading checkpoints:', error);
        this.data.checkpoints = [];
        this.renderCheckpointsTable();
    }
}


    async loadIncidentes() {
        try {
            this.data.incidentes = await this.apiRequest('/admin/incidentes');
            this.renderIncidentesTable();
        } catch (error) {
            console.error('Error loading incidentes:', error);
            this.data.incidentes = [];
            this.renderIncidentesTable();
        }
    }

    
    renderUsuariosTable() {
        const tbody = document.getElementById('usuarios-table-body');
        tbody.innerHTML = '';

        if (this.data.usuarios.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No hay usuarios registrados</td></tr>';
            return;
        }

        this.data.usuarios.forEach(usuario => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${usuario.id}</td>
                <td>${usuario.nombre}</td>
                <td>${usuario.correo}</td>
                <td>${usuario.telefono || 'N/A'}</td>
                <td><span class="badge badge-${usuario.rol}">${usuario.rol.toUpperCase()}</span></td>
                <td><span class="status ${usuario.activo ? 'active' : 'inactive'}">${usuario.activo ? 'ACTIVO' : 'INACTIVO'}</span></td>
                <td>${this.formatDate(usuario.fecha_registro)}</td>
                <td class="actions-cell">
                    <button class="action-btn view-btn" data-type="usuario" data-id="${usuario.id}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn edit-btn" data-type="usuario" data-id="${usuario.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete-btn" data-type="usuario" data-id="${usuario.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderCamionesTable() {
        const tbody = document.getElementById('camiones-table-body');
        tbody.innerHTML = '';

        if (this.data.camiones.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No hay camiones registrados</td></tr>';
            return;
        }

        this.data.camiones.forEach(camion => {
            const row = document.createElement('tr');
           
           
            const estadoCamion = 'disponible'; 
            const fechaRegistroCamion = new Date().toISOString(); 
            row.innerHTML = `
                <td>${camion.id}</td>
                <td><strong>${camion.placa}</strong></td>
                <td>${camion.modelo}</td>
                <td>${camion.capacidad_kg || 'N/A'} kg</td>
                <td>${camion.año || 'N/A'}</td>
                <td><span class="status ${estadoCamion}">${estadoCamion.toUpperCase()}</span></td>
                <td>${this.formatDate(fechaRegistroCamion)}</td>
                <td class="actions-cell">
                    <button class="action-btn view-btn" data-type="camion" data-id="${camion.id}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn edit-btn" data-type="camion" data-id="${camion.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete-btn" data-type="camion" data-id="${camion.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderViajesTable() {
        const tbody = document.getElementById('viajes-table-body');
        tbody.innerHTML = '';

        if (this.data.viajes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align: center;">No hay viajes registrados</td></tr>';
            return;
        }

        this.data.viajes.forEach(viaje => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${viaje.id}</td>
                <td>${viaje.usuario_id}</td>
                <td>${viaje.camion_id}</td>
                <td><span class="status ${viaje.estado}">${viaje.estado.toUpperCase()}</span></td>
                <td>${this.formatDate(viaje.fecha_inicio)}</td>
                <td>${this.formatDate(viaje.fecha_fin)}</td>
                <td>${viaje.codigo || 'N/A'}</td>
                <td>${viaje.observaciones || 'N/A'}</td>
                <td class="actions-cell">
                    <button class="action-btn view-btn" data-type="viaje" data-id="${viaje.id}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn edit-btn" data-type="viaje" data-id="${viaje.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete-btn" data-type="viaje" data-id="${viaje.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderRutasTable() {
        const tbody = document.getElementById('rutas-table-body');
        tbody.innerHTML = '';

        if (this.data.rutas.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No hay rutas registradas</td></tr>';
            return;
        }

        this.data.rutas.forEach(ruta => {
            const row = document.createElement('tr');
           
            const estadoRuta = 'activa'; 
            row.innerHTML = `
                <td>${ruta.id}</td>
                <td>${ruta.viaje_id}</td>
                <td>${ruta.nombre || 'Sin nombre'}</td>
                <td>${ruta.distancia_km || 'N/A'} km</td>
                <td>${ruta.tiempo_estimado_hrs || 'N/A'} hrs</td>
                <td><span class="status ${estadoRuta}">${estadoRuta.toUpperCase()}</span></td>
                <td>${this.formatDate(ruta.fecha_creacion)}</td>
                <td class="actions-cell">
                    <button class="action-btn view-btn" data-type="ruta" data-id="${ruta.id}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn edit-btn" data-type="ruta" data-id="${ruta.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete-btn" data-type="ruta" data-id="${ruta.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderCheckpointsTable() {
        const tbody = document.getElementById('checkpoints-table-body');
        tbody.innerHTML = '';

        if (this.data.checkpoints.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No hay checkpoints registrados</td></tr>';
            return;
        }

        this.data.checkpoints.forEach(checkpoint => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${checkpoint.id}</td>
                <td>${checkpoint.ruta_id}</td>
                <td class="truncate" title="${checkpoint.direccion}">${checkpoint.direccion}</td>
                <td>${checkpoint.latitud}, ${checkpoint.longitud}</td>
                <td>${checkpoint.orden}</td>
                <td><span class="status ${checkpoint.estado}">${checkpoint.estado.toUpperCase()}</span></td>
                <td class="hash-cell" title="${checkpoint.hash}">${this.truncateHash(checkpoint.hash)}</td>
                <td class="actions-cell">
                    <button class="action-btn view-btn" data-type="checkpoint" data-id="${checkpoint.id}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn edit-btn" data-type="checkpoint" data-id="${checkpoint.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete-btn" data-type="checkpoint" data-id="${checkpoint.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderIncidentesTable() {
        const tbody = document.getElementById('incidentes-table-body');
        tbody.innerHTML = '';

        if (this.data.incidentes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No hay incidentes registrados</td></tr>';
            return;
        }

        this.data.incidentes.forEach(incidente => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${incidente.id}</td>
                <td>${incidente.checkpoint_id}</td>
                <td><span class="badge badge-${incidente.tipo}">${incidente.tipo.toUpperCase()}</span></td>
                <td class="truncate" title="${incidente.descripcion}">${incidente.descripcion}</td>
                <td><span class="badge badge-${incidente.gravedad}">${incidente.gravedad.toUpperCase()}</span></td>
                <td><span class="status ${incidente.resuelto ? 'resolved' : 'pending'}">${incidente.resuelto ? 'RESUELTO' : 'PENDIENTE'}</span></td>
                <td>${this.formatDate(incidente.timestamp)}</td>
                <td class="actions-cell">
                    <button class="action-btn view-btn" data-type="incidente" data-id="${incidente.id}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn edit-btn" data-type="incidente" data-id="${incidente.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    ${!incidente.resuelto ? `
                        <button class="action-btn resolve-btn" data-type="incidente" data-id="${incidente.id}" title="Marcar como resuelto">
                            <i class="fas fa-check"></i>
                        </button>
                    ` : ''}
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    
    openFormModal(type, item = null) {
        const modal = document.getElementById('form-modal');
        const title = document.getElementById('modal-title');
        const form = document.getElementById('data-form');
        
        title.textContent = item ? `Editar ${type.charAt(0).toUpperCase() + type.slice(1)}` : `Agregar ${type.charAt(0).toUpperCase() + type.slice(1)}`;
        
        form.dataset.type = type;
        form.dataset.mode = item ? 'edit' : 'add';
        if (item) form.dataset.id = item.id;
        
        this.generateFormFields(type, item);
        modal.classList.remove('hidden');
    }

    generateFormFields(type, item = null) {
        const container = document.getElementById('form-fields');
        container.innerHTML = '';

        const configs = this.getFormConfigs();
        const config = configs[type];

        if (!config) {
            console.error(`No form config found for type: ${type}`);
            return;
        }

        config.fields.forEach(field => {
            const fieldDiv = document.createElement('div');
            fieldDiv.className = 'form-group';

            const label = document.createElement('label');
            label.textContent = field.label;
            label.setAttribute('for', field.name);

            let input;

            if (field.type === 'select') {
                input = document.createElement('select');
                input.name = field.name;
                input.id = field.name;
                input.required = field.required || false;

                field.options.forEach(option => {
                    const optionEl = document.createElement('option');
                    optionEl.value = option.value || option;
                    optionEl.textContent = option.label || option;
                    if (item && item[field.name] === (option.value || option)) {
                        optionEl.selected = true;
                    }
                    input.appendChild(optionEl);
                });
            } else if (field.type === 'textarea') {
                input = document.createElement('textarea');
                input.name = field.name;
                input.id = field.name;
                input.required = field.required || false;
                input.rows = 3;
                if (item) {
                    input.value = item[field.name] || '';
                }
            } else {
                input = document.createElement('input');
                input.type = field.type;
                input.name = field.name;
                input.id = field.name;
                input.required = field.required || false;
                
                if (field.type === 'number') {
                    input.min = field.min !== undefined ? field.min : '';  
                    input.step = field.step || 1;
                }
                
                if (item) {
                   
                    if (field.type === 'datetime-local' && item[field.name]) {
                        const date = new Date(item[field.name]);
                        input.value = date.toISOString().slice(0, 16); 
                    } else if (field.type === 'password') {
                       
                        input.value = ''; 
                        input.placeholder = 'Dejar en blanco para no cambiar';
                        input.required = false; 
                    } else {
                        input.value = item[field.name] !== undefined ? item[field.name] : '';
                    }
                }
            }

            if (field.placeholder) {
                input.placeholder = field.placeholder;
            }

            fieldDiv.appendChild(label);
            fieldDiv.appendChild(input);
            container.appendChild(fieldDiv);
        });
    }

    getFormConfigs() {
        return {
            usuario: {
                fields: [
                    { name: 'nombre', label: 'Nombre', type: 'text', required: true },
                    { name: 'correo', label: 'Correo', type: 'email', required: true },
                    { name: 'telefono', label: 'Teléfono', type: 'tel', placeholder: '+57 300 123 4567' },
                    { name: 'contraseña', label: 'Contraseña', type: 'password', required: false }, 
                    { 
                        name: 'rol', 
                        label: 'Rol', 
                        type: 'select', 
                        required: true,
                        options: [
                            { value: 'conductor', label: 'Conductor' },
                            { value: 'administrador', label: 'Administrador' }
                        ]
                    }
                ]
            },
            camion: {
                fields: [
                    { name: 'placa', label: 'Placa', type: 'text', required: true, placeholder: 'ABC123' },
                    { name: 'modelo', label: 'Modelo', type: 'text', required: true, placeholder: 'Volvo FH16' },
                    { name: 'marca', label: 'Marca', type: 'text', required: true },
                    { name: 'año', label: 'Año', type: 'number', required: true, min: 1900, max: new Date().getFullYear() + 5 },
                    { name: 'capacidad_kg', label: 'Capacidad (kg)', type: 'number', required: true, min: 1, step: 0.1 }
                ]
            },
            viaje: {
                fields: [
                    { name: 'codigo', label: 'Código', type: 'text', required: true, placeholder: 'VJ-001' },
                    { name: 'usuario_id', label: 'ID Usuario', type: 'number', required: true },
                    { name: 'camion_id', label: 'ID Camión', type: 'number', required: true },
                    { name: 'fecha_inicio', label: 'Fecha Inicio', type: 'datetime-local' },
                    { name: 'fecha_fin', label: 'Fecha Fin', type: 'datetime-local' },
                    { name: 'observaciones', label: 'Observaciones', type: 'textarea' },
                    { 
                        name: 'estado', 
                        label: 'Estado', 
                        type: 'select',
                        options: ['pendiente', 'en_curso', 'completado', 'cancelado']
                    }
                ]
            },
            ruta: {
                fields: [
                    { name: 'viaje_id', label: 'ID Viaje', type: 'number', required: true },
                    { name: 'nombre', label: 'Nombre de la Ruta', type: 'text', required: true, placeholder: 'Ruta Bogotá-Medellín' },
                    { name: 'origen', label: 'Origen', type: 'text', required: true },
                    { name: 'destino', label: 'Destino', type: 'text', required: true },
                    { name: 'distancia_km', label: 'Distancia (km)', type: 'number', min: 0, step: 0.1 },
                    { name: 'tiempo_estimado_hrs', label: 'Tiempo Estimado (horas)', type: 'number', min: 0, step: 0.1 }
                ]
            },
            checkpoint: {
                fields: [
                    { name: 'ruta_id', label: 'ID Ruta', type: 'number', required: true },
                    { name: 'direccion', label: 'Dirección', type: 'text', required: true, placeholder: 'Calle 123 #45-67' },
                    { name: 'latitud', label: 'Latitud', type: 'number', required: true, step: 0.000001, placeholder: '4.7110' },
                    { name: 'longitud', label: 'Longitud', type: 'number', required: true, step: 0.000001, placeholder: '-74.0721' },
                    { name: 'orden', label: 'Orden en la Ruta', type: 'number', required: true, min: 1 },
                    { name: 'hash', label: 'Hash del Checkpoint', type: 'text', required: true },
                    { name: 'blockchain_tx_hash', label: 'Hash Transacción Blockchain (opcional)', type: 'text' },
                    { 
                        name: 'estado', 
                        label: 'Estado', 
                        type: 'select',
                        options: ['pendiente', 'alcanzado', 'saltado']
                    }
                ]
            },
            incidente: {
                fields: [
                    { name: 'checkpoint_id', label: 'ID Checkpoint', type: 'number', required: true },
                    { name: 'descripcion', label: 'Descripción', type: 'textarea', required: true },
                    { 
                        name: 'tipo', 
                        label: 'Tipo', 
                        type: 'select',
                        required: true,
                        options: ['accidente', 'mecanico', 'trafico', 'clima', 'otro']
                    },
                    { 
                        name: 'gravedad', 
                        label: 'Gravedad', 
                        type: 'select',
                        options: ['baja', 'media', 'alta', 'critica']
                    },
                    { name: 'usuario_id', label: 'ID Usuario (opcional)', type: 'number' },
                    { 
                        name: 'resuelto', 
                        label: 'Resuelto', 
                        type: 'select',
                        options: [{value: 'false', label: 'No'}, {value: 'true', label: 'Sí'}]
                    }
                ]
            }
        };
    }


    async handleFormSubmit(e) {
        const form = e.target;
        const type = form.dataset.type;
        const mode = form.dataset.mode;
        const id = form.dataset.id;

        const submitBtn = form.querySelector('.submit-btn');
        this.showButtonLoading(submitBtn, true);

        try {
            const formData = new FormData(form);
            const data = {};
            
            for (let [key, value] of formData.entries()) {
               
                if (['usuario_id', 'camion_id', 'viaje_id', 'ruta_id', 'checkpoint_id', 'año', 'orden'].includes(key)) {
                    data[key] = value ? parseInt(value, 10) : null;
                }
               
                else if (['capacidad_kg', 'distancia_km', 'tiempo_estimado_hrs', 'latitud', 'longitud'].includes(key)) {
                    data[key] = value ? parseFloat(value) : null;
                }
               
                else if (key === 'resuelto') {
                    data[key] = value === 'true';
                }
               
                else if (['fecha_inicio', 'fecha_fin'].includes(key) && value) {
                   
                    data[key] = value; 
                }
               
                else {
                    data[key] = value;
                }
            }

           
            if (mode === 'edit' && type === 'usuario' && (!data['contraseña'] || data['contraseña'] === '')) {
                delete data['contraseña'];
            }

            if (mode === 'add') {
                await this.createItem(type, data);
            } else if (mode === 'edit') {       
                await this.updateItem(type, id, data);
            }
            this.showMessage(`${type.charAt(0).toUpperCase() + type.slice(1)} ${mode === 'add' ? 'creado' : 'actualizado'} correctamente`, 'success');
            this.loadTabData(this.currentTab);
        }
        catch (error) {
            console.error(`Error ${mode === 'add' ? 'creando' : 'actualizando'} ${type}:`, error);
            this.showMessage(`Error ${mode === 'add' ? 'creando' : 'actualizando'} ${type}: ${error.message}`, 'error');
        } finally {
            this.showButtonLoading(submitBtn, false);
            document.getElementById('form-modal').classList.add('hidden');
        }
    }



getApiType(type) {
   
    const typeMapping = {
        'usuario': 'usuarios',      
        'usuarios': 'usuarios',     
        'camion': 'camiones',      
        'camiones': 'camiones',     
        'viaje': 'viajes',          
        'viajes': 'viajes',         
        'ruta': 'rutas',            
        'rutas': 'rutas',           
        'checkpoint': 'checkpoints', 
        'checkpoints': 'checkpoints', 
        'incidente': 'incidentes',   
        'incidentes': 'incidentes'  
    };
    
    console.log(` Mapeo de tipo: "${type}" -> "${typeMapping[type] || type}"`);
    return typeMapping[type] || type;
}


async createItem(type, data) {
    const apiType = this.getApiType(type);
    console.log(`➕ Creando ${type} -> API endpoint: /admin/${apiType}`);
    
    try {
        const response = await this.apiRequest(`/admin/${apiType}`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
        return response;
    } catch (error) {
        throw error;
    }
}

async viewItem(type, id) {
    const apiType = this.getApiType(type);
    console.log(` Viendo ${type} ID:${id} -> API endpoint: /admin/${apiType}/${id}`);
    
    try {
        const item = await this.apiRequest(`/admin/${apiType}/${id}`);
        this.openViewModal(type, item);
    } catch (error) {
        this.showMessage(`Error cargando ${type}: ${error.message}`, 'error');
    }
}

async editItem(type, id) {
    const apiType = this.getApiType(type);
    console.log(` Editando ${type} ID:${id} -> API endpoint: /admin/${apiType}/${id}`);
    
    try {
        const item = await this.apiRequest(`/admin/${apiType}/${id}`);
        this.openFormModal(type, item);
    } catch (error) {
        this.showMessage(`Error cargando ${type}: ${error.message}`, 'error');
    }
}

async updateItem(type, id, data) {
    const apiType = this.getApiType(type);
    console.log(` Actualizando ${type} ID:${id} -> API endpoint: /admin/${apiType}/${id}`);
    
    try {
        const response = await this.apiRequest(`/admin/${apiType}/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
        return response;
    } catch (error) {
        throw error;
    }
}

async deleteItem(type, id) {
    if (!confirm(`¿Estás seguro de eliminar este ${type}? Esta acción es irreversible.`)) return;
    
    const apiType = this.getApiType(type);
    console.log(` Eliminando ${type} ID:${id} -> API endpoint: /admin/${apiType}/${id}`);
    console.log(` URL completa: ${this.API_BASE_URL}/admin/${apiType}/${id}`);
    
    try {
        await this.apiRequest(`/admin/${apiType}/${id}`, {
            method: 'DELETE'
        });
        
        this.showMessage(`${type.charAt(0).toUpperCase() + type.slice(1)} eliminado exitosamente`, 'success');
        this.loadTabData(this.currentTab);
    } catch (error) {
        console.error(` Error completo eliminando ${type}:`, error);
        this.showMessage(`Error eliminando ${type}: ${error.message}`, 'error');
    }
}

async resolveIncidente(id) {
    if (!confirm(`¿Estás seguro de marcar este incidente como RESUELTO?`)) return;

    try {
        await this.apiRequest(`/admin/incidentes/${id}/resolver`, {
            method: 'PUT'
        });
        
        this.showMessage('Incidente marcado como resuelto', 'success');
        this.loadTabData('incidentes');
    } catch (error) {
        this.showMessage(`Error resolviendo incidente: ${error.message}`, 'error');
    }
}


    openViewModal(type, item) {
        const modal = document.getElementById('view-modal');
        const title = document.getElementById('view-modal-title');  
        const content = document.getElementById('view-content'); 
        
        title.textContent = `Detalles de ${type.charAt(0).toUpperCase() + type.slice(1)}`;
        content.innerHTML = this.generateViewContent(type, item);
        
        modal.classList.remove('hidden');
    }

    generateViewContent(type, item) {
        let html = '<div class="view-content">';
        
        for (const [key, value] of Object.entries(item)) {
            let displayValue = value;
            if (['fecha_registro', 'fecha_inicio', 'fecha_fin', 'fecha_creacion', 'timestamp'].includes(key) && value) {
                displayValue = this.formatDate(value);
            } else if (key === 'resuelto') {
                displayValue = value ? 'Sí' : 'No';
            } else if (key === 'contraseña') { 
                continue; 
            } else if (key.includes('hash') && value) {
                displayValue = `<span title="${value}">${this.truncateHash(value, 30)}</span>`; 
            }
            
            html += `
                <div class="view-row">
                    <span class="view-label">${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</span>
                    <span class="view-value">${displayValue || 'N/A'}</span>
                </div>
            `;
        }
        
        html += '</div>';
        return html;
    }

  
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        try {
            const date = new Date(dateString);
            if (isNaN(date)) return 'N/A'; 
            return date.toLocaleString('es-CO', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (e) {
            console.warn("Could not format date:", dateString, e);
            return 'N/A';
        }
    }

    truncateHash(hash, length = 10) {
        if (!hash || hash.length <= length * 2 + 3) return hash;
        return `${hash.substring(0, length)}...${hash.substring(hash.length - length)}`;
    }

    showMessage(message, type = 'info', duration = 3000) {
        const container = document.getElementById('messageContainer');
        if (!container) return;

    
        container.innerHTML = '';
        container.classList.remove('hidden', 'info', 'success', 'error', 'warning');

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;

        container.appendChild(messageDiv);
        container.classList.remove('hidden');
        container.classList.add(type); 

        setTimeout(() => {
            container.classList.add('hidden');
            container.innerHTML = '';
        }, duration);
    }

    showLoading(show) {
        const loadingSpinner = document.getElementById('loadingSpinner');
        if (loadingSpinner) {
            if (show) {
                loadingSpinner.classList.remove('hidden');
            } else {
                loadingSpinner.classList.add('hidden');
            }
        }
    }

    showButtonLoading(button, show) {
        const spinner = button.querySelector('.spinner');
        const buttonText = button.querySelector('.btn-text');

        if (spinner && buttonText) {
            if (show) {
                spinner.classList.remove('hidden');
                buttonText.classList.add('hidden');
                button.disabled = true;
            } else {
                spinner.classList.add('hidden');
                buttonText.classList.remove('hidden');
                button.disabled = false;
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new AdminPanel();
});