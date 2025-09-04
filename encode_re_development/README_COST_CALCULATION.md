# Automatic Product Cost Calculation Feature

## Overview
This feature automatically calculates and updates the **Standard Cost** field (`standard_price`) in the Product form (product.template) based on the average of past vendor bill prices from the last year.

## Features Implemented

### 1. Automatic Cost Calculation
- **Formula**: Cost = (Sum of all Vendor Bill Line Prices for the product ÷ Count of Vendor Bill Lines for the product)
- **Time Period**: Last year from today
- **Scope**: Only posted vendor bills (in_invoice with state='posted')
- **Filter**: Only considers lines with positive prices

### 2. New Fields Added to Product Template
- `cost_calculation_date_from`: Start date of calculation period
- `cost_calculation_date_to`: End date of calculation period  
- `cost_calculation_note`: Human-readable note about the calculation (styled in grey)
- `vendor_bill_count`: Number of vendor bills used in calculation

**Note**: The `standard_price` field is automatically updated with the calculated cost.

### 3. Automatic Updates
- **Real-time**: Costs are recalculated when vendor bills are posted, cancelled, reset to draft, modified, or deleted
- **Product Creation**: Costs are calculated immediately when new products are created
- **Product Modification**: Costs are recalculated when products are modified
- **Scheduled**: Daily cron job recalculates all product costs
- **Manual**: Button on product form to force cost recalculation

### 4. User Interface
- **Form View**: Shows updated standard cost (readonly) with grey-styled calculation note and compact recalculate button
- **List View**: Displays vendor bill count
- **Search View**: Filters for products with/without auto-calculated costs

## Technical Implementation

### Models Modified/Created
1. **product.template** (enhanced)
   - Added fields for cost calculation tracking
   - Added computation method `_compute_calculated_cost()` that updates `standard_price`
   - Added `_update_all_product_costs()` method for bulk updates
   - Override `create()` method to calculate costs for new products
   - Override `write()` method to recalculate costs when products are modified
   - Added `action_recalculate_cost()` method for manual recalculation
   - Implemented recursion prevention using context flags
   - Enhanced vendor bill search logic with comprehensive filtering

2. **account.move** (enhanced)
   - Override `write()` method to trigger cost recalculation when bills are modified (posted, cancelled, reset to draft, etc.)
   - Override `unlink()` method to trigger cost recalculation when bills are deleted
   - Added `_recalculate_product_costs()` method

### Views Created/Modified
1. **product_template_views.xml**
   - Enhanced form view with grey-styled calculation note
   - Added list view with vendor bill count column
   - Added search view with auto-calculated cost filters

### Automation
1. **Cron Job**: Daily automatic recalculation for all products
2. **Triggers**: Automatic recalculation when vendor bills are posted, cancelled, reset to draft, modified, or deleted
3. **Product Triggers**: Automatic calculation when products are created or modified
4. **Manual**: Button on product form to force cost recalculation

## Usage

### For Accounting Managers
1. **View Auto-Calculated Costs**: Open any product and see the automatically updated standard cost (readonly)
2. **Check Calculation Period**: View the grey-styled note showing the date range used
3. **Manual Recalculation**: Use the "🔄 Recalc" button to force immediate updates

### For System Administrators
1. **Monitor Cron Jobs**: Check the scheduled job "Recalculate Product Costs from Vendor Bills" (runs daily)
2. **Adjust Calculation Period**: Modify the `_compute_calculated_cost()` method if needed
3. **Performance**: The calculation is optimized to only process relevant vendor bills
4. **Bulk Updates**: All products are automatically updated regardless of how they're accessed
5. **Recursion Prevention**: Context flags prevent infinite loops during cost calculations

## Example Calculation
```
Vendor Bill Line on 01/01/2025 → 100 SR
Vendor Bill Line on 02/01/2025 → 120 SR  
Vendor Bill Line on 03/01/2025 → 130 SR

Standard Cost = (100 + 120 + 130) ÷ 3 = 116.67 SR
Note: "💡 Auto-calculated cost from 3 vendor bills (01/01/2024 to 01/01/2025)"
```

## Dependencies
- `account` module (for vendor bill functionality)
- `product` module (base product functionality)
- `dateutil` library (for date calculations)

## Security
- All calculated fields are read-only for users
- Only system administrators can modify the calculation logic
- Proper access controls on vendor bill data

## Future Enhancements
1. Configurable calculation periods (monthly, quarterly, etc.)
2. Weighted average based on quantities
3. Currency conversion support
4. Historical cost tracking
5. Cost trend analysis
