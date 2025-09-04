from odoo import models, fields, api


class Project(models.Model):
    _inherit = 'project.project'

    material_requisition_count = fields.Integer(
        compute='_compute_material_requisition_count',
        string='Material Requisition Count'
    )
    subcontractor_and_supervisor_ids = fields.Many2many(
        'res.users',
        string="Subcontractors",
        domain=lambda self: self._get_portal_user_domain(),  # Only portal users (share=True)
        help="Portal users (subcontractors or supervisors) who can access and create material requisitions for this project.",
    )

    @api.model
    def _get_portal_user_domain(self):
        portal_group = self.env.ref('base.group_portal')
        admin_group = self.env.ref('base.group_system')
        return [('groups_id', 'in', [portal_group.id, admin_group.id])]

    def _compute_material_requisition_count(self):
        for project in self:
            project.material_requisition_count = self.env['material.requisition'].search_count([
                ('project_id', '=', project.id)
            ])

    def open_material_requisitions(self):
        """
        open related material requisitions
        """
        self.ensure_one()
        material_requisitions = self.env['material.requisition'].search([
            ('project_id', '=', self.id)
        ])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Material Requisitions',
            'res_model': 'material.requisition',
            'view_mode': 'list,form',
            'domain': [('id', 'in', material_requisitions.ids)],
            'context': {
                'default_project_id': self.id,
                'search_default_project_id': self.id, },
            'target': 'current',
        }
