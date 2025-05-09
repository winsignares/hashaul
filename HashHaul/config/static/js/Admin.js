document.addEventListener("DOMContentLoaded", () => {
   
    const datos = {
      usuarios: [
        {
          id: "CM-4587",
          nombre: "Juan Perez",
          telefono: "+57 312 456 7890",
          licencia: "B2-987654",
          camion: "XJ96-K",
          experiencia: "7",
          historialRutas: "152",
          ultimaRuta: "28-02-2025",
          estado: "Activo",
        },
        {
          id: "CM-2345",
          nombre: "María López",
          telefono: "+57 315 789 1234",
          licencia: "B2-123456",
          camion: "D67D",
          experiencia: "5",
          historialRutas: "87",
          ultimaRuta: "25-02-2025",
          estado: "Inactivo",
        },
      ],
      camiones: [
        {
          id: "XJ96-K",
          modelo: "Volvo FH16",
          capacidad: "40 toneladas",
          estado: "Activo",
          ultimoMantenimiento: "15-01-2025",
        },
        {
          id: "D67D",
          modelo: "Scania R500",
          capacidad: "35 toneladas",
          estado: "Activo",
          ultimoMantenimiento: "20-01-2025",
        },
      ],
      viajes: [
        {
          id: "9a367d5a87c5e6a87d",
          fecha: "28-02-2025",
          hora: "08:15 - 16:45",
          conductor: "Juan Perez",
          camion: "XJ96-K",
          cargamento: "3219hsjdk820s",
          estado: "Completado",
          checkpoints: "5",
        },
        {
          id: "4jkh23hjk4hkj234",
          fecha: "30-02-2025",
          hora: "14:20 pm",
          conductor: "Pendiente",
          camion: "D67D",
          cargamento: "8924jfdkls",
          estado: "Pendiente",
          checkpoints: "4",
        },
      ],
      rutas: [
        {
          id: "9a367d5a87c5e6a87d",
          origen: "Bogotá",
          destino: "Medellín",
          distancia: "420 km",
          tiempoEstimado: "8 horas",
          viajeId: "9a367d5a87c5e6a87d",
        },
      ],
      checkpoints: [
        {
          id: "cp-001",
          ubicacion: "Calle 12 #45-78, Bogotá",
          hora: "09:00 AM",
          valor: "$5,000,000",
          estado: "Entregado",
          rutaId: "9a367d5a87c5e6a87d",
        },
      ],
      incidentes: [
        {
          id: "inc-001",
          tipo: "Avería",
          descripcion: "Fallo en el sistema de frenos",
          fecha: "27-02-2025",
          hora: "14:30",
          viajeId: "9a367d5a87c5e6a87d",
          estado: "Resuelto",
        },
      ],
    }
  

    const navItems = document.querySelectorAll(".nav-item")
    const views = document.querySelectorAll(".view")
  
    navItems.forEach((item) => {
      item.addEventListener("click", function (e) {
        e.preventDefault()
  
    
        navItems.forEach((nav) => nav.classList.remove("active"))
        this.classList.add("active")
  
        
        const viewId = this.getAttribute("data-view") + "-view"
        views.forEach((view) => view.classList.add("hidden"))
        document.getElementById(viewId).classList.remove("hidden")
  
     
        document.querySelector(".page-title").textContent = this.textContent
      })
    })
  

    const tabBtns = document.querySelectorAll(".tab-btn")
    const tabPanes = document.querySelectorAll(".tab-pane")
  
    tabBtns.forEach((btn) => {
      btn.addEventListener("click", function () {
       
        tabBtns.forEach((tab) => tab.classList.remove("active"))
        this.classList.add("active")
  
       
        const tabId = this.getAttribute("data-tab") + "-tab"
        tabPanes.forEach((pane) => pane.classList.remove("active"))
        document.getElementById(tabId).classList.add("active")
      })
    })
  

    const formConfigs = {
      usuario: {
        title: "Usuario",
        fields: [
          { name: "id", label: "ID Conductor", type: "text" },
          { name: "nombre", label: "Nombre", type: "text" },
          { name: "telefono", label: "Teléfono", type: "text" },
          { name: "licencia", label: "Licencia", type: "text" },
          { name: "camion", label: "Camión Asignado", type: "text" },
          { name: "experiencia", label: "Años de Experiencia", type: "number" },
          { name: "historialRutas", label: "Historial de Rutas", type: "number" },
          { name: "ultimaRuta", label: "Última Ruta", type: "date" },
          { name: "estado", label: "Estado", type: "select", options: ["Activo", "Inactivo"] },
        ],
      },
      camion: {
        title: "Camión",
        fields: [
          { name: "id", label: "ID", type: "text" },
          { name: "modelo", label: "Modelo", type: "text" },
          { name: "capacidad", label: "Capacidad", type: "text" },
          {
            name: "estado",
            label: "Estado",
            type: "select",
            options: ["Activo", "En mantenimiento", "Fuera de servicio"],
          },
          { name: "ultimoMantenimiento", label: "Último Mantenimiento", type: "date" },
        ],
      },
      viaje: {
        title: "Viaje",
        fields: [
          { name: "id", label: "ID", type: "text" },
          { name: "fecha", label: "Fecha", type: "date" },
          { name: "hora", label: "Hora", type: "text" },
          { name: "conductor", label: "Conductor", type: "text" },
          { name: "camion", label: "Camión", type: "text" },
          { name: "cargamento", label: "Cargamento", type: "text" },
          {
            name: "estado",
            label: "Estado",
            type: "select",
            options: ["Pendiente", "En progreso", "Completado", "Cancelado"],
          },
          { name: "checkpoints", label: "Número de Checkpoints", type: "number" },
        ],
      },
      ruta: {
        title: "Ruta",
        fields: [
          { name: "id", label: "ID", type: "text" },
          { name: "origen", label: "Origen", type: "text" },
          { name: "destino", label: "Destino", type: "text" },
          { name: "distancia", label: "Distancia", type: "text" },
          { name: "tiempoEstimado", label: "Tiempo Estimado", type: "text" },
          { name: "viajeId", label: "ID de Viaje", type: "text" },
        ],
      },
      checkpoint: {
        title: "Checkpoint",
        fields: [
          { name: "id", label: "ID", type: "text" },
          { name: "ubicacion", label: "Ubicación", type: "text" },
          { name: "hora", label: "Hora", type: "text" },
          { name: "valor", label: "Valor", type: "text" },
          { name: "estado", label: "Estado", type: "select", options: ["Pendiente", "Entregado", "Cancelado"] },
          { name: "rutaId", label: "ID de Ruta", type: "text" },
        ],
      },
      incidente: {
        title: "Incidente",
        fields: [
          { name: "id", label: "ID", type: "text" },
          { name: "tipo", label: "Tipo", type: "select", options: ["Avería", "Accidente", "Retraso", "Otro"] },
          { name: "descripcion", label: "Descripción", type: "textarea" },
          { name: "fecha", label: "Fecha", type: "date" },
          { name: "hora", label: "Hora", type: "text" },
          { name: "viajeId", label: "ID de Viaje", type: "text" },
          { name: "estado", label: "Estado", type: "select", options: ["Pendiente", "En proceso", "Resuelto"] },
        ],
      },
    }
  
    
    const formModal = document.getElementById("form-modal")
    const viewModal = document.getElementById("view-modal")
    const closeModalBtns = document.querySelectorAll(".close-modal")
    const cancelBtn = document.querySelector(".cancel-btn")
    const closeBtn = document.querySelector(".close-btn")
    const dataForm = document.getElementById("data-form")
    const formFields = document.getElementById("form-fields")
    const modalTitle = document.getElementById("modal-title")
    const viewTitle = document.getElementById("view-title")
    const viewContent = document.getElementById("view-content")
  
    
    function cerrarFormModal() {
      formModal.style.display = "none"
    }
  
    function cerrarViewModal() {
      viewModal.style.display = "none"
    }
  
    closeModalBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        cerrarFormModal()
        cerrarViewModal()
      })
    })
  
    cancelBtn.addEventListener("click", cerrarFormModal)
    closeBtn.addEventListener("click", cerrarViewModal)
  
    window.addEventListener("click", (e) => {
      if (e.target === formModal) {
        cerrarFormModal()
      }
      if (e.target === viewModal) {
        cerrarViewModal()
      }
    })
  
 
    function generarFormulario(tipo, item = null) {
      const config = formConfigs[tipo]
      modalTitle.textContent = item ? `Editar ${config.title}` : `Agregar ${config.title}`
  
      formFields.innerHTML = ""
  
      config.fields.forEach((field) => {
        const fieldDiv = document.createElement("div")
        fieldDiv.className = "form-group"
  
        const label = document.createElement("label")
        label.textContent = field.label
        label.setAttribute("for", field.name)
  
        let input
  
        if (field.type === "select") {
          input = document.createElement("select")
          input.name = field.name
          input.id = field.name
  
          field.options.forEach((option) => {
            const optionEl = document.createElement("option")
            optionEl.value = option
            optionEl.textContent = option
            if (item && item[field.name] === option) {
              optionEl.selected = true
            }
            input.appendChild(optionEl)
          })
        } else if (field.type === "textarea") {
          input = document.createElement("textarea")
          input.name = field.name
          input.id = field.name
          if (item) {
            input.value = item[field.name] || ""
          }
        } else {
          input = document.createElement("input")
          input.type = field.type
          input.name = field.name
          input.id = field.name
          if (item) {
            input.value = item[field.name] || ""
          }
        }
  
        fieldDiv.appendChild(label)
        fieldDiv.appendChild(input)
        formFields.appendChild(fieldDiv)
      })
  
      dataForm.setAttribute("data-type", tipo)
      dataForm.setAttribute("data-mode", item ? "edit" : "add")
      if (item) {
        dataForm.setAttribute("data-id", item.id)
      } else {
        dataForm.removeAttribute("data-id")
      }
    }
  
  
    function generarVistaDetalles(tipo, item) {
      const config = formConfigs[tipo]
      viewTitle.textContent = `Detalles de ${config.title}: ${item.id}`
  
      viewContent.innerHTML = ""
  
      config.fields.forEach((field) => {
        const detailDiv = document.createElement("div")
        detailDiv.className = "detail-item"
  
        const label = document.createElement("div")
        label.className = "detail-label"
        label.textContent = field.label + ":"
  
        const value = document.createElement("div")
        value.className = "detail-value"
        value.textContent = item[field.name] || "N/A"
  
        detailDiv.appendChild(label)
        detailDiv.appendChild(value)
        viewContent.appendChild(detailDiv)
      })
    }
  
    
    document.getElementById("add-usuario-btn").addEventListener("click", () => {
      generarFormulario("usuario")
      formModal.style.display = "block"
    })
  
    document.getElementById("add-camion-btn").addEventListener("click", () => {
      generarFormulario("camion")
      formModal.style.display = "block"
    })
  
    document.getElementById("add-viaje-btn").addEventListener("click", () => {
      generarFormulario("viaje")
      formModal.style.display = "block"
    })
  
    document.getElementById("add-ruta-btn").addEventListener("click", () => {
      generarFormulario("ruta")
      formModal.style.display = "block"
    })
  
    document.getElementById("add-checkpoint-btn").addEventListener("click", () => {
      generarFormulario("checkpoint")
      formModal.style.display = "block"
    })
  
    document.getElementById("add-incidente-btn").addEventListener("click", () => {
      generarFormulario("incidente")
      formModal.style.display = "block"
    })
  
  
    document.addEventListener("click", (e) => {
      if (e.target.classList.contains("view-btn")) {
        const id = e.target.getAttribute("data-id")
        const tipo = e.target.getAttribute("data-type")
  
        
        const item = datos[tipo + "s"].find((item) => item.id === id)
  
        if (item) {
          generarVistaDetalles(tipo, item)
          viewModal.style.display = "block"
        }
      }
  
      if (e.target.classList.contains("edit-btn")) {
        const id = e.target.getAttribute("data-id")
        const tipo = e.target.getAttribute("data-type")
  
      
        const item = datos[tipo + "s"].find((item) => item.id === id)
  
        if (item) {
          generarFormulario(tipo, item)
          formModal.style.display = "block"
        }
      }
  
      if (e.target.classList.contains("delete-btn")) {
        const id = e.target.getAttribute("data-id")
        const tipo = e.target.getAttribute("data-type")
  
        if (confirm(`¿Estás seguro de que deseas eliminar este ${tipo}?`)) {
       
          alert(`${tipo.charAt(0).toUpperCase() + tipo.slice(1)} con ID ${id} eliminado correctamente.`)
        }
      }
    })
  

    dataForm.addEventListener("submit", function (e) {
      e.preventDefault()
  
      const tipo = this.getAttribute("data-type")
      const modo = this.getAttribute("data-mode")
      const id = this.getAttribute("data-id")
  
  
      const formData = {}
      const inputs = this.querySelectorAll("input, select, textarea")
      inputs.forEach((input) => {
        formData[input.name] = input.value
      })
  
      
      if (modo === "add") {
        alert(`Nuevo ${tipo} creado correctamente.`)
      } else {
        alert(`${tipo.charAt(0).toUpperCase() + tipo.slice(1)} con ID ${id} actualizado correctamente.`)
      }
  
    
      cerrarFormModal()
    })
  })
  