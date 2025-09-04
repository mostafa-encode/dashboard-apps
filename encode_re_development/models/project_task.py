from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta


class Task(models.Model):
    _inherit = "project.task"

    task_duration = fields.Integer(
        string="Task Duration (days)",
        compute="_compute_task_duration",
        inverse="_inverse_task_duration",
        store=True,
        help="Duration in days between start and end dates (inclusive)."
    )

    @api.depends('planned_date_begin', 'date_deadline')
    def _compute_task_duration(self):
        for task in self:
            if task.planned_date_begin and task.date_deadline:
                # inclusive days
                task.task_duration = (task.date_deadline - task.planned_date_begin).days + 1
            else:
                task.task_duration = 0

    def _inverse_task_duration(self):
        """Update end date when duration changes manually."""
        for task in self:
            if task.planned_date_begin and task.task_duration:
                task.date_deadline = task.planned_date_begin + timedelta(days=task.task_duration - 1)

    def _auto_update_state_planned_date(self):
        now = fields.Datetime.now()
        target_state = '1_done'
        cancel_state = '1_canceled'

        tasks = self.search([
            ('date_deadline', '!=', False),
            ('date_deadline', '<=', now),
            ('state', '!=', target_state),
            ('state', '!=', cancel_state),
        ])

        for task in tasks:
            task.write({
                'state': target_state,
            })

    def write(self, vals):
        """
        write method:
        - Auto mark task as done if deadline passed
        - Skip canceled tasks
        - Propagate changes to subtasks & sequential tasks only when relevant
        - Update project end date
        """
        # If this write comes from a dependent update, skip propagation logic entirely
        if self.env.context.get('skip_dependent_update') or self.env.context.get('skip_project_sequence'):
            return super(Task, self).write(vals)
        res = super(Task, self).write(vals)

        # ---------------- Propagation Control ---------------- #
        date_changed = any(k in vals for k in ['date_deadline', 'planned_date_begin'])

        if date_changed:
            for task in self:
                if task.parent_id:
                    # ✅ Case 1: Update dependent subtasks

                    # ---------- ✅ Step 1: Update dependent subtasks
                    task.with_context(skip_project_sequence=True)._update_dependent_tasks()

                    # ---------- ✅ Step 2: After parent updated → trigger project sequence for parent
                    task.parent_id.with_context(skip_dependent_update=True)._update_project_sequence_tasks()

                else:
                    # ✅ Case 2: No parent → use project sequence
                    task.with_context(skip_dependent_update=True)._update_project_sequence_tasks()
        return res

    # ---------------- Dependency Handling ---------------- #

    # ---------- Shift only direct children when parent date changes ----------#
    def _update_dependent_tasks(self):
        """Shift only direct children when parent date changes"""
        if self.env.context.get('skip_dependent_update'):
            return

        for task in self:
            children = self.env['project.task'].search([
                ('parent_id', '=', task.parent_id.id),
                ('id', '!=', task.id),
                ('state', 'not in', ['1_done', '1_canceled']),
            ], order="planned_date_begin asc")

            prev_end = task.date_deadline
            earliest_start = task.planned_date_begin
            latest_end = task.date_deadline

            for child in children:
                if not child.planned_date_begin or not prev_end:
                    continue

                # ✅ Only shift tasks that start after the current task
                if child.planned_date_begin > task.planned_date_begin:
                    new_start = prev_end + timedelta(days=1)
                    new_end = new_start + timedelta(days=child.task_duration - 1)
                    child.with_context(skip_dependent_update=True).write({
                        'planned_date_begin': new_start,
                        'date_deadline': new_end
                    })
                    prev_end = new_end
                    earliest_start = min(earliest_start, new_start) if earliest_start else new_start
                    latest_end = max(latest_end, new_end)
                else:
                    earliest_start = min(earliest_start,
                                         child.planned_date_begin) if child.planned_date_begin else earliest_start
                    latest_end = max(latest_end, child.date_deadline) if child.date_deadline else latest_end

            # ✅ Update parent end date if exists
            if task.parent_id and latest_end:
                task.parent_id.with_context(skip_dependent_update=True).write({
                    'planned_date_begin': earliest_start,
                    'date_deadline': latest_end})

    # ---------- Shift tasks sequentially by project order, skipping tasks with a parent ----------#
    def _update_project_sequence_tasks(self):
        """
            Shift only tasks that start after the current task
            (project-level, excluding subtasks with parent_id).
            Re-align them sequentially without gaps and update project end date.
        """
        if self.env.context.get('skip_project_sequence'):
            return

        for task in self:
            project = task.project_id
            if not project:
                continue

            # ✅ Get all project tasks (no parent), sorted by start
            tasks = self.env['project.task'].search([
                ('project_id', '=', project.id),
                ('parent_id', '=', False), # ✅ skip tasks with parent
                ('state', 'not in', ['1_done', '1_canceled']),
            ], order="planned_date_begin asc")

            # ✅ Detect if current task is the first in sequence
            first_task = tasks[:1]
            is_first = (first_task and first_task.id == task.id)

            prev_end = task.date_deadline
            latest_end = task.date_deadline

            for t in tasks:
                if t.id == task.id or not t.planned_date_begin:
                    continue

                # ✅ If first task was edited → shift all following tasks
                if is_first or t.planned_date_begin > task.planned_date_begin:
                    new_start = prev_end + timedelta(days=1)
                    new_end = new_start + timedelta(days=t.task_duration - 1)  # ✅ keep duration

                    t.with_context(skip_project_sequence=True).write({
                        'planned_date_begin': new_start,
                        'date_deadline': new_end
                    })

                    prev_end = new_end
                    latest_end = max(latest_end, new_end)
                else:
                    # prev_end = t.date_deadline
                    latest_end = max(latest_end, t.date_deadline)

            # ✅ Update project end date once per project
            project._update_project_end_date()
