{
    'name': 'Encode Project Budget',
    'version': '18.1.0',
    'author': 'Encode Company',
    'summary': 'Project Budget module ',
    "description": "Project Budget module.",
    'contributors': [
        'Mustafa Elian <mustafa3lian1@gmail.com>',
    ],
    'category': "Project Budget",
    "depends": [
        "project",
        "account_budget"],
    "data": [
        # "security/ir.model.access.csv",

        "views/project_views.xml",
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
}
