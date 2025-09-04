from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def write(self, vals):
        """Override to recalculate product costs when vendor bills are modified"""
        result = super().write(vals)
        
        # Recalculate if any relevant field changed for vendor bills
        if self.move_type == 'in_invoice' and (
            'state' in vals or 
            'invoice_line_ids' in vals or
            'invoice_date' in vals
        ):
            self._recalculate_product_costs()
        
        return result

    def unlink(self):
        """Override to recalculate product costs when vendor bills are deleted"""
        # Store products before deletion for recalculation
        products_to_recalculate = set()
        for move in self:
            if move.move_type == 'in_invoice' and move.state == 'posted':
                products = move.invoice_line_ids.mapped('product_id.product_tmpl_id')
                products_to_recalculate.update(products.ids)
        
        result = super().unlink()
        
        # Recalculate costs for affected products
        if products_to_recalculate:
            products = self.env['product.template'].browse(list(products_to_recalculate))
            products._compute_calculated_cost()
        
        return result

    def _recalculate_product_costs(self):
        """Recalculate costs for products in this vendor bill"""
        for move in self:
            # Get all products from the bill lines
            products = move.invoice_line_ids.mapped('product_id.product_tmpl_id')
            
            if products:
                # Recalculate costs for these products (use context to prevent recursion)
                products.with_context(skip_cost_recalculation=True)._compute_calculated_cost()
