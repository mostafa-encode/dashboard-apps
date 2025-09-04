{
    'name': 'Encode Material Requisition',
    'version': '18.1.0',
    'author': 'Encode Company',
    'summary': 'Structured material requisition system with project linkage, vendor filtering, auto-filled product info, and per-line cost computation',
    "description": """    
    This module adds a structured material requisition system designed for project-based or subcontractor workflows. Key features include:
    
    - Create and manage material requisition requests linked to projects or work types.
    - Add multiple product lines with quantities, descriptions, and cost tracking.
    - Automatically fetch product purchase description and unit of measure.
    - Vendor selection is limited to the suppliers defined on the product, with the first vendor auto-selected.
    - Computes total cost per line item based on unit price and quantity.
    
    """,
    'contributors': [
        'Ameer Essam <ameer.essama@gmail.com>',
    ],
    'category': "Material Requisition",
    'depends': ['base', 'project', 'purchase', 'uom', 'project_purchase'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/requisition_sequence_data.xml',
        'data/mail_template_data.xml',
        'views/material_requisition_views.xml',
        'views/project_integration_view.xml',
        'views/work_type_views.xml',
        'views/work_sub_type_views.xml',
        'views/menus.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
}
