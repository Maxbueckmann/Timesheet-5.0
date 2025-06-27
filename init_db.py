from app import app, db, ActivityType, Category, Activity, Customer, Project

def init_db():
    with app.app_context():
        print("Lösche bestehende Datenbank...")
        db.drop_all()
        
        print("Erstelle Datenbankstruktur...")
        db.create_all()

        print("Erstelle Aktivitätstypen...")
        # Standard-Aktivitätstypen
        activity_types = {
            'customer': 'Kundenprojekte',
            'internal': 'Arbeitszeit im Unternehmen',
            'absence': 'Abwesenheit'
        }
        
        type_objects = {}
        for type_id, type_name in activity_types.items():
            type_obj = ActivityType(name=type_name)
            db.session.add(type_obj)
            db.session.flush()
            type_objects[type_id] = type_obj
        
        print("Erstelle Kategorien...")
        # Kategorien erstellen
        categories = [
            # Abwesenheit (project_id ist None für direkte Kategorien)
            Category(id='H03147', description='Other Paid Time off', project_id=None, is_chargeable=False),
            Category(id='H03128', description='Sickness Leave', project_id=None, is_chargeable=False),
            Category(id='H03118', description='Holiday Time', project_id=None, is_chargeable=False),
            Category(id='H03003', description='Special Leave', project_id=None, is_chargeable=False),
            
            # Interne Arbeit (project_id ist None für direkte Kategorien)
            Category(id='H03107', description='Professional Development', project_id=None, is_chargeable=False),
            Category(id='H03108', description='Career Development/Mentoring', project_id=None, is_chargeable=False),
            Category(id='H03104', description='Non-client meetings', project_id=None, is_chargeable=False),
            Category(id='H03105', description='Non-client operational activities', project_id=None, is_chargeable=False)
            
            # Kundenkategorien werden später beim Erstellen der Projekte hinzugefügt
        ]
        
        for category in categories:
            db.session.add(category)
        db.session.flush()

        print("Erstelle Kunden und Projekte...")
        # Kunden und ihre Projekte
        customers_data = [
            {
                'name': 'Siemens',
                'projects': [
                    {
                        'name': 'Xcelerator',
                        'activities': [
                            {
                                'name': 'Xcelerator UX',
                                'billing_project_id': '312464.02.01.02',
                                'category_id': 'H02006.13',
                                'is_chargeable': True,
                                'default_comment': 'Xcelerator UX Development - '
                            },
                            {
                                'name': 'Xcelerator UX Support',
                                'billing_project_id': '312464.02.01.04',
                                'category_id': 'H02006.13',
                                'is_chargeable': False,
                                'default_comment': 'Xcelerator UX Support - '
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'Customer A',
                'projects': [
                    {
                        'name': 'Project Alpha',
                        'activities': [
                            {
                                'name': 'Project Alpha Development',
                                'billing_project_id': '312464.03.01.02',
                                'category_id': 'H02006.13',
                                'is_chargeable': True,
                                'default_comment': 'Project Alpha Development - '
                            },
                            {
                                'name': 'Project Alpha Support',
                                'billing_project_id': '312464.03.01.04',
                                'category_id': 'H02006.13',
                                'is_chargeable': False,
                                'default_comment': 'Project Alpha Support - '
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'Customer B',
                'projects': [
                    {
                        'name': 'Project Beta',
                        'activities': [
                            {
                                'name': 'Project Beta Development',
                                'billing_project_id': '312464.04.01.02',
                                'category_id': 'H02013.1',
                                'is_chargeable': True,
                                'default_comment': 'Project Beta Development - '
                            },
                            {
                                'name': 'Project Beta Support',
                                'billing_project_id': '312464.04.01.04',
                                'category_id': 'H02013.1',
                                'is_chargeable': False,
                                'default_comment': 'Project Beta Support - '
                            }
                        ]
                    }
                ]
            }
        ]

        # Kunden und Projekte erstellen
        for customer_data in customers_data:
            customer = Customer(
                name=customer_data['name'],
                type_id=type_objects['customer'].id
            )
            db.session.add(customer)
            db.session.flush()

            for project_data in customer_data['projects']:
                # Extrahiere die Projekt-IDs aus den Aktivitäten
                chargeable_activity = next(
                    (a for a in project_data['activities'] if a['is_chargeable']),
                    None
                )
                non_chargeable_activity = next(
                    (a for a in project_data['activities'] if not a['is_chargeable']),
                    None
                )
                
                project = Project(
                    name=project_data['name'],
                    customer_id=customer.id,
                    chargeable_project_id=chargeable_activity['billing_project_id'],
                    non_chargeable_project_id=non_chargeable_activity['billing_project_id']
                )
                db.session.add(project)
                db.session.flush()

                # Erstelle die projektspezifischen Kategorien
                categories = set(a['category_id'] for a in project_data['activities'])
                for category_id in categories:
                    # Erstelle zwei Versionen der Kategorie: chargeable und non-chargeable
                    Category(
                        id=f"{category_id}.C.{project.id}",
                        description=f"{dict(H02006='UX Development', H02013='UI Development').get(category_id.split('.')[0])} (Chargeable)",
                        project_id=project.id,
                        is_chargeable=True
                    )
                    Category(
                        id=f"{category_id}.NC.{project.id}",
                        description=f"{dict(H02006='UX Development', H02013='UI Development').get(category_id.split('.')[0])} (Non-Chargeable)",
                        project_id=project.id,
                        is_chargeable=False
                    )
                db.session.flush()

                for activity_data in project_data['activities']:
                    # Verwende die korrekte Kategorie-ID basierend auf is_chargeable
                    category_suffix = '.C.' if activity_data['is_chargeable'] else '.NC.'
                    activity_category_id = f"{activity_data['category_id']}{category_suffix}{project.id}"
                    
                    activity = Activity(
                        name=activity_data['name'],
                        project_id=project.id,
                        type_id=type_objects['customer'].id,
                        category_id=activity_category_id,
                        billing_project_id=activity_data['billing_project_id'],
                        is_chargeable=activity_data['is_chargeable'],
                        default_comment=activity_data['default_comment']
                    )
                    db.session.add(activity)

        print("Erstelle Abwesenheits-Aktivitäten...")
        # Abwesenheits-Aktivitäten
        absence_activities = [
            {
                'name': 'Uni Zeit',
                'billing_project_id': '890085',
                'category_id': 'H03147',
                'default_comment': 'University Time - Monthly Timesheet'
            },
            {
                'name': 'Krankheit',
                'billing_project_id': '890085',
                'category_id': 'H03128',
                'default_comment': 'Sick Leave'
            },
            {
                'name': 'Urlaub',
                'billing_project_id': '890085',
                'category_id': 'H03118',
                'default_comment': 'Holiday Time'
            },
            {
                'name': 'Sonderurlaub',
                'billing_project_id': '890085',
                'category_id': 'H03003',
                'default_comment': 'Special Leave - '
            }
        ]

        for activity_data in absence_activities:
            activity = Activity(
                name=activity_data['name'],
                type_id=type_objects['absence'].id,
                billing_project_id=activity_data['billing_project_id'],
                category_id=activity_data['category_id'],
                default_comment=activity_data['default_comment'],
                is_chargeable=False
            )
            db.session.add(activity)

        print("Erstelle interne Aktivitäten...")
        # Interne Aktivitäten
        internal_activities = [
            {
                'name': 'Training',
                'billing_project_id': '890023',
                'category_id': 'H03107',
                'default_comment': 'Professional Training - '
            },
            {
                'name': 'Projektarbeit',
                'billing_project_id': '890023',
                'category_id': 'H03108',
                'default_comment': 'Internal Project Work - '
            },
            {
                'name': 'Interne Meetings',
                'billing_project_id': '890023',
                'category_id': 'H03104',
                'default_comment': 'Internal Meeting - '
            },
            {
                'name': '1:1 Gespräche',
                'billing_project_id': '890023',
                'category_id': 'H03108',
                'default_comment': 'One-to-One Session - '
            },
            {
                'name': 'Interne Operationen',
                'billing_project_id': '890023',
                'category_id': 'H03105',
                'default_comment': 'Internal Operations - '
            }
        ]

        for activity_data in internal_activities:
            activity = Activity(
                name=activity_data['name'],
                type_id=type_objects['internal'].id,
                billing_project_id=activity_data['billing_project_id'],
                category_id=activity_data['category_id'],
                default_comment=activity_data['default_comment'],
                is_chargeable=False
            )
            db.session.add(activity)

        print("Speichere Änderungen in der Datenbank...")
        db.session.commit()
        print("Datenbank wurde erfolgreich initialisiert!")

if __name__ == '__main__':
    init_db() 