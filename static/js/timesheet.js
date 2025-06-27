class Timesheet {
    constructor() {
        // Selektoren
        this.typeSelect = document.getElementById('activityType');
        this.customerSelect = document.getElementById('customer');
        this.projectSelect = document.getElementById('project');
        this.chargeableSelect = document.getElementById('chargeable');
        this.categorySelect = document.getElementById('category');
        this.commentInput = document.getElementById('comment');
        
        // Event-Listener
        this.typeSelect.addEventListener('change', () => this.handleTypeSelection());
        this.customerSelect.addEventListener('change', () => this.handleCustomerSelection());
        this.projectSelect.addEventListener('change', () => this.handleProjectSelection());
        this.chargeableSelect.addEventListener('change', () => this.handleChargeableSelection());
        
        // Initial laden
        this.loadTypes();
    }

    async loadTypes() {
        try {
            const response = await fetch('/api/types');
            const types = await response.json();
            
            this.typeSelect.innerHTML = '<option value="" selected disabled>Aktivitätstyp wählen</option>';
            types.forEach(type => {
                const option = document.createElement('option');
                option.value = type.id;
                option.textContent = type.name;
                this.typeSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Fehler beim Laden der Typen:', error);
            alert('Fehler beim Laden der Typen');
        }
    }

    async handleTypeSelection() {
        const typeId = this.typeSelect.value;
        this.resetSelections('type');
        
        if (typeId) {
            const selectedType = this.typeSelect.options[this.typeSelect.selectedIndex].text;
            if (selectedType === 'Kundenprojekte') {
                await this.loadCustomers(typeId);
                this.showCustomerFlow();
            } else {
                await this.loadDirectCategories(selectedType);
                this.showDirectCategoryFlow();
            }
        }
    }

    showCustomerFlow() {
        document.getElementById('customerSection').style.display = 'block';
        document.getElementById('projectSection').style.display = 'none';
        document.getElementById('chargeableSection').style.display = 'none';
        document.getElementById('categorySection').style.display = 'none';
    }

    showDirectCategoryFlow() {
        document.getElementById('customerSection').style.display = 'none';
        document.getElementById('projectSection').style.display = 'none';
        document.getElementById('chargeableSection').style.display = 'none';
        document.getElementById('categorySection').style.display = 'block';
    }

    async loadCustomers(typeId) {
        try {
            const response = await fetch(`/api/customers?type_id=${typeId}`);
            const customers = await response.json();
            
            this.customerSelect.innerHTML = '<option value="" selected disabled>Kunde wählen</option>';
            customers.forEach(customer => {
                const option = document.createElement('option');
                option.value = customer.id;
                option.textContent = customer.name;
                option.dataset.projects = JSON.stringify(customer.projects);
                this.customerSelect.appendChild(option);
            });
            
            this.customerSelect.disabled = false;
        } catch (error) {
            console.error('Fehler beim Laden der Kunden:', error);
            alert('Fehler beim Laden der Kunden');
        }
    }

    async handleCustomerSelection() {
        const selectedOption = this.customerSelect.selectedOptions[0];
        this.resetSelections('customer');
        
        if (selectedOption) {
            const projects = JSON.parse(selectedOption.dataset.projects);
            this.loadProjects(projects);
            document.getElementById('projectSection').style.display = 'block';
        }
    }

    loadProjects(projects) {
        this.projectSelect.innerHTML = '<option value="" selected disabled>Projekt wählen</option>';
        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = project.name;
            option.dataset.chargeableId = project.chargeable_project_id;
            option.dataset.nonChargeableId = project.non_chargeable_project_id;
            option.dataset.categories = JSON.stringify(project.categories);
            this.projectSelect.appendChild(option);
        });
        
        this.projectSelect.disabled = false;
    }

    handleProjectSelection() {
        const selectedOption = this.projectSelect.selectedOptions[0];
        this.resetSelections('project');
        
        if (selectedOption) {
            document.getElementById('chargeableSection').style.display = 'block';
            this.chargeableSelect.disabled = false;
        }
    }

    async handleChargeableSelection() {
        const isChargeable = this.chargeableSelect.value === 'true';
        const selectedProject = this.projectSelect.selectedOptions[0];
        this.resetSelections('chargeable');
        
        if (selectedProject) {
            const categories = JSON.parse(selectedProject.dataset.categories)
                .filter(cat => cat.is_chargeable === isChargeable);
            
            this.categorySelect.innerHTML = '<option value="" selected disabled>Kategorie wählen</option>';
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.description;
                this.categorySelect.appendChild(option);
            });
            
            document.getElementById('categorySection').style.display = 'block';
            this.categorySelect.disabled = false;
            
            // Setze die korrekte Projekt-ID basierend auf der Chargeable-Auswahl
            const projectId = isChargeable ? 
                selectedProject.dataset.chargeableId : 
                selectedProject.dataset.nonChargeableId;
            document.getElementById('projectId').value = projectId;
        }
    }

    async loadDirectCategories(activityType) {
        try {
            const response = await fetch(`/api/categories?type=${activityType}`);
            const categories = await response.json();
            
            this.categorySelect.innerHTML = '<option value="" selected disabled>Kategorie wählen</option>';
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.description;
                this.categorySelect.appendChild(option);
            });
            
            this.categorySelect.disabled = false;
        } catch (error) {
            console.error('Fehler beim Laden der Kategorien:', error);
            alert('Fehler beim Laden der Kategorien');
        }
    }

    resetSelections(level) {
        switch(level) {
            case 'type':
                this.customerSelect.innerHTML = '';
                this.customerSelect.disabled = true;
                // fall through
            case 'customer':
                this.projectSelect.innerHTML = '';
                this.projectSelect.disabled = true;
                // fall through
            case 'project':
                this.chargeableSelect.value = '';
                this.chargeableSelect.disabled = true;
                // fall through
            case 'chargeable':
                this.categorySelect.innerHTML = '';
                this.categorySelect.disabled = true;
                document.getElementById('projectId').value = '';
                break;
        }
    }
}

// Timesheet initialisieren
document.addEventListener('DOMContentLoaded', () => {
    new Timesheet();
}); 