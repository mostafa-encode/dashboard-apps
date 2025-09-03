from odoo import models, fields, _
from odoo.exceptions import UserError

class BudgetLine(models.Model):
    _inherit = "budget.line"

    project_id = fields.Many2one('project.project', string='Project')

