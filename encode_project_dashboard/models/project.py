from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class Project(models.Model):
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
            
            # Debug: Print all available fields in budget.line model
            if budget_lines:
                sample_line = budget_lines[0]
                _logger.info(f"=== BUDGET.LINE MODEL FIELDS ===")
                _logger.info(f"All fields: {list(sample_line._fields.keys())}")
                _logger.info(f"Sample line: {sample_line}")
                _logger.info(f"Sample line ID: {sample_line.id}")
                _logger.info(f"=== END BUDGET.LINE MODEL FIELDS ===")
            
            _logger.info(f"Budget lines found for project {self.name}: {len(budget_lines)}")
            for line in budget_lines:
                _logger.info(f"Budget line: {line.name if hasattr(line, 'name') else 'No name'}, "
                           f"achieved: {getattr(line, 'achieved', 'N/A')}, "
                           f"budgeted: {getattr(line, 'budgeted', 'N/A')}, "
                           f"budget_amount: {getattr(line, 'budget_amount', 'N/A')}")
                
                # Log all available fields for debugging
                _logger.info(f"Budget line fields: {list(line._fields.keys())}")
                
                # Try to access the line directly to see what's available
                _logger.info(f"Budget line record: {line}")
                _logger.info(f"Budget line ID: {line.id}")
                
                # Try to get the actual values using different methods
                try:
                    achieved_val = line.achieved if hasattr(line, 'achieved') else 'No achieved field'
                    budgeted_val = line.budgeted if hasattr(line, 'budgeted') else 'No budgeted field'
                    budget_amount_val = line.budget_amount if hasattr(line, 'budget_amount') else 'No budget_amount field'
                    
                    _logger.info(f"Direct access - achieved: {achieved_val}, budgeted: {budgeted_val}, budget_amount: {budget_amount_val}")
                except Exception as e:
                    _logger.error(f"Error accessing budget line fields: {e}")
            
            # Also get budget analytics data
            budget_analytics = self.env['budget.analytic'].search([
                '|',
                ('project_id', '=', self.id),
                ('budget_line_ids.project_id', '=', self.id)
            ])
            
            _logger.info(f"Budget analytics found for project {self.name}: {len(budget_analytics)}")
            
            # Try different field names for budget data
            budget_data = []
            for line in budget_lines:
                # Try multiple possible field names for achieved amount
                achieved = (getattr(line, 'amount_achieved', 0) or 
                           getattr(line, 'achieved_amount', 0) or 
                           getattr(line, 'actual_amount', 0) or 
                           getattr(line, 'achieved', 0) or 
                           getattr(line, 'amount_actual', 0) or 0)
                
                budgeted = (getattr(line, 'budget_amount', 0) or 
                           getattr(line, 'budgeted', 0) or 
                           getattr(line, 'planned_amount', 0) or 
                           getattr(line, 'amount_budgeted', 0) or 0)
                
                budget_data.append({
                    'achieved_amount': achieved,
                    'budgeted': budgeted
                })
                
                _logger.info(f"Processed budget line - achieved: {achieved}, budgeted: {budgeted}")
                _logger.info(f"Tried fields - amount_achieved: {getattr(line, 'amount_achieved', 'N/A')}, "
                           f"achieved_amount: {getattr(line, 'achieved_amount', 'N/A')}, "
                           f"actual_amount: {getattr(line, 'actual_amount', 'N/A')}, "
                           f"achieved: {getattr(line, 'achieved', 'N/A')}, "
                           f"amount_actual: {getattr(line, 'amount_actual', 'N/A')}")
            
            # Convert allocated time from days to hours (assuming 8 hours per day)
            # Get working hours from company settings or default to 8
            working_hours_per_day = self.env.company.resource_calendar_id.hours_per_day if self.env.company.resource_calendar_id else 8
            allocated_hours = (self.allocated_hours or 0) * working_hours_per_day
            
            # Return raw data for JavaScript processing
            result = {
                'id': self.id,
                'name': self.name,
                'allocated_hours': allocated_hours,
                'total_tasks': total_tasks,
                'closed_tasks': closed_tasks,
                'open_tasks': open_tasks,
                'total_time_spent': total_time_spent,
                'budget_lines': budget_data
            }
            
            _logger.info(f"Final result for project {self.name}: {result}")
            
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
