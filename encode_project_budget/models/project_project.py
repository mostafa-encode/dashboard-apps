from odoo import models, fields, _
from odoo.exceptions import UserError
import re

class ProjectProject(models.Model):
    _inherit = "project.project"

    # Computed helper to hide the button if a budget already exists
    budget_exists = fields.Boolean(
        string='Has Budget',
        compute='_compute_budget_exists',
        store=False
    )

    budget_count = fields.Integer(
        string="Budgets",
        compute="_compute_budget_stats",
        store=False
    )

    def _compute_budget_exists(self):
        BudgetLine = self.env['budget.line'].sudo()
        for project in self:
            if project.account_id:
                project.budget_exists = bool(
                    BudgetLine.search_count([
                        '|',
                        ('account_id', '=', project.account_id.id),
                        ('project_id', '=', project.id),
                    ])
                )
            else:
                project.budget_exists = False

    def _compute_budget_stats(self):
        Budget = self.env['budget.analytic'].sudo()
        for project in self:
            domain = ['|', ('project_id', '=', project.id), ('budget_line_ids.project_id', '=', project.id)]
            cnt = Budget.search_count(domain)
            project.budget_count = cnt
            project.budget_exists = bool(cnt)


    def action_open_budgets(self):
        """Open all budgets related to this project (tree/form)."""
        self.ensure_one()
        domain = ['|', ('project_id', '=', self.id), ('budget_line_ids.project_id', '=', self.id)]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Budgets'),
            'res_model': 'budget.analytic',
            'view_mode': 'list,form',
            'domain': domain,
            'target': 'current',
            # helpful defaults if the user creates a new budget from this view
            'context': {
                'default_project_id': self.id if 'project_id' in self.env['budget.analytic']._fields else False,
                'default_name': _("ميزانية %s") % self.name,
                'default_budget_type': 'expense',
                'default_date_from': self.date_start,  # all are Date (per you)
                'default_date_to': self.date,
            },
        }

    def action_create_budget(self):
        self.ensure_one()

        if hasattr(self, 'budget_exists') and self.budget_exists:
            raise UserError(_("A budget already exists for this project"))

        Budget = self.env['budget.analytic'].sudo()
        BudgetLine = self.env['budget.line'].sudo()

        # All fields are Date, so use them directly
        date_from = self.date_start
        date_to = self.date

        # Optional sanity check
        if date_from and date_to and date_to < date_from:
            raise UserError(_("Project end date cannot be before start date."))

        is_ar = bool(re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', self.name or ''))
        label = (_("ميزانية %s") % self.name) if is_ar else (_("Budget %s") % self.name)

        budget_vals = {
            'state': 'draft',
            'name': label,
            'budget_type': 'expense',
            'date_from': date_from,  # project.date_start
            'date_to': date_to,  # project.date
        }
        if 'project_id' in Budget._fields:
            budget_vals['project_id'] = self.id

        budget = Budget.create(budget_vals)



        # Create a related budget.line
        line_vals = {
            'budget_analytic_id': budget.id,
            'account_id': self.account_id.id if self.account_id else False,
            'project_id': self.id,
        }
        BudgetLine.create(line_vals)

        # Redirect to the new Budget form
        return {
            'type': 'ir.actions.act_window',
            'name': _('Budget'),
            'res_model': 'budget.analytic',
            'view_mode': 'form',
            'res_id': budget.id,
            'target': 'current',
        }
