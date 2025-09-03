{
    'name': 'Encode Project Dashboard',
    'version': '1.0',
    'category': 'Project',
    'summary': 'Elegant project dashboard with ring charts',
    'description': """
        A modern and elegant project dashboard that displays:
        - Completion percentage ring chart
        - Schedule Performance Index (SPI) ring chart  
        - Cost spent percentage ring chart
        
        Uses existing project fields for calculations.
    """,
    'author': 'Encode',
    'contributors': [
        'Mustafa Elian <mustafa3lian1@gmail.com>',
    ],
    'website': 'https://www.encode.com',
    'depends': [
        'project',
        'hr_timesheet',
        'web',
        'encode_project_budget',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_dashboard_views.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'encode_project_dashboard/static/src/css/project_dashboard.css',
            'encode_project_dashboard/static/src/js/project_dashboard.js',
            'encode_project_dashboard/static/src/xml/project_dashboard.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
