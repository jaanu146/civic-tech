"""
Department initialization with AI-powered colors and icons
"""

from models.models import db, Department

DEPARTMENTS = [
    {
        'name': 'Roads & Infrastructure',
        'color': '#3b82f6',
        'icon': '🛣️',
        'complaint_type': 'road'
    },
    {
        'name': 'Water Supply',
        'color': '#06b6d4',
        'icon': '💧',
        'complaint_type': 'water'
    },
    {
        'name': 'Sanitation & Waste',
        'color': '#8b5cf6',
        'icon': '🗑️',
        'complaint_type': 'garbage'
    },
    {
        'name': 'Public Lighting',
        'color': '#eab308',
        'icon': '💡',
        'complaint_type': 'light'
    },
    {
        'name': 'Health & Sanitation',
        'color': '#ec4899',
        'icon': '🏥',
        'complaint_type': 'health'
    },
    {
        'name': 'Public Safety',
        'color': '#ef4444',
        'icon': '🚨',
        'complaint_type': 'safety'
    },
]

def init_departments():
    """Initialize departments with colors and icons"""
    for dept_data in DEPARTMENTS:
        existing = Department.query.filter_by(name=dept_data['name']).first()
        if not existing:
            dept = Department(
                name=dept_data['name'],
                color=dept_data['color'],
                icon=dept_data['icon']
            )
            db.session.add(dept)
    
    try:
        db.session.commit()
        print("✓ Departments initialized with AI colors and icons")
    except Exception as e:
        db.session.rollback()
        print(f"Department initialization error: {e}")
