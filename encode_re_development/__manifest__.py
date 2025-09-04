# -*- coding: utf-8 -*-
{
    'name': "Encode RE Development",
    'version': '18.1.0',
    'author': "Encode Company",
    'website': "https://encode.odoo.com/",
    'summary': """
    Manage Real Estate operations 
    """,
    'description': """
    this module is for RE Development 
    """,
    'contributors': [
        'Mustafa Elian <mustafa3lian1@gmail.com>',
    ],
    'category': "RE Development",
    'depends': [
        'base',
        'project',
        'product',
        'hr_expense',
        'hr_timesheet',
        'account',
    ],
    'data': [
        # 'security/ir.model.access.csv',

        'data/ir_cron.xml',

        'views/project_views.xml',
        # 'views/project_task_views.xml',
        'views/product_template_views.xml',

        'report/re_developer_template.xml',
        'report/re_developer_report.xml',
        'report/re_investor_template.xml',
        'report/re_investor_report.xml',
    ],
    'license': 'OEEL-1',
    'installable': True,
    'application': False,
}
