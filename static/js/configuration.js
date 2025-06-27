class Configuration {
    constructor() {
        // Modals
        this.customerModal = new bootstrap.Modal(document.getElementById('customerModal'));
        this.projectModal = new bootstrap.Modal(document.getElementById('projectModal'));
        this.editProjectModal = new bootstrap.Modal(document.getElementById('editProjectModal'));
        this.categoryModal = new bootstrap.Modal(document.getElementById('categoryModal'));
        this.internalModal = new bootstrap.Modal(document.getElementById('internalModal'));
        this.absenceModal = new bootstrap.Modal(document.getElementById('absenceModal'));
        
        // Event-Listener
        document.getElementById('saveCustomer').addEventListener('click', () => this.saveCustomer());
        document.getElementById('deleteCustomerBtn').addEventListener('click', () => this.deleteCustomer(this.editId));
        document.getElementById('saveProject').addEventListener('click', () => this.saveProject());
        document.getElementById('saveEditProject').addEventListener('click', () => this.saveEditProject());
        document.getElementById('saveCategory').addEventListener('click', () => this.saveCategory());
        document.getElementById('saveInternal').addEventListener('click', () => this.saveInternal());
        document.getElementById('saveAbsence').addEventListener('click', () => this.saveAbsence());
        
        // Bearbeitungsmodus-Flag
        this.editMode = false;
        this.editId = null;
        
        // Initial laden
        this.loadAll();
    }

    async loadAll() {
        await this.loadCustomers();
        await this.loadInternalActivities();
        await this.loadAbsenceTypes();
    }

    async loadCustomers() {
        try {
            const response = await fetch('/api/customers?type_id=1');
            const customers = await response.json();
            const tbody = document.getElementById('customerTable');
            tbody.innerHTML = '';
            
            customers.forEach(customer => {
                const row = document.createElement('tr');
                
                // Kundenname-Zelle mit Buttons
                const nameCell = document.createElement('td');
                nameCell.innerHTML = `
                    <div class="d-flex align-items-center">
                        <span class="me-3">${customer.name}</span>
                        <button class="btn btn-sm btn-outline-primary me-2" onclick="window.config.editCustomer(${customer.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="window.config.deleteCustomer(${customer.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                `;
                
                // Projekte und Jobbezeichnungen
                const projectsCell = document.createElement('td');
                
                if (customer.projects && customer.projects.length > 0) {
                    // "Neues Projekt" Button am Anfang
                    const newProjectButton = document.createElement('div');
                    newProjectButton.className = 'mb-3';
                    newProjectButton.innerHTML = `
                        <button class="btn btn-sm btn-primary" onclick="window.config.openProjectModal(${customer.id})">
                            + Neues Projekt für ${customer.name}
                        </button>
                    `;
                    projectsCell.appendChild(newProjectButton);

                    // Projekte
                customer.projects.forEach(project => {
                        const projectDiv = document.createElement('div');
                        projectDiv.className = 'project-container';
                        
                        projectDiv.innerHTML = `
                            <div class="project-header">
                                <div class="d-flex justify-content-between align-items-start mb-3">
                                    <h6 class="mb-0">${project.name}</h6>
                                    <button class="btn btn-outline-primary btn-sm" onclick="window.config.editProject(${project.id}, '${project.name}', '${project.chargeable_project_id}', '${project.non_chargeable_project_id}')" title="Projektdetails bearbeiten">
                                        Projekt bearbeiten
                                    </button>
                                </div>
                                ${project.categories && project.categories.length > 0 ? `
                                    <div class="job-titles">
                                        ${project.categories
                                            .filter(cat => cat.is_chargeable)
                                            .map(cat => {
                                                const baseId = cat.id.replace(/\.(C|NC)$/, '');
                                                const baseDescription = cat.description.replace(/ \((Non-)?Chargeable\)/, '');
                                                return `<div class="job-title-container">
                                                    <span class="job-title-name">${baseDescription}</span>
                                                    <span class="job-title-id">${baseId}</span>
                                                </div>`;
                                            })
                                            .join('')}
                                        <div class="job-title-container add-job" onclick="window.config.openCategoryModal(${project.id})" style="cursor: pointer;">
                                            <span class="job-title-name">
                                                <span class="add-icon">+</span>
                                                Jobbezeichnung hinzufügen
                                            </span>
                                        </div>
                                    </div>
                                ` : `
                                    <div class="job-titles">
                                        <div class="job-title-container add-job" onclick="window.config.openCategoryModal(${project.id})" style="cursor: pointer;">
                                            <span class="job-title-name">
                                                <span class="add-icon">+</span>
                                                Jobbezeichnung hinzufügen
                                            </span>
                                        </div>
                                    </div>
                                `}
                            </div>
                        `;
                        
                        projectsCell.appendChild(projectDiv);
                    });
                } else {
                    projectsCell.innerHTML = `
                        <div class="text-center">
                            <p class="text-muted mb-2">Keine Projekte vorhanden</p>
                            <button class="btn btn-primary" onclick="window.config.openProjectModal(${customer.id})">
                                + Erstes Projekt für ${customer.name} anlegen
                            </button>
                        </div>
                    `;
                }
                
                row.appendChild(nameCell);
                row.appendChild(projectsCell);
                tbody.appendChild(row);
            });
        } catch (error) {
            console.error('Fehler beim Laden der Kunden:', error);
            alert('Fehler beim Laden der Kunden');
        }
    }

    async saveCustomer() {
        const customerName = document.getElementById('customerName').value.trim();
        
        if (!customerName) {
            alert('Bitte geben Sie einen Kundennamen ein');
            return;
        }
        
        try {
            let url = '/api/customers';
            let method = 'POST';
            let data = {
                name: customerName,
                type_id: 1
            };
            
            if (this.editMode) {
                url = `/api/customers/${this.editId}`;
                method = 'PUT';
            } else {
                // Zusätzliche Felder nur beim Erstellen
                data = {
                    ...data,
                    project_name: customerName,
                    chargeable_project_id: null,
                    non_chargeable_project_id: null
                };
            }
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                this.customerModal.hide();
                await this.loadCustomers();
            } else {
                throw new Error('Fehler beim Speichern des Kunden');
            }
        } catch (error) {
            console.error('Fehler beim Speichern:', error);
            alert('Fehler beim Speichern des Kunden');
        }
    }

    async saveProject() {
        const form = document.getElementById('projectForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const data = {
            customer_id: document.getElementById('projectCustomerId').value,
            name: document.getElementById('projectName').value,
            chargeable_project_id: document.getElementById('chargeableProjectId').value,
            non_chargeable_project_id: document.getElementById('nonChargeableProjectId').value
        };
        
        try {
            const response = await fetch('/api/projects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                this.projectModal.hide();
                form.reset();
                await this.loadCustomers();
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Fehler beim Speichern des Projekts');
            }
        } catch (error) {
            console.error('Fehler:', error);
            alert(error.message);
        }
    }

    openProjectModal(customerId) {
        document.getElementById('projectCustomerId').value = customerId;
        this.projectModal.show();
    }

    async saveCategory() {
        const form = document.getElementById('categoryForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const data = {
            project_id: document.getElementById('categoryProjectId').value,
            name: document.getElementById('categoryName').value,
            category_id: document.getElementById('categoryId').value
        };
        
        try {
            const response = await fetch('/api/categories', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                this.categoryModal.hide();
                form.reset();
                await this.loadCustomers();
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Fehler beim Speichern der Kategorie');
            }
        } catch (error) {
            console.error('Fehler:', error);
            alert(error.message);
        }
    }

    openCategoryModal(projectId) {
        document.getElementById('categoryProjectId').value = projectId;
        this.categoryModal.show();
    }

    async editCustomer(id) {
        this.editMode = true;
        this.editId = id;
        
        try {
            const response = await fetch(`/api/customers/${id}`);
            const customer = await response.json();
            
            document.getElementById('customerName').value = customer.name;
            document.querySelector('#customerModal .modal-title').textContent = 'Kunden bearbeiten';
            document.getElementById('deleteCustomerBtn').style.display = 'block';
            
            this.customerModal.show();
        } catch (error) {
            console.error('Fehler beim Laden der Kundendaten:', error);
            alert('Fehler beim Laden der Kundendaten');
        }
    }

    async deleteCustomer(id) {
        if (confirm('Möchten Sie diesen Kunden wirklich löschen?')) {
            try {
                const response = await fetch(`/api/customers/${id}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    this.customerModal.hide();
                    await this.loadCustomers();
                } else {
                    throw new Error('Fehler beim Löschen des Kunden');
                }
            } catch (error) {
                console.error('Fehler beim Löschen des Kunden:', error);
                alert('Fehler beim Löschen des Kunden');
            }
        }
    }

    openCustomerModal() {
        this.editMode = false;
        this.editId = null;
        document.getElementById('customerName').value = '';
        document.querySelector('#customerModal .modal-title').textContent = 'Neuen Kunden anlegen';
        document.getElementById('deleteCustomerBtn').style.display = 'none';
        this.customerModal.show();
    }

    async loadInternalActivities() {
        try {
            const response = await fetch('/api/activities?type_id=2');
            const activities = await response.json();
            
            const tbody = document.getElementById('internalTable');
            tbody.innerHTML = '';
            
            activities.forEach(activity => {
                const row = document.createElement('tr');
                
                // Name
                const nameCell = document.createElement('td');
                nameCell.textContent = activity.name;
                row.appendChild(nameCell);
                
                // Projekt-ID
                const projectIdCell = document.createElement('td');
                projectIdCell.textContent = activity.billing_project_id;
                row.appendChild(projectIdCell);
                
                // Kategorie
                const categoryCell = document.createElement('td');
                categoryCell.textContent = activity.category_id;
                row.appendChild(categoryCell);
                
                // Aktionen
                const actionsCell = document.createElement('td');
                const editBtn = document.createElement('button');
                editBtn.className = 'btn btn-sm btn-outline-primary me-2';
                editBtn.textContent = 'Bearbeiten';
                editBtn.addEventListener('click', () => this.editInternal(activity));
                
                const deleteBtn = document.createElement('button');
                deleteBtn.className = 'btn btn-sm btn-outline-danger';
                deleteBtn.textContent = 'Löschen';
                deleteBtn.addEventListener('click', () => this.deleteActivity(activity.id));
                
                actionsCell.appendChild(editBtn);
                actionsCell.appendChild(deleteBtn);
                row.appendChild(actionsCell);
                
                tbody.appendChild(row);
            });
        } catch (error) {
            console.error('Fehler beim Laden der internen Aktivitäten:', error);
            alert('Fehler beim Laden der internen Aktivitäten');
        }
    }

    async loadAbsenceTypes() {
        try {
            const response = await fetch('/api/activities?type_id=3');
            const activities = await response.json();
            
            const tbody = document.getElementById('absenceTable');
            tbody.innerHTML = '';
            
            activities.forEach(activity => {
                const row = document.createElement('tr');
                
                // Name
                const nameCell = document.createElement('td');
                nameCell.textContent = activity.name;
                row.appendChild(nameCell);
                
                // Projekt-ID
                const projectIdCell = document.createElement('td');
                projectIdCell.textContent = activity.billing_project_id;
                row.appendChild(projectIdCell);
                
                // Kategorie
                const categoryCell = document.createElement('td');
                categoryCell.textContent = activity.category_id;
                row.appendChild(categoryCell);
                
                // Aktionen
                const actionsCell = document.createElement('td');
                const editBtn = document.createElement('button');
                editBtn.className = 'btn btn-sm btn-outline-primary me-2';
                editBtn.textContent = 'Bearbeiten';
                editBtn.addEventListener('click', () => this.editAbsence(activity));
                
                const deleteBtn = document.createElement('button');
                deleteBtn.className = 'btn btn-sm btn-outline-danger';
                deleteBtn.textContent = 'Löschen';
                deleteBtn.addEventListener('click', () => this.deleteActivity(activity.id));
                
                actionsCell.appendChild(editBtn);
                actionsCell.appendChild(deleteBtn);
                row.appendChild(actionsCell);
                
                tbody.appendChild(row);
            });
        } catch (error) {
            console.error('Fehler beim Laden der Abwesenheitstypen:', error);
            alert('Fehler beim Laden der Abwesenheitstypen');
        }
    }

    editInternal(activity) {
        this.editMode = true;
        this.editId = activity.id;
        
        document.getElementById('internalName').value = activity.name;
        document.getElementById('internalCategoryId').value = activity.category_id;
        
        this.internalModal.show();
    }

    editAbsence(activity) {
        this.editMode = true;
        this.editId = activity.id;
        
        document.getElementById('absenceName').value = activity.name;
        document.getElementById('absenceCategoryId').value = activity.category_id;
        
        this.absenceModal.show();
    }

    async saveInternal() {
        const form = document.getElementById('internalForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const data = {
            name: document.getElementById('internalName').value,
            billing_project_id: document.getElementById('internalProjectId').value,
            category_id: document.getElementById('internalCategoryId').value,
            type_id: 2,
            is_chargeable: false
        };
        
        try {
            const url = this.editMode ? `/api/activities/${this.editId}` : '/api/activities';
            const method = this.editMode ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                this.internalModal.hide();
                form.reset();
                this.editMode = false;
                this.editId = null;
                await this.loadInternalActivities();
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Fehler beim Speichern der Aktivität');
            }
        } catch (error) {
            console.error('Fehler:', error);
            alert(error.message);
        }
    }

    async saveAbsence() {
        const form = document.getElementById('absenceForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const data = {
            name: document.getElementById('absenceName').value,
            billing_project_id: document.getElementById('absenceProjectId').value,
            category_id: document.getElementById('absenceCategoryId').value,
            type_id: 3,
            is_chargeable: false
        };
        
        try {
            const url = this.editMode ? `/api/activities/${this.editId}` : '/api/activities';
            const method = this.editMode ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                this.absenceModal.hide();
                form.reset();
                this.editMode = false;
                this.editId = null;
                await this.loadAbsenceTypes();
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Fehler beim Speichern der Aktivität');
            }
        } catch (error) {
            console.error('Fehler:', error);
            alert(error.message);
        }
    }

    async deleteActivity(id) {
        if (!confirm('Möchten Sie diese Aktivität wirklich löschen?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/activities/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                await this.loadAll();
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Fehler beim Löschen der Aktivität');
            }
        } catch (error) {
            console.error('Fehler:', error);
            alert(error.message);
        }
    }

    editProject(projectId, name, chargeableId, nonChargeableId) {
        document.getElementById('editProjectId').value = projectId;
        document.getElementById('editProjectName').value = name;
        document.getElementById('editChargeableProjectId').value = chargeableId;
        document.getElementById('editNonChargeableProjectId').value = nonChargeableId;
        
        // Jobbezeichnungen laden
        this.loadProjectCategories(projectId);
        
        this.editProjectModal.show();
    }

    async loadProjectCategories(projectId) {
        try {
            const response = await fetch(`/api/projects/${projectId}/categories`);
            if (!response.ok) {
                throw new Error('Fehler beim Laden der Jobbezeichnungen');
            }
            const categories = await response.json();
            
            const jobList = document.getElementById('editJobList');
            jobList.innerHTML = '';
            
            // Nur die Chargeable-Kategorien anzeigen (da Non-Chargeable automatisch erstellt werden)
            categories
                .filter(cat => cat.is_chargeable)
                .forEach(category => {
                    const baseId = category.id.replace(/\.(C|NC)$/, '');
                    const baseDescription = category.description.replace(/ \((Non-)?Chargeable\)/, '');
                    this.addJobRow(baseDescription, baseId);
                });
            
        } catch (error) {
            console.error('Fehler:', error);
            alert(error.message);
        }
    }

    addJobRow(description = '', categoryId = '') {
        const jobList = document.getElementById('editJobList');
        const jobRow = document.createElement('div');
        jobRow.className = 'job-row';
        
        jobRow.innerHTML = `
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label">Jobbezeichnung</label>
                    <input type="text" class="form-control job-description" value="${description}" required>
                </div>
                <div class="col-md-5">
                    <label class="form-label">Kategorie-ID</label>
                    <input type="text" class="form-control job-category-id" value="${categoryId}" 
                           pattern="^H\d{5}(\.\d{1,2})?$" required>
                    <small class="form-text text-muted">Format: H02006.13</small>
                </div>
                <div class="col-md-1 d-flex align-items-end">
                    <button type="button" class="btn btn-sm btn-outline-danger" onclick="this.closest('.job-row').remove()">
                        <i class="bi bi-trash-fill"></i> Löschen
                    </button>
                </div>
            </div>
        `;
        
        jobList.appendChild(jobRow);
    }

    async saveEditProject() {
        const form = document.getElementById('editProjectForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const projectId = document.getElementById('editProjectId').value;
        const projectData = {
            name: document.getElementById('editProjectName').value,
            chargeable_project_id: document.getElementById('editChargeableProjectId').value,
            non_chargeable_project_id: document.getElementById('editNonChargeableProjectId').value
        };
        
        try {
            // Projekt aktualisieren
            const projectResponse = await fetch(`/api/projects/${projectId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(projectData)
            });
            
            if (!projectResponse.ok) {
                throw new Error('Fehler beim Speichern des Projekts');
            }
            
            // Jobbezeichnungen sammeln
            const jobRows = document.querySelectorAll('#editJobList .job-row');
            const categories = Array.from(jobRows).map(row => ({
                name: row.querySelector('.job-description').value,
                category_id: row.querySelector('.job-category-id').value
            }));
            
            // Bestehende Kategorien löschen und neue erstellen
            const categoriesResponse = await fetch(`/api/projects/${projectId}/categories`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ categories })
            });
            
            if (!categoriesResponse.ok) {
                throw new Error('Fehler beim Speichern der Jobbezeichnungen');
            }
            
            this.editProjectModal.hide();
            form.reset();
            await this.loadCustomers();
            
        } catch (error) {
            console.error('Fehler:', error);
            alert(error.message);
        }
    }

    async deleteProject(projectId) {
        if (!confirm('Möchten Sie dieses Projekt wirklich löschen?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/projects/${projectId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                await this.loadCustomers();
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Fehler beim Löschen des Projekts');
            }
        } catch (error) {
            console.error('Fehler:', error);
            alert(error.message);
        }
    }
}

// Configuration initialisieren
document.addEventListener('DOMContentLoaded', () => {
    window.config = new Configuration();
}); 