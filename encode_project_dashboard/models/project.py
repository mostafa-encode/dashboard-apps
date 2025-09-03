from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = 'project.project'


    def get_dashboard_data(self):
        """Get raw project data for JavaScript processing"""
        self.ensure_one()

        try:
            # Use Odoo's built-in task count fields
            total_tasks = self.task_count or 0
            closed_tasks = self.closed_task_count or 0
            open_tasks = self.open_task_count or 0

            # Get all tasks for timesheet calculation
            all_tasks = self.env['project.task'].search([('project_id', '=', self.id)])

            # Calculate total time spent from timesheets on all project tasks
            total_time_spent = 0
            for task in all_tasks:
                task_timesheets = task.timesheet_ids
                task_time = sum(task_timesheets.mapped('unit_amount'))
                total_time_spent += task_time

            # Get budget data
            budget_lines = self.env['budget.line'].search([
                '|',
                ('project_id', '=', self.id),
                ('account_id', '=', self.account_id.id) if self.account_id else (False, '=', False)
            ])

            # Also get budget analytics data
            budget_analytics = self.env['budget.analytic'].search([
                '|',
                ('project_id', '=', self.id),
                ('budget_line_ids.project_id', '=', self.id)
            ])

            # Return raw data for JavaScript processing
            result = {
                'id': self.id,
                'name': self.name,
                'allocated_hours': self.allocated_hours or 0,
                'total_tasks': total_tasks,
                'closed_tasks': closed_tasks,
                'open_tasks': open_tasks,
                'total_time_spent': total_time_spent,
                'budget_lines': [{
                    'achieved': getattr(line, 'achieved', 0),
                    'budgeted': getattr(line, 'budget_amount', getattr(line, 'budgeted', 0))
                } for line in budget_lines]
            }

            return result

        except Exception as e:
            _logger.error(f"Error getting dashboard data for project {self.name}: {str(e)}")
            return {
                'id': self.id,
                'name': self.name,
                'allocated_hours': 0,
                'total_tasks': 0,
                'closed_tasks': 0,
                'open_tasks': 0,
                'total_time_spent': 0,
                'budget_lines': []
            }

    @api.model
    def get_all_dashboard_data(self):
        """Get raw data for all active projects"""
        try:
            projects = self.search([('active', '=', True)])

            if not projects:
                return []

            dashboard_data = []
            for project in projects:
                try:
                    data = project.get_dashboard_data()
                    dashboard_data.append(data)
                except Exception as e:
                    _logger.error(f"Error processing project {project.name}: {str(e)}")
                    continue

            return dashboard_data

        except Exception as e:
            _logger.error(f"Error in get_all_dashboard_data: {str(e)}")
            return []

