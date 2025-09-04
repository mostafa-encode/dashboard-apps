from odoo import models, fields, api, _
from random import randint


class WorkType(models.Model):
    _name = 'work.type'
    _description = 'Work Type'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    sub_type_ids = fields.One2many('work.sub.type', 'work_type_id', string='Work Subtypes')

    work_sub_type_ids = fields.One2many(
        'work.sub.type', 'work_type_id', string='Work Sub Types'
    )

    work_sub_type_count = fields.Integer(
        string='Subtypes Count',
        compute='_compute_work_sub_type_count'
    )

    @api.depends('work_sub_type_ids')
    def _compute_work_sub_type_count(self):
        for rec in self:
            rec.work_sub_type_count = len(rec.work_sub_type_ids)

    def action_open_work_sub_types(self):
        return {
            'name': 'Work Sub Types',
            'type': 'ir.actions.act_window',
            'res_model': 'work.sub.type',
            'view_mode': 'list,form',
            'domain': [('work_type_id', '=', self.id)],
            'context': {'default_work_type_id': self.id},
        }


class WorkSubType(models.Model):
    _name = 'work.sub.type'
    _description = 'Work Sub Type'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    color = fields.Integer(string='Color', default=_get_default_color, aggregator=False)
    description = fields.Text(string='Description')
    work_type_id = fields.Many2one('work.type', string='Work Type')
