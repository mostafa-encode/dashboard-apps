{
    'name': 'Encode Project Dashboard',
    'version': '1.0.0',
    'summary': 'Dashboard with KPIs for projects (Completion, SPI, Cost Spent %).',
    'category': 'Project',
    'author': 'Encode',
    'depends': ['project', 'hr_timesheet', 'analytic', 'encode_project_budget', 'encode_project_template'],
    'data': [
        'views/project_dashboard_actions.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'encode_project_dashboard/static/src/css/project_dashboard.css',
            'encode_project_dashboard/static/src/js/project_dashboard.js',
            'encode_project_dashboard/static/src/xml/project_dashboard.xml',
        ],
    },
    'license': 'LGPL-3',
    'application': False,
}

