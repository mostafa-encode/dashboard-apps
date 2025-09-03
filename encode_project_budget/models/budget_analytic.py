from odoo import models, fields, _
from odoo.exceptions import UserError

class BudgetAnalytic(models.Model):
    _inherit = "budget.analytic"

    project_id = fields.Many2one('project.project', string='Project')

