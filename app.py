from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timesheet.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Datenbankmodelle
class ActivityType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    activities = db.relationship('Activity', backref='activity_type', lazy=True)
    customers = db.relationship('Customer', backref='activity_type', lazy=True)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('activity_type.id'), nullable=False)
    projects = db.relationship('Project', backref='customer', lazy=True, cascade='all, delete-orphan')

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    chargeable_project_id = db.Column(db.String(50), nullable=False)  # z.B. 312464.02.01.02
    non_chargeable_project_id = db.Column(db.String(50), nullable=False)  # z.B. 312464.02.01.04
    activities = db.relationship('Activity', backref='project', lazy=True, cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='project', lazy=True)

class Category(db.Model):
    id = db.Column(db.String(20), primary_key=True)  # z.B. H02006.13
    description = db.Column(db.String(100))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)  # Null für direkte Kategorien
    is_chargeable = db.Column(db.Boolean, nullable=True)  # Null für direkte Kategorien
    activities = db.relationship('Activity', backref='category', lazy=True)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)  # Null für non-customer activities
    type_id = db.Column(db.Integer, db.ForeignKey('activity_type.id'), nullable=False)
    category_id = db.Column(db.String(20), db.ForeignKey('category.id'), nullable=False)
    default_comment = db.Column(db.String(500))
    is_chargeable = db.Column(db.Boolean, default=True)
    billing_project_id = db.Column(db.String(50), nullable=False)  # Wird aus project.chargeable/non_chargeable_project_id abgeleitet
    timesheet_entries = db.relationship('TimesheetEntry', backref='activity', lazy=True)

class TimesheetEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Dauer in Sekunden
    comment = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Datenbank erstellen
with app.app_context():
    db.create_all()
    
    # Standard-Aktivitätstypen erstellen, falls sie noch nicht existieren
    activity_types = {
        'customer': 'Kundenprojekte',
        'internal': 'Arbeitszeit im Unternehmen',
        'absence': 'Abwesenheit'
    }
    
    for type_id, type_name in activity_types.items():
        if not ActivityType.query.filter_by(name=type_name).first():
            db.session.add(ActivityType(name=type_name))
    
    db.session.commit()

# Routen
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/configuration')
def configuration():
    return render_template('configuration.html')

# API-Routen
@app.route('/api/activities')
def get_activities():
    type_id = request.args.get('type_id')
    
    if not type_id:
        return jsonify({'error': 'Aktivitätstyp erforderlich'}), 400
    
    activities = Activity.query.filter_by(type_id=type_id).all()
    
    return jsonify([{
        'id': a.id,
        'name': a.name,
        'billing_project_id': a.billing_project_id,
        'category_id': a.category_id,
        'default_comment': a.default_comment,
        'is_chargeable': a.is_chargeable
    } for a in activities])

@app.route('/api/activities/<int:activity_id>', methods=['GET'])
def get_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    return jsonify({
        'id': activity.id,
        'name': activity.name,
        'project_id': activity.project_id,
        'category_id': activity.category_id,
        'default_comment': activity.default_comment,
        'is_chargeable': activity.is_chargeable,
        'customer_name': activity.customer_name,
        'type': activity.activity_type.name
    })

@app.route('/api/activities', methods=['POST'])
def create_activity():
    data = request.json
    
    if not all(k in data for k in ['name', 'billing_project_id', 'category_id', 'type_id']):
        return jsonify({'error': 'Fehlende erforderliche Felder'}), 400
    
    try:
        # Kategorie erstellen oder abrufen
        category = Category.query.get(data['category_id'])
        if not category:
            category = Category(id=data['category_id'])
            db.session.add(category)
        
        # Aktivität erstellen
        activity = Activity(
            name=data['name'],
            type_id=data['type_id'],
            category_id=data['category_id'],
            billing_project_id=data['billing_project_id'],
            is_chargeable=data.get('is_chargeable', False),
            default_comment=f"{data['name']} - "
        )
        db.session.add(activity)
        
        db.session.commit()
        return jsonify({'message': 'Aktivität erfolgreich erstellt'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/activities/<int:activity_id>', methods=['PUT'])
def update_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    data = request.json
    
    try:
        if 'name' in data:
            activity.name = data['name']
        if 'project_id' in data:
            activity.project_id = data['project_id']
        if 'category_id' in data:
            # Kategorie erstellen oder abrufen
            category = Category.query.get(data['category_id'])
            if not category:
                category = Category(id=data['category_id'])
                db.session.add(category)
            activity.category_id = data['category_id']
        if 'default_comment' in data:
            activity.default_comment = data['default_comment']
        if 'is_chargeable' in data:
            activity.is_chargeable = data['is_chargeable']
        if 'customer_name' in data:
            activity.customer_name = data['customer_name']
        
        db.session.commit()
        return jsonify({'message': 'Aktivität erfolgreich aktualisiert'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/activities/<int:activity_id>', methods=['DELETE'])
def delete_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    
    try:
        # Prüfen, ob es verknüpfte Zeiteinträge gibt
        if activity.timesheet_entries:
            return jsonify({
                'error': 'Aktivität kann nicht gelöscht werden, da bereits Zeiteinträge existieren'
            }), 400
        
        db.session.delete(activity)
        db.session.commit()
        return jsonify({'message': 'Aktivität erfolgreich gelöscht'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/timesheet', methods=['POST'])
def create_timesheet_entry():
    data = request.json
    
    if not all(k in data for k in ['activity', 'duration', 'comment', 'start_time']):
        return jsonify({'error': 'Fehlende erforderliche Felder'}), 400
    
    try:
        # Aktivität finden oder erstellen
        activity = None
        activity_data = data['activity']
        
        if activity_data['type_id']:
            # Für Kundenprojekte
            if 'customer_id' in activity_data and activity_data['customer_id']:
                activity = Activity.query.filter_by(
                    project_id=activity_data['project_id'],
                    is_chargeable=activity_data['is_chargeable'],
                    category_id=activity_data['category_id']
                ).first()
            # Für interne Aktivitäten und Abwesenheit
            else:
                activity = Activity.query.filter_by(
                    type_id=activity_data['type_id'],
                    category_id=activity_data['category_id']
                ).first()
        
        if not activity:
            return jsonify({'error': 'Aktivität nicht gefunden'}), 404
        
        entry = TimesheetEntry(
            activity_id=activity.id,
            start_time=datetime.fromisoformat(data['start_time'].replace('Z', '+00:00')),
            duration=data['duration'],
            comment=data['comment']
        )
        db.session.add(entry)
        db.session.commit()
        return jsonify({'message': 'Zeiteintrag erfolgreich erstellt'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/timesheet/weekly')
def get_weekly_timesheet():
    # Aktuellen Wochenbeginn ermitteln
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Wochenende ermitteln
    friday = monday + timedelta(days=4, hours=23, minutes=59, seconds=59)
    
    # Zeiteinträge der Woche abrufen
    entries = TimesheetEntry.query.filter(
        TimesheetEntry.start_time.between(monday, friday)
    ).join(Activity).all()
    
    # Einträge nach Aktivitäten gruppieren
    weekly_data = {}
    for entry in entries:
        activity_id = entry.activity_id
        if activity_id not in weekly_data:
            activity = entry.activity
            weekly_data[activity_id] = {
                'activity_id': activity_id,
                'activity_name': activity.name,
                'project_id': activity.project_id,
                'category_id': activity.category_id,
                'monday': 0,
                'tuesday': 0,
                'wednesday': 0,
                'thursday': 0,
                'friday': 0,
                'total': 0
            }
        
        # Tag bestimmen und Dauer addieren
        day_index = entry.start_time.weekday()
        day_name = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'][day_index]
        weekly_data[activity_id][day_name] += entry.duration
        weekly_data[activity_id]['total'] += entry.duration
    
    return jsonify(list(weekly_data.values()))

@app.route('/api/timesheet/comment')
def get_timesheet_comment():
    activity_id = request.args.get('activity_id')
    day = request.args.get('day')
    
    if not activity_id or not day:
        return jsonify({'error': 'Fehlende Parameter'}), 400
    
    try:
        # Aktuellen Wochenbeginn ermitteln
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Tag bestimmen
        day_index = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'].index(day)
        target_date = monday + timedelta(days=day_index)
        
        # Zeiteintrag für diesen Tag finden
        entry = TimesheetEntry.query.filter(
            TimesheetEntry.activity_id == activity_id,
            TimesheetEntry.start_time >= target_date,
            TimesheetEntry.start_time < target_date + timedelta(days=1)
        ).first()
        
        return jsonify({
            'comment': entry.comment if entry else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/timesheet/update', methods=['PUT'])
def update_timesheet_entry():
    data = request.json
    
    if not all(k in data for k in ['activity_id', 'day', 'duration', 'comment']):
        return jsonify({'error': 'Fehlende erforderliche Felder'}), 400
    
    try:
        # Aktuellen Wochenbeginn ermitteln
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Tag bestimmen
        day_index = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'].index(data['day'])
        target_date = monday + timedelta(days=day_index)
        
        # Bestehende Einträge für diesen Tag und diese Aktivität finden
        existing_entry = TimesheetEntry.query.filter(
            TimesheetEntry.activity_id == data['activity_id'],
            TimesheetEntry.start_time >= target_date,
            TimesheetEntry.start_time < target_date + timedelta(days=1)
        ).first()
        
        if existing_entry:
            existing_entry.duration = data['duration']
            existing_entry.comment = data['comment']
        else:
            new_entry = TimesheetEntry(
                activity_id=data['activity_id'],
                start_time=target_date,
                duration=data['duration'],
                comment=data['comment']
            )
            db.session.add(new_entry)
        
        db.session.commit()
        return jsonify({'message': 'Zeiteintrag erfolgreich aktualisiert'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API-Routen für die hierarchische Struktur
@app.route('/api/types')
def get_types():
    types = ActivityType.query.all()
    return jsonify([{
        'id': t.id,
        'name': t.name
    } for t in types])

@app.route('/api/customers')
def get_customers():
    type_id = request.args.get('type_id')
    if not type_id:
        return jsonify({'error': 'Aktivitätstyp erforderlich'}), 400
    
    customers = Customer.query.filter_by(type_id=type_id).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'projects': [{
            'id': p.id,
            'name': p.name,
            'chargeable_project_id': p.chargeable_project_id,
            'non_chargeable_project_id': p.non_chargeable_project_id,
            'categories': [{
                'id': cat.id,
                'description': cat.description,
                'is_chargeable': cat.is_chargeable
            } for cat in p.categories]
        } for p in c.projects]
    } for c in customers])

@app.route('/api/projects/<int:project_id>/categories')
def get_project_categories(project_id):
    categories = Category.query.filter_by(project_id=project_id).all()
    
    return jsonify([{
        'id': c.id,
        'description': c.description,
        'is_chargeable': c.is_chargeable
    } for c in categories])

@app.route('/api/categories')
def get_categories():
    activity_type = request.args.get('type')
    if not activity_type:
        return jsonify({'error': 'Aktivitätstyp erforderlich'}), 400
    
    if activity_type == 'Kundenprojekte':
        project_id = request.args.get('project_id')
        is_chargeable = request.args.get('is_chargeable', type=bool)
        if project_id is None or is_chargeable is None:
            return jsonify({'error': 'project_id und is_chargeable erforderlich für Kundenprojekte'}), 400
        
        categories = Category.query.filter_by(
            project_id=project_id,
            is_chargeable=is_chargeable
        ).all()
    else:
        # Direkte Kategorien für Arbeitszeit/Abwesenheit
        categories = Category.query.filter_by(
            project_id=None
        ).all()
    
    return jsonify([{
        'id': c.id,
        'description': c.description
    } for c in categories])

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.json
    
    if not all(k in data for k in ['customer_id', 'name', 'chargeable_project_id', 'non_chargeable_project_id']):
        return jsonify({'error': 'Fehlende erforderliche Felder'}), 400
    
    try:
        project = Project(
            name=data['name'],
            customer_id=data['customer_id'],
            chargeable_project_id=data['chargeable_project_id'],
            non_chargeable_project_id=data['non_chargeable_project_id']
        )
        db.session.add(project)
        db.session.commit()
        return jsonify({'message': 'Projekt erfolgreich erstellt'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.json
    
    if not all(k in data for k in ['project_id', 'name', 'category_id']):
        return jsonify({'error': 'Fehlende erforderliche Felder'}), 400
    
    try:
        # Erstelle zwei Kategorien - eine für chargeable, eine für non-chargeable
        chargeable_category = Category(
            id=f"{data['category_id']}.C",
            description=f"{data['name']} (Chargeable)",
            project_id=data['project_id'],
            is_chargeable=True
        )
        
        non_chargeable_category = Category(
            id=f"{data['category_id']}.NC",
            description=f"{data['name']} (Non-Chargeable)",
            project_id=data['project_id'],
            is_chargeable=False
        )
        
        db.session.add(chargeable_category)
        db.session.add(non_chargeable_category)
        db.session.commit()
        
        return jsonify({'message': 'Kategorien erfolgreich erstellt'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# API-Routen für die Konfiguration
@app.route('/api/customers', methods=['POST'])
def create_customer():
    data = request.json
    
    if not all(k in data for k in ['name', 'project_name', 'chargeable_project_id', 'non_chargeable_project_id', 'type_id']):
        return jsonify({'error': 'Fehlende erforderliche Felder'}), 400
    
    try:
        # Kunde erstellen
        customer = Customer(
            name=data['name'],
            type_id=data['type_id']
        )
        db.session.add(customer)
        db.session.flush()
        
        # Projekt erstellen
        project = Project(
            name=data['project_name'],
            customer_id=customer.id,
            chargeable_project_id=data['chargeable_project_id'],
            non_chargeable_project_id=data['non_chargeable_project_id']
        )
        db.session.add(project)
        
        db.session.commit()
        return jsonify({'message': 'Kunde erfolgreich erstellt'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    
    try:
        # Prüfen, ob es verknüpfte Zeiteinträge gibt
        for project in customer.projects:
            for activity in project.activities:
                if activity.timesheet_entries:
                    return jsonify({
                        'error': 'Kunde kann nicht gelöscht werden, da bereits Zeiteinträge existieren'
                    }), 400
        
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Kunde erfolgreich gelöscht'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    data = request.json
    
    try:
        if 'name' in data:
            customer.name = data['name']
        
        # Projekt aktualisieren
        if customer.projects:
            project = customer.projects[0]  # Nehme das erste Projekt
            
            if 'project_name' in data:
                project.name = data['project_name']
            if 'chargeable_project_id' in data:
                project.chargeable_project_id = data['chargeable_project_id']
            if 'non_chargeable_project_id' in data:
                project.non_chargeable_project_id = data['non_chargeable_project_id']
            
            # Kategorien aktualisieren
            if 'category_id' in data:
                base_category_id = data['category_id']
                
                # Lösche alte Kategorien
                Category.query.filter_by(project_id=project.id).delete()
                
                # Erstelle neue Kategorien
                chargeable_category = Category(
                    id=f"{base_category_id}.C.{project.id}",
                    description=f"{dict(H02006='UX Development', H02013='UI Development').get(base_category_id.split('.')[0])} (Chargeable)",
                    project_id=project.id,
                    is_chargeable=True
                )
                db.session.add(chargeable_category)
                
                non_chargeable_category = Category(
                    id=f"{base_category_id}.NC.{project.id}",
                    description=f"{dict(H02006='UX Development', H02013='UI Development').get(base_category_id.split('.')[0])} (Non-Chargeable)",
                    project_id=project.id,
                    is_chargeable=False
                )
                db.session.add(non_chargeable_category)
        
        db.session.commit()
        return jsonify({'message': 'Kunde erfolgreich aktualisiert'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return jsonify({
        'id': customer.id,
        'name': customer.name,
        'projects': [{
            'id': p.id,
            'name': p.name,
            'chargeable_project_id': p.chargeable_project_id,
            'non_chargeable_project_id': p.non_chargeable_project_id,
            'categories': [{
                'id': cat.id,
                'description': cat.description,
                'is_chargeable': cat.is_chargeable
            } for cat in p.categories]
        } for p in customer.projects]
    })

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.json
    
    try:
        if 'name' in data:
            project.name = data['name']
        if 'chargeable_project_id' in data:
            project.chargeable_project_id = data['chargeable_project_id']
        if 'non_chargeable_project_id' in data:
            project.non_chargeable_project_id = data['non_chargeable_project_id']
        
        db.session.commit()
        return jsonify({'message': 'Projekt erfolgreich aktualisiert'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/projects/<int:project_id>/categories', methods=['PUT'])
def update_project_categories(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.json
    
    if 'categories' not in data:
        return jsonify({'error': 'Keine Kategorien angegeben'}), 400
        
    try:
        # Bestehende Kategorien löschen
        Category.query.filter_by(project_id=project_id).delete()
        
        # Neue Kategorien erstellen
        for category_data in data['categories']:
            base_id = category_data['category_id']
            name = category_data['name']
            
            # Chargeable Kategorie
            chargeable_category = Category(
                id=f"{base_id}.C",
                description=f"{name} (Chargeable)",
                project_id=project_id,
                is_chargeable=True
            )
            db.session.add(chargeable_category)
            
            # Non-Chargeable Kategorie
            non_chargeable_category = Category(
                id=f"{base_id}.NC",
                description=f"{name} (Non-Chargeable)",
                project_id=project_id,
                is_chargeable=False
            )
            db.session.add(non_chargeable_category)
        
        db.session.commit()
        return jsonify({'message': 'Kategorien erfolgreich aktualisiert'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    try:
        # Prüfen, ob es verknüpfte Zeiteinträge gibt
        if any(activity.timesheet_entries for activity in project.activities):
            return jsonify({
                'error': 'Projekt kann nicht gelöscht werden, da bereits Zeiteinträge existieren'
            }), 400
        
        # Zuerst alle verknüpften Kategorien löschen
        Category.query.filter_by(project_id=project_id).delete()
        
        # Dann das Projekt selbst löschen
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': 'Projekt erfolgreich gelöscht'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
