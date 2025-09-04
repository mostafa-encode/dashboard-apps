from odoo import fields, models, api
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_unit = fields.Boolean(string="Unit", help="Mark as real estate unit")

    # 🔷 Automatic Cost Calculation Fields
    cost_calculation_date_from = fields.Date(
        string="Cost Calculation From",
        readonly=True,
        help="Start date for cost calculation period"
    )
    cost_calculation_date_to = fields.Date(
        string="Cost Calculation To", 
        readonly=True,
        help="End date for cost calculation period"
    )
    cost_calculation_note = fields.Text(
        string="Cost Calculation Note",
        readonly=True,
        help="Note about the cost calculation period"
    )
    vendor_bill_count = fields.Integer(
        string="Vendor Bill Count",
        readonly=True,
        help="Number of vendor bills used in cost calculation"
    )

    # 🔷 Identification & Structure
    project_name_id = fields.Many2one('project.project', string="Project")
    floor_number = fields.Integer(string="Floor Number")
    unit_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('duplex', 'Duplex'),
        ('floor', 'Floor'),
    ], string="Unit Type")
    unit_category = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('both', 'Residential and Commercial'),
    ], string="Unit Category")
    unit_status = fields.Selection([
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('sold', 'Sold'),
    ], string="Unit Status", default='available')

    # 🔷 Area & Rooms
    plot_area = fields.Float(string="Land Area (m²)")
    built_up_area = fields.Float(string="Built-up Area (m²)")
    bedrooms = fields.Integer(string="Bedrooms")
    bathrooms = fields.Integer(string="Bathrooms")
    maid_room = fields.Boolean(string="Maid Room")
    balcony = fields.Boolean(string="Balcony")
    balcony_area = fields.Float(string="Balcony Area (m²)")
    parking = fields.Boolean(string="Parking Available?")
    parking_numbers = fields.Integer(string="Parking Numbers")

    # 🔷 Location & View
    city = fields.Char(string="City")
    district = fields.Char(string="District")
    zone = fields.Char(string="Zone")
    street_name = fields.Char(string="Street Name")
    orientation = fields.Selection([
        ('east', 'Eastern'),
        ('west', 'Western'),
        ('south', 'Southern'),
        ('north', 'Northern'),
    ], string="Orientation")

    # 🔷 Financial Info
    price_per_m2 = fields.Float(string="Price per m²")

    # 🔷 Legal & Delivery
    title_deed_number = fields.Char(string="Title Deed Number")
    title_deed_type = fields.Selection([
        ('freehold', 'Freehold'),
        ('leasehold', 'Leasehold'),
    ], string="Title Deed Type")
    municipal_license_no = fields.Char(string="Municipal License No.")
    construction_permit_no = fields.Char(string="Construction Permit No.")
    warranty_period = fields.Integer(string="Warranty Period")

    # 🔷 Media & Attachments
    blueprints = fields.Many2many('ir.attachment', 'product_blueprint_rel', 'product_id', 'attachment_id', string="Blueprints")
    unit_photos = fields.Many2many('ir.attachment', 'product_photos_rel', 'product_id', 'attachment_id', string="Unit Photos")
    video_tour_url = fields.Char(string="Video Tour URL")

    def _compute_calculated_cost(self):
        """Compute the average cost from vendor bills for the last year and update standard_price"""
        for product in self:
            # Get the product variants
            variants = product.product_variant_ids
            
            if not variants:
                product.standard_price = 0.0
                product.cost_calculation_date_from = False
                product.cost_calculation_date_to = False
                product.cost_calculation_note = "No product variants found"
                product.vendor_bill_count = 0
                continue
            
            # Calculate date range (last year from today)
            today = date.today()
            date_from = today - relativedelta(years=1)
            # Temporary debug to check dates
            print(f"DEBUG: Today={today}, Date range: {date_from} to {today}")
            
            # Get all vendor bill lines for this product within the date range
            # Search for both product template and variants, and handle date ranges more flexibly
            product_ids = [product.id] + variants.ids
            
            # First, let's get all vendor bills for this product (without date filter)
            all_vendor_bills = self.env['account.move.line'].search([
                '|',
                ('product_id', 'in', product_ids),
                ('product_id.product_tmpl_id', '=', product.id),
                ('move_id.move_type', '=', 'in_invoice'),
                ('move_id.state', '=', 'posted'),
                ('price_unit', '>', 0),
            ])
            
            # Now filter by date range - handle cases where invoice_date might be empty
            vendor_bill_lines = []
            
            for bill_line in all_vendor_bills:
                invoice_date = bill_line.move_id.invoice_date
                if invoice_date:
                    print(f"DEBUG: Checking bill {bill_line.move_id.name} with invoice_date={invoice_date}")
                    # Only include bills from the past, not future
                    if date_from <= invoice_date <= today:
                        vendor_bill_lines.append(bill_line)
                        print(f"DEBUG: Added bill (in range)")
                    else:
                        print(f"DEBUG: Skipped bill (outside range or future)")
                else:
                    # If no invoice_date, check if the move was created within the last year
                    create_date = bill_line.move_id.create_date
                    if create_date:
                        create_date = create_date.date()
                        print(f"DEBUG: Checking bill {bill_line.move_id.name} with create_date={create_date}")
                        if date_from <= create_date <= today:
                            vendor_bill_lines.append(bill_line)
                            print(f"DEBUG: Added bill (create date in range)")
                        else:
                            print(f"DEBUG: Skipped bill (create date outside range or future)")
                    else:
                        print(f"DEBUG: Skipped bill {bill_line.move_id.name} (no date)")
            
            if not vendor_bill_lines:
                # If no bills in date range, check if there are any bills at all
                if all_vendor_bills:
                    # Get some sample dates to show what's available
                    sample_dates = []
                    for bill in all_vendor_bills[:3]:
                        date_info = f"Bill {bill.move_id.name}: "
                        if bill.move_id.invoice_date:
                            date_info += f"invoice_date={bill.move_id.invoice_date}"
                        else:
                            date_info += f"create_date={bill.move_id.create_date.date() if bill.move_id.create_date else 'None'}"
                        sample_dates.append(date_info)
                    
                    product.standard_price = 0.0
                    product.cost_calculation_date_from = date_from
                    product.cost_calculation_date_to = today
                    product.cost_calculation_note = f"⚠️ No vendor bills in date range ({date_from.strftime('%d/%m/%Y')} to {today.strftime('%d/%m/%Y')}). Found {len(all_vendor_bills)} bills outside range. Sample: {', '.join(sample_dates)}"
                    product.vendor_bill_count = 0
                else:
                    product.standard_price = 0.0
                    product.cost_calculation_date_from = date_from
                    product.cost_calculation_date_to = today
                    product.cost_calculation_note = f"⚠️ No vendor bills found for this product from {date_from.strftime('%d/%m/%Y')} to {today.strftime('%d/%m/%Y')}"
                    product.vendor_bill_count = 0
                continue
            
            # Calculate average cost
            total_price = sum(line.price_unit for line in vendor_bill_lines)
            bill_count = len(vendor_bill_lines)
            average_cost = total_price / bill_count if bill_count > 0 else 0.0
            
            # Set the values directly
            product.standard_price = average_cost
            product.cost_calculation_date_from = date_from
            product.cost_calculation_date_to = today
            product.vendor_bill_count = bill_count
            
            # Generate note with visual styling
            if bill_count == 1:
                note = f"💡 Auto-calculated cost from 1 vendor bill ({date_from.strftime('%d/%m/%Y')} to {today.strftime('%d/%m/%Y')})"
            else:
                note = f"💡 Auto-calculated cost from {bill_count} vendor bills ({date_from.strftime('%d/%m/%Y')} to {today.strftime('%d/%m/%Y')})"
            
            product.cost_calculation_note = note

    @api.model
    def _update_all_product_costs(self):
        """Update costs for all products - called by cron job"""
        all_products = self.search([])
        # Use context to prevent recursion
        all_products.with_context(skip_cost_recalculation=True)._compute_calculated_cost()
        return len(all_products)

    @api.model
    def create(self, vals):
        """Override to calculate cost when product is created"""
        product = super().create(vals)
        # Calculate cost for the new product
        if not self.env.context.get('skip_cost_recalculation'):
            product._compute_calculated_cost()
        return product

    def write(self, vals):
        """Override to recalculate cost when product is modified"""
        result = super().write(vals)
        # Recalculate cost for modified products (only if not already calculating)
        if not self.env.context.get('skip_cost_recalculation'):
            self.with_context(skip_cost_recalculation=True)._compute_calculated_cost()
        return result

    def action_recalculate_cost(self):
        """Manual action to force cost recalculation"""
        self.with_context(skip_cost_recalculation=True)._compute_calculated_cost()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Cost Recalculated',
                'message': f'Cost has been recalculated for {len(self)} product(s)',
                'type': 'success',
                'sticky': False,
            }
        }


