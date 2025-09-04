from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MaterialRequisition(models.Model):
    _name = 'material.requisition'
    _description = 'Material Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='MR#', required=True, copy=False, readonly=True, default=lambda self: _('New'),
                       tracking=True)
    description = fields.Char(tracking=True)
    project_id = fields.Many2one('project.project', required=True, tracking=True)
    sub_project_id = fields.Many2one('project.project', tracking=True)
    date = fields.Datetime(default=fields.Datetime.now, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('material_arrived', 'Material Arrived'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True)
    material_arrived_date = fields.Datetime(string="Material Arrival Date", tracking=True)
    line_ids = fields.One2many('material.requisition.line', 'requisition_id', string="Lines", tracking=True)
    purchase_order_ids = fields.One2many('purchase.order', 'requisition_id', string='RFQs', tracking=True)
    purchase_order_count = fields.Integer(compute='_compute_purchase_order_count', string='# of RFQs', tracking=True)
    rfq_created = fields.Boolean(compute='_compute_purchase_order_count', store=True, string="RFQ Created",
                                 tracking=True)
    work_type_id = fields.Many2one('work.type', string='Work Type')

    color = fields.Integer(string="Color", compute="_compute_color", store=True)

    @api.depends('state')
    def _compute_color(self):
        for rec in self:
            if rec.state == 'draft':
                rec.color = 0  # gray
            elif rec.state == 'waiting':
                rec.color = 3  # yellow
            elif rec.state == 'approved':
                rec.color = 2  # green
            elif rec.state == 'cancelled':
                rec.color = 1  # red
            else:
                rec.color = 0  # default


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('material.requisition') or _('New')
        requisition = super().create(vals)
        
        # Send notification email for new requisitions
        requisition._send_notification_email()
        
        return requisition

    def action_submit(self):
        self.write({'state': 'waiting'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset(self):
        self.write({'state': 'draft'})

    def action_create_rfq(self):
        PurchaseOrder = self.env['purchase.order']

        # Group lines by vendor
        vendor_lines_map = {}
        for line in self.line_ids:
            if not line.vendor_id:
                continue
            vendor_lines_map.setdefault(line.vendor_id.id, []).append(line)

        rfqs = []
        for vendor_id, lines in vendor_lines_map.items():
            po_vals = {
                'partner_id': vendor_id,
                'origin': self.name,
                'requisition_id': self.id,
                'project_id': self.project_id.id if self.project_id else False,
                'order_line': [],
            }

            for line in lines:
                po_line_vals = {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'price_unit': line.cost,
                    'date_planned': fields.Datetime.now(),
                }
                po_vals['order_line'].append((0, 0, po_line_vals))

            rfq = PurchaseOrder.create(po_vals)
            rfqs.append(rfq)

        if not rfqs:
            raise UserError(_("No valid lines with vendor found to create RFQ."))

        if len(rfqs) == 1:
            self.write({'state': 'in_progress'})
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'view_mode': 'form',
                'res_id': rfqs[0].id,
                'target': 'current',
            }
        else:
            action = self.env['ir.actions.actions']._for_xml_id('purchase.purchase_rfq')
            action['domain'] = [('id', 'in', [r.id for r in rfqs])]
            return action

    def action_material_arrived(self):
        if not self.env.user.has_group('encode_material_requisition.group_mark_material_arrived'):
            raise UserError("You are not authorized to mark materials as arrived.")

        # Check that at least one line has a received quantity > 0
        has_received = any(line.received_qty > 0 for line in self.line_ids)
        if not has_received:
            raise UserError(_("At least one line must have Received Qty > 0 before marking as received."))

        self.write({
            'state': 'material_arrived',
            'material_arrived_date': fields.Datetime.now(),
        })

    @api.depends('purchase_order_ids')
    def _compute_purchase_order_count(self):
        for requisition in self:
            requisition.purchase_order_count = len(requisition.purchase_order_ids)
            requisition.rfq_created = bool(requisition.purchase_order_ids)

    def open_purchase_orders(self):
        """
        a button to open the purchase orders related to the requisition
        """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders',
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.purchase_order_ids.ids)],
            'context': dict(self._context),
            'target': 'current',
        }

    def _send_notification_email(self):
        """Send notification email to project manager when requisition is created"""
        self.ensure_one()
        
        # Check if requisition is in draft or waiting state
        if self.state not in ['draft', 'waiting']:
            return
        
        # Check if project has a manager assigned
        if not self.project_id.user_id:
            self.message_post(
                body=_("⚠️ Notification email not sent: No project manager assigned to this project."),
                message_type='notification'
            )
            return
        
        # Check if project manager has an email
        if not self.project_id.user_id.email:
            self.message_post(
                body=_("⚠️ Notification email not sent: Project manager does not have an email address."),
                message_type='notification'
            )
            return
        
        try:
            # Get the email template
            template = self.env.ref('encode_material_requisition.email_template_material_requisition_notification_v2')
            if not template:
                self.message_post(
                    body=_("⚠️ Notification email not sent: Email template not found."),
                    message_type='notification'
                )
                return
            
            
            # Send the email asynchronously with proper context
            result = template.with_context(lang=self.project_id.user_id.lang or 'en_US').send_mail(
                self.id, 
                force_send=True
            )
            
            
            # Log success in chatter
            self.message_post(
                body=_("📧 Notification email sent to project manager: %s") % self.project_id.user_id.name,
                message_type='notification'
            )
            
        except Exception as e:
            # Log error in chatter
            self.message_post(
                body=_("❌ Failed to send notification email: %s") % str(e),
                message_type='notification'
            )


class MaterialRequisitionLine(models.Model):
    _name = 'material.requisition.line'
    _description = 'Material Requisition Line'

    requisition_id = fields.Many2one('material.requisition', required=True, ondelete='cascade')
    work_sub_type_id = fields.Many2one(
        'work.sub.type',
        string='Work Sub Type',
        domain="[('id', 'in', allowed_work_sub_type_ids)]"
    )
    allowed_work_sub_type_ids = fields.Many2many(
        'work.sub.type',
        compute='_compute_allowed_work_subtypes',
        store=False,
        string="Allowed Work Subtypes"
    )
    product_id = fields.Many2one('product.product', required=True)
    description = fields.Text(string='Description', related='product_id.description_purchase', readonly=True)
    product_uom_qty = fields.Integer(string='Quantity')
    received_qty = fields.Integer(string="Received Qty", default=0, help="Quantity of materials actually received")
    receiving_notes = fields.Text(string="Receiving Notes", help="Notes about the received delivery")
    product_uom = fields.Many2one('uom.uom', string='UoM', related='product_id.uom_po_id', readonly=True)
    cost = fields.Monetary(string='Unit Cost', currency_field='currency_id')
    total_price = fields.Monetary(string='Total Price', compute='_compute_total_price', currency_field='currency_id')
    delivery_id = fields.Many2one('stock.warehouse')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    vendor_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        domain="[('id', 'in', allowed_vendor_ids)]"
    )
    allowed_vendor_ids = fields.Many2many(
        'res.partner',
        compute='_compute_allowed_vendors',
        string="Allowed Vendors",
        compute_sudo=True,
        store=False
    )

    @api.constrains('received_qty', 'product_uom_qty')
    def _check_received_qty(self):
        for line in self:
            if line.received_qty > line.product_uom_qty:
                raise ValidationError(_("Received quantity cannot exceed the requested quantity."))

    @api.depends('product_id')
    def _compute_allowed_vendors(self):
        Partner = self.env['res.partner']
        for line in self:
            if line.product_id:
                vendors = line.product_id.seller_ids.mapped('partner_id')
                line.allowed_vendor_ids = vendors if vendors else Partner.search([])
            else:
                line.allowed_vendor_ids = Partner.search([])

    @api.onchange('product_id')
    def _onchange_product_id_set_default_vendor(self):
        for line in self:
            vendors = line.product_id.seller_ids.mapped('partner_id')
            line.vendor_id = vendors[0] if vendors else False

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.cost = line.product_id.standard_price

    @api.depends('product_uom_qty', 'cost')
    def _compute_total_price(self):
        for line in self:
            line.total_price = line.product_uom_qty * line.cost

    @api.depends('requisition_id.work_type_id')
    def _compute_allowed_work_subtypes(self):
        for line in self:
            if line.requisition_id and line.requisition_id.work_type_id:
                line.allowed_work_sub_type_ids = self.env['work.sub.type'].search([
                    ('work_type_id', '=', line.requisition_id.work_type_id.id)
                ])
            else:
                line.allowed_work_sub_type_ids = self.env['work.sub.type'].browse()

