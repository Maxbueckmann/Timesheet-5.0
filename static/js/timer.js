class Timer {
    constructor() {
        this.startTime = null;
        this.timerInterval = null;
        this.isRunning = false;
        this.elapsedSeconds = 0;

        // DOM-Elemente
        this.timerDisplay = document.getElementById('timer');
        this.startButton = document.getElementById('startTimer');
        this.stopButton = document.getElementById('stopTimer');
        this.commentInput = document.getElementById('comment');

        // Event-Listener
        this.startButton.addEventListener('click', () => this.start());
        this.stopButton.addEventListener('click', () => this.stop());

        // Event-Listener für Formular-Änderungen
        document.getElementById('categorySection').addEventListener('change', () => this.updateButtonState());
        this.commentInput.addEventListener('input', () => this.updateButtonState());
    }

    updateButtonState() {
        const category = document.getElementById('category');
        const hasCategory = category && category.value;
        const hasComment = this.commentInput.value.trim() !== '';
        
        this.startButton.disabled = !(hasCategory && hasComment);
    }

    start() {
        if (!this.isRunning) {
            this.startTime = new Date();
            this.isRunning = true;
            this.startButton.disabled = true;
            this.stopButton.disabled = false;
            this.commentInput.disabled = true;

            this.timerInterval = setInterval(() => {
                const now = new Date();
                this.elapsedSeconds = Math.floor((now - this.startTime) / 1000);
                this.updateDisplay();
            }, 1000);
        }
    }

    stop() {
        if (this.isRunning) {
            clearInterval(this.timerInterval);
            this.isRunning = false;
            this.startButton.disabled = false;
            this.stopButton.disabled = true;
            this.commentInput.disabled = false;

            // Zeiteintrag speichern
            this.saveTimeEntry();
        }
    }

    reset() {
        clearInterval(this.timerInterval);
        this.isRunning = false;
        this.elapsedSeconds = 0;
        this.startTime = null;
        this.updateDisplay();
        this.startButton.disabled = false;
        this.stopButton.disabled = true;
        this.commentInput.disabled = false;
        this.updateButtonState();
    }

    updateDisplay() {
        const hours = Math.floor(this.elapsedSeconds / 3600);
        const minutes = Math.floor((this.elapsedSeconds % 3600) / 60);
        const seconds = this.elapsedSeconds % 60;

        this.timerDisplay.textContent = 
            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    getSelectedActivity() {
        const type = document.getElementById('activityType');
        const customer = document.getElementById('customer');
        const project = document.getElementById('project');
        const chargeable = document.getElementById('chargeable');
        const category = document.getElementById('category');

        if (!type.value || !category.value) {
            throw new Error('Bitte wählen Sie einen Aktivitätstyp und eine Kategorie aus.');
        }

        // Für Kundenprojekte
        if (type.options[type.selectedIndex].text === 'Kundenprojekte') {
            if (!customer.value || !project.value || !chargeable.value) {
                throw new Error('Bitte füllen Sie alle Projektdetails aus.');
            }
        }

        return {
            type_id: type.value,
            customer_id: customer.value,
            project_id: project.value,
            is_chargeable: chargeable.value === 'true',
            category_id: category.value
        };
    }

    async saveTimeEntry() {
        try {
            const activity = this.getSelectedActivity();
            const comment = this.commentInput.value.trim();

            if (!comment) {
                throw new Error('Bitte geben Sie einen Kommentar ein.');
            }

            const response = await fetch('/api/timesheet', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    activity: activity,
                    duration: this.elapsedSeconds,
                    comment: comment,
                    start_time: this.startTime.toISOString()
                })
            });

            if (response.ok) {
                this.reset();
                this.commentInput.value = '';
                // Wochenübersicht aktualisieren
                window.dispatchEvent(new CustomEvent('timeEntryAdded'));
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Fehler beim Speichern des Zeiteintrags');
            }
        } catch (error) {
            console.error('Fehler:', error);
            alert(error.message || 'Fehler beim Speichern des Zeiteintrags');
        }
    }
}

// Timer initialisieren
document.addEventListener('DOMContentLoaded', () => {
    window.timer = new Timer();
}); 