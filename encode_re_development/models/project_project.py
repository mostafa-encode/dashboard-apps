from odoo import api, fields, models, _
from odoo.exceptions import UserError
import urllib.parse


def get_google_maps_url(latitude, longitude):
    return "https://maps.google.com?q=%s,%s" % (latitude, longitude)


class Project(models.Model):
    _inherit = "project.project"

    template_id = fields.Many2one(comodel_name='project.project')
    street = fields.Char(string='Street')
    city = fields.Char(string='City')
    state = fields.Many2one(comodel_name='res.country.state')
    zip = fields.Char(string='ZIP')
    country = fields.Many2one('res.country')
    latitude = fields.Float(digits=(10, 7), copy=False)
    longitude = fields.Float(digits=(10, 7), copy=False)
    show_map_button = fields.Boolean(
        compute='_compute_show_map_button',
        string="Show Map Button"
    )
    stakeholder_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Stakeholders'
    )




    # ############################### Inputs Tab ####################
    # Land Data group (Inputs Tab)
    district = fields.Char(string='District')
    type = fields.Selection([('floors', 'Floors')], string='Type', default='floors')
    depth = fields.Float(string='Depth')
    width = fields.Float(string='Width')
    area = fields.Float(string='The Area', compute='_compute_area', help='Computed as: Depth × Width')
    upper_factor = fields.Float(string='Upper Factor')
    total_upper_surfaces = fields.Float(string='Total Upper Surfaces', compute='_compute_totals',
                                        help='Computed as: Upper Factor × The Area')
    lower_factor = fields.Float(string='Lower Factor', compute='_compute_totals',
                                help='Computed as: (3 × (Width - 4)) / The Area')
    total_lower_surfaces = fields.Float(string='Total Lower Surfaces', compute='_compute_totals',
                                        help='Computed as: Lower Factor × The Area')
    surfaces_total = fields.Float(string='Surfaces Total', compute='_compute_totals',
                                  help='Computed as: Total Upper Surfaces + Total Lower Surfaces')
    surfaces_factor = fields.Float(string='Surfaces Factor', compute='_compute_totals',
                                   help='Computed as: Surfaces Total ÷ The Area')
    total_sales_area = fields.Float(string='Total Sales Area', compute='_compute_totals',
                                    help='Computed as: Total Upper Surfaces × 0.85')
    sales_area_factor = fields.Float(string='Sales Area Factor', compute='_compute_totals',
                                     help='Computed as: Total Sales Area ÷ The Area')
    meter_price = fields.Float(string='Meter Price')
    meter_price_for_shareholders = fields.Float(string='Meter Price for shareholders')
    villas_number = fields.Float(string='Villas Number')
    apartments_number = fields.Float(string='Apartments Number', compute='_compute_apartments_number',
                                     help='Computed as: Villas Number * 3')
    average_areas = fields.Float(string='Average Areas', compute='_compute_average_areas',
                                 help='Computed as: Total Sales Area ÷ Apartments Number')
    basement = fields.Selection([('available', 'Available'), ('unavailable', 'Unavailable'), ], string='Basement',
                                default='available')
    ac_type = fields.Selection([('split', 'Split'), ('hide', 'Hide')], string='AC Type', default='split')
    url_location = fields.Char(string='URL Location')

    # ########## Company Statements group (Inputs Tab)
    dev_supervision_for_input = fields.Float(string="Construction Supervision for Developer")
    dev_marketing_striving_for_input = fields.Float(string="Developer Marketing Striving")
    investment_mgmt_fee_for_input = fields.Float(string="Investment Management Fee")
    company_investment_profits_for_input = fields.Float(string="Company Investment Profits")

    # ########### The Costs (Inputs Tab)
    government_engineering_costs = fields.Float(string="Government and Engineering Costs")
    villa_cost = fields.Float(string="Villa Cost")
    supervision_percent = fields.Float(string="Supervision (%)")
    cost_per_meter = fields.Float(string="Cost per Meter")

    # ########## Financial Restructuring (Inputs Tab)
    financing_rate = fields.Float(string="Financing Rate")
    investors_share = fields.Float(string="Investors Share")
    the_bank = fields.Float(string="The Bank")
    company_share = fields.Float(string="Company Share")

    # ############################### RE Developer Tab ####################
    # ########### Costs (RE Developer Tab)
    land_cost = fields.Float(string="Land Cost", compute="_compute_costs",
                             help="Computed as: Meter Price × The Area")
    land_commission = fields.Float(string="Land Commission", compute="_compute_costs",
                                   help="Computed as: Land Cost × 2.5%")
    re_transaction_tax = fields.Float(string="RE Transaction Tax", compute="_compute_costs",
                                      help="Computed as: Land Cost × 5%")
    land_cost_total = fields.Float(string="Land Cost Total", compute="_compute_costs",
                                   help="Computed as: Land Cost + Commission + RE Transaction Tax")
    construction_cost_per_meter = fields.Float(string="Construction Cost per Meter", compute="_compute_costs",
                                               help="Computed as: Cost per Meter × Surfaces Total")
    villa_construction_cost = fields.Float(string="Villa Construction Cost", compute="_compute_costs",
                                           help="Computed as: Villas Number × Villa Cost")
    estimated_construction_cost = fields.Float(string="Estimated Construction Cost", compute="_compute_costs",
                                               help="Computed as: Villa Construction Cost")
    gov_eng_costs_dev = fields.Float(string="Gov. & Eng. Costs (Dev)", compute="_compute_costs",
                                     help="Computed as: Government & Engineering Costs × Apartments Number")
    supervision_dev = fields.Float(string="Supervision (Dev)", compute="_compute_costs",
                                   help="Computed as: Supervision % × (Est. Construction + Gov/Eng Costs)")
    financing_cost = fields.Float(string="Financing Cost")
    total_cost = fields.Float(string="Total Cost", compute="_compute_costs",
                              help="Computed as: Estimated Construction + Land Cost Total + Gov/Eng Costs + Supervision + Financing")
    floor_avg_cost = fields.Float(string="Floor Average Cost", compute="_compute_costs",
                                  help="Computed as: Total Cost ÷ Apartments Number")

    # ########## Financial Restructuring (RE Developer Tab)
    capital = fields.Float(string="Capital", compute="_compute_financial_restructuring",
                           help="Computed as: Land Cost Total + Financing Cost")
    financing = fields.Float(string="Financing", compute="_compute_financial_restructuring",
                             help="Computed as: Estimated Construction + Gov/Eng Costs + Supervision")
    total_company_amounts = fields.Float(string="Total Company Amounts", compute="_compute_financial_restructuring",
                                         help="Computed as: Company Share × Capital")
    total_investor_amounts = fields.Float(string="Total Investor Amounts", compute="_compute_financial_restructuring",
                                          help="Computed as: Investors Share × Capital")

    # ########## Sales Data (RE Developer Tab)
    avg_floor_price_incl_commission = fields.Float(string="Avg. Floor Price (Incl. Commission)")
    avg_floor_price_excl_commission = fields.Float(string="Avg. Floor Price (Excl. Commission)",
                                                   compute="_compute_sales_data",
                                                   help="Computed as: Avg. Floor Price Incl. Commission ÷ 1.025")
    sales_total = fields.Float(string="Sales Total")
    profits_total = fields.Float(string="Profits Total", compute="_compute_sales_data",
                                 help="Computed as: Sales Total − Total Cost")
    project_profit_margin = fields.Float(string="Project Profit Margin (%)", compute="_compute_sales_data",
                                         help="Computed as: (Sales Total ÷ Total Cost) − 1")
    capital_gains_rate = fields.Float(string="Capital Gains Rate (%)", compute="_compute_sales_data",
                                      help="Computed as: Profits Total ÷ Capital")
    investor_profit_percent = fields.Float(string="Investor Profit Percentage (%)", compute="_compute_sales_data",
                                           help="Computed as: Capital Gains Rate × 85%")
    investor_profits = fields.Float(string="Investor Profits", compute="_compute_sales_data",
                                    help="Computed as: Investor Profit Percentage × 85%")

    # ########## Company Profits Section (RE Developer Tab)
    company_investment_profits = fields.Float(string="Company Investment Profits", compute="_compute_company_profits",
                                              help="Computed as: Total Company Amounts × Investor Profit %")
    investment_mgmt_fee = fields.Float(string="Investment Management Fee 15%", compute="_compute_company_profits",
                                       help="Computed as: Profits Total × 15%")
    dev_marketing_striving = fields.Float(string="Developer Marketing Striving", compute="_compute_company_profits",
                                          help="Computed as: Sales Total × 2.5%")
    dev_supervision = fields.Float(string="Construction Supervision for Developer", compute="_compute_company_profits",
                                   help="Copied from: Supervision (Dev)")
    diff_meter_price = fields.Float(string="Different Meter Price in Land Purchase", compute="_compute_company_profits",
                                    help="Computed as: The Area × (Meter Price − Price for Shareholders)")
    total_dev_earnings = fields.Float(string="Total Developer Earnings", compute="_compute_company_profits",
                                      help="Sum of: Company Profits + Mgmt Fee + Marketing Striving + Developer Supervision + Meter Price Difference")

    # ############################### End RE Developer Tab ####################



    # ############################### Status ####################
    status = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ], string="Status", default='new', tracking=True)

    def action_set_to_new(self):
        for record in self:
            record.status = 'new'

    def action_set_in_progress(self):
        for record in self:
            record.status = 'in_progress'

    def action_set_completed(self):
        for record in self:
            record.status = 'completed'

    def action_set_on_hold(self):
        for record in self:
            record.status = 'on_hold'

    def action_set_cancelled(self):
        for record in self:
            record.status = 'cancelled'
    # ############################### End Status ####################







    # ########### computed field method #############
    # ########### The Costs
    @api.depends(
        'meter_price', 'area', 'villa_cost', 'villas_number',
        'supervision_percent', 'apartments_number', 'surfaces_total',
        'cost_per_meter', 'financing_cost'
    )
    def _compute_costs(self):
        for rec in self:
            area = rec.area or 0.0
            land_cost = rec.meter_price * area
            rec.land_cost = land_cost
            rec.land_commission = land_cost * 0.025
            rec.re_transaction_tax = land_cost * 0.05
            rec.land_cost_total = land_cost + rec.land_commission + rec.re_transaction_tax

            rec.construction_cost_per_meter = rec.cost_per_meter * rec.surfaces_total
            rec.villa_construction_cost = rec.villas_number * rec.villa_cost
            rec.estimated_construction_cost = rec.villa_construction_cost

            rec.gov_eng_costs_dev = rec.government_engineering_costs * rec.apartments_number
            supervision_base = rec.estimated_construction_cost + rec.gov_eng_costs_dev
            rec.supervision_dev = (rec.supervision_percent / 100) * supervision_base

            rec.total_cost = rec.estimated_construction_cost + rec.land_cost_total + rec.supervision_dev + rec.gov_eng_costs_dev + rec.financing_cost
            rec.floor_avg_cost = rec.total_cost / rec.apartments_number if rec.apartments_number else 0.0

    # ########### End The Costs

    # ########### Financial Restructuring
    @api.depends(
        'land_cost_total',
        'financing_cost',
        'estimated_construction_cost',
        'gov_eng_costs_dev',
        'supervision_dev',
        'company_share',
        'investors_share',
    )
    def _compute_financial_restructuring(self):
        for rec in self:
            # Capital = Land Cost Total + Financing Cost
            rec.capital = (rec.land_cost_total or 0.0) + (rec.financing_cost or 0.0)

            # Financing = Construction + Govt/Eng + Supervision
            rec.financing = (
                    (rec.estimated_construction_cost or 0.0) +
                    (rec.gov_eng_costs_dev or 0.0) +
                    (rec.supervision_dev or 0.0)
            )

            # Total Company Amounts = Company Share * Capital
            rec.total_company_amounts = (rec.company_share) * rec.capital

            # Total Investor Amounts = Investor Share * Capital
            rec.total_investor_amounts = (rec.investors_share) * rec.capital

    # ########### End Financial Restructuring

    # ########### Sales Data
    @api.depends(
        'avg_floor_price_incl_commission',
        'sales_total',
        'total_cost',
        'capital'
    )
    def _compute_sales_data(self):
        for rec in self:
            # Excluding commission
            if rec.avg_floor_price_incl_commission:
                rec.avg_floor_price_excl_commission = rec.avg_floor_price_incl_commission / 1.025
            else:
                rec.avg_floor_price_excl_commission = 0.0

            # Profits = Sales Total - Total Cost
            rec.profits_total = (rec.sales_total or 0.0) - (rec.total_cost or 0.0)

            # Profit Margin = (Sales / Cost) - 1
            if rec.total_cost:
                rec.project_profit_margin = (rec.sales_total / rec.total_cost) - 1
            else:
                rec.project_profit_margin = 0.0

            # Capital Gains Rate = Profits / Capital
            if rec.capital:
                rec.capital_gains_rate = rec.profits_total / rec.capital
            else:
                rec.capital_gains_rate = 0.0

            # Investor Profit % = Capital Gains Rate * 0.85
            rec.investor_profit_percent = rec.capital_gains_rate * 0.85

            # Investor Profits = Investor Profit % * 0.85
            rec.investor_profits = rec.investor_profit_percent * 0.85

    # ########### End Sales Data

    # ########### Company Profits Section
    @api.depends(
        'total_company_amounts',
        'investor_profit_percent',
        'profits_total',
        'sales_total',
        'supervision_dev',
        'area',
        'meter_price',
        'meter_price_for_shareholders'
    )
    def _compute_company_profits(self):
        for rec in self:
            # Company Investment Profits = Total Company Amounts * Investor Profit Percentage
            rec.company_investment_profits = rec.total_company_amounts * round(rec.investor_profit_percent, 2)

            # Investment Mgmt Fee = Profits Total * 15%
            rec.investment_mgmt_fee = (rec.profits_total or 0.0) * 0.15

            # Developer Marketing Striving = Sales Total * 2.5%
            rec.dev_marketing_striving = (rec.sales_total or 0.0) * 0.025

            # Developer Supervision = Supervision (Dev)
            rec.dev_supervision = rec.supervision_dev or 0.0

            # Different Meter Price in Land Purchase = Area * (Meter Price - Meter Price for Shareholders)
            meter_diff = (rec.meter_price or 0.0) - (rec.meter_price_for_shareholders or 0.0)
            rec.diff_meter_price = (rec.area or 0.0) * meter_diff

            # Total Developer Earnings = sum of all above
            rec.total_dev_earnings = (
                    rec.company_investment_profits +
                    rec.investment_mgmt_fee +
                    rec.dev_marketing_striving +
                    rec.dev_supervision +
                    rec.diff_meter_price
            )

    # ########### End Company Profits Section

    @api.depends('depth', 'width')
    def _compute_area(self):
        for rec in self:
            rec.area = rec.depth * rec.width

    @api.depends('villas_number')
    def _compute_apartments_number(self):
        for rec in self:
            rec.apartments_number = rec.villas_number * 3 if rec.villas_number else 0.0

    @api.depends('total_sales_area', 'apartments_number')
    def _compute_average_areas(self):
        for rec in self:
            if rec.apartments_number:
                rec.average_areas = rec.total_sales_area / rec.apartments_number
            else:
                rec.average_areas = 0.0

    @api.depends('area', 'upper_factor', 'width')
    def _compute_totals(self):
        for rec in self:
            area = rec.area or 0.0

            # Total Upper Surfaces = Upper Factor * Area
            rec.total_upper_surfaces = rec.upper_factor * area

            # Lower Factor = (3 * (Width - 4)) / Area
            rec.lower_factor = (3 * (rec.width - 4)) / area if area else 0

            # Total Lower Surfaces = Lower Factor * Area
            rec.total_lower_surfaces = rec.lower_factor * area

            # Surfaces Total = Total Upper Surfaces + Total Lower Surfaces
            rec.surfaces_total = rec.total_upper_surfaces + rec.total_lower_surfaces

            # Surfaces Factor = Surfaces Total / Area
            rec.surfaces_factor = rec.surfaces_total / area if area else 0.0

            # Total Sales Area = Total Upper Surfaces * 0.85
            rec.total_sales_area = rec.total_upper_surfaces * 0.85

            # Sales Area Factor = Total Sales Area / Area
            rec.sales_area_factor = rec.total_sales_area / area if area else 0.0

    @api.depends('latitude', 'longitude', 'street', 'city', 'state')
    def _compute_show_map_button(self):
        for record in self:
            has_coordinates = record.latitude and record.longitude
            has_address = bool(record.street or record.city or (record.state and record.state.name))
            record.show_map_button = bool(has_coordinates or has_address)

    # ##################### End computed field    ########################

    # ################## onchange methods
    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            template = self.template_id
            self.street = template.street
            self.city = template.city
            self.state = template.state
            self.zip = template.zip
            self.country = template.country
            self.latitude = template.latitude
            self.longitude = template.longitude

    # #############################################

    # Button Action: Open Google Maps
    def action_open_google_maps(self):
        self.ensure_one()

        if self.latitude and self.longitude:
            # Use coordinates if available
            url = f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
            # url = get_google_maps_url(self.latitude, self.longitude)
        else:
            # Build address using only street, city, and state
            address_parts = filter(None, [
                self.street,
                self.city,
                self.state.name if self.state else ''
            ])
            address_string = ', '.join(address_parts)

            if not address_string:
                raise UserError(_("No location data available."))

            encoded_address = urllib.parse.quote(address_string)
            url = f"https://www.google.com/maps?q={encoded_address}"

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def action_print_re_developer_pdf(self):
        self.ensure_one()
        return self.env.ref('encode_re_development.action_project_re_developer_report').report_action(self)
    def action_print_re_investor_pdf(self):
        self.ensure_one()
        return self.env.ref('encode_re_development.action_project_re_investor_report').report_action(self)

    def _update_project_end_date(self):
        for project in self:
            last_task = self.env['project.task'].search([
                ('project_id', '=', project.id),
                ('date_deadline', '!=', False)
            ], order="date_deadline desc", limit=1)
            if last_task:
                project.date = last_task.date_deadline