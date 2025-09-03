# Encode Project Dashboard

A modern, real-time project dashboard for Odoo 18 that provides comprehensive project performance metrics with live updates and interactive visualizations.

## 🚀 Features

### 📊 **Three Key Performance Metrics**
- **Completion %** - Task completion progress (large ring chart)
- **SPI (Schedule Performance Index)** - Time efficiency (small ring chart)  
- **Cost Spent %** - Budget utilization (small ring chart)

### 🎨 **Modern UI/UX**
- **Clean, professional design** with off-white background
- **Responsive grid layout** supporting multiple projects
- **Interactive ring charts** with smooth animations
- **Live data updates** without page refresh
- **Progressive ring animations** every 20 seconds
- **Hover effects** and visual feedback

### 📱 **Smart Indicators**
- **Task count** with blue icon
- **Completed tasks** with green checkmark
- **Allocated hours** with purple hourglass (smaller icon)
- **Time spent** with light blue clock
- **Budget amount** with yellow money icon

### 🎯 **Clickable Project Cards**
- **Click any project card** to open its form view
- **Keyboard navigation** support (Enter key)
- **Visual hover states** with color transitions

## 📋 Requirements

### **Dependencies**
- Odoo 18.0+
- `encode_project_budget` module (for budget data)
- `project` module (standard Odoo)

### **Optional Dependencies**
- `account_budget` module (for budget.line model)

## 🛠️ Installation

1. **Copy the module** to your Odoo addons directory
2. **Update the module list** in Odoo
3. **Install the module** `encode_project_dashboard`
4. **Restart Odoo** to ensure all assets are loaded

## 📊 Metric Calculations

### **Completion %**
```
Completion % = (Completed Tasks ÷ Total Tasks) × 100
```
- **Color**: Always blue
- **Logic**: Shows task completion progress
- **Edge cases**: 0% if no tasks, 100% if all tasks completed

### **SPI (Schedule Performance Index)**
```
SPI = Allocated Hours ÷ Total Time Spent
```
- **Display**: Index value (e.g., 1.25, 0.85)
- **Color thresholds**:
  - 🟢 **Green**: ≥ 1.0 (on or under schedule)
  - 🟡 **Yellow**: 0.9 – 0.99 (slightly over schedule)
  - 🔴 **Red**: < 0.9 (significantly over schedule)
- **Edge cases**: 0 if either time value is 0, 1.0 if all tasks completed

### **Cost Spent %**
```
Cost Spent % = (Achieved ÷ Budgeted) × 100
```
- **Color thresholds**:
  - 🟢 **Green**: ≥ 100% (on or under budget)
  - 🟡 **Yellow**: 90% – 99% (slightly over budget)
  - 🔴 **Red**: < 90% (significantly over budget)
- **Edge cases**: 100% if achieved > 0 but no budget, 0% if no budget data

## 🎨 Color Coding System

### **Ring Charts**
- **Completion %**: Always blue (#007bff)
- **SPI & Cost %**: Dynamic based on thresholds
  - **Good**: Green (#28a745)
  - **Warning**: Yellow (#ffc107)
  - **Danger**: Red (#dc3545)

### **Indicators**
- **Tasks**: Blue (#007bff) when > 0, muted when 0
- **Done**: Green (#28a745) when > 0, muted when 0
- **Allocated**: Purple (#6f42c1) when > 0, muted when 0
- **Hours**: Light Blue (#17a2b8) when > 0, muted when 0
- **Budget**: Yellow (#ffc107) when > 0, muted when 0

## 🔧 Technical Architecture

### **Backend (Python)**
- **Model**: `project.project` extension
- **Methods**:
  - `get_dashboard_data()` - Single project data
  - `get_all_dashboard_data()` - All active projects
- **Data Sources**:
  - Odoo built-in task count fields
  - Timesheet calculations from project tasks
  - Budget data from `budget.line` and `budget.analytic`

### **Frontend (JavaScript/OWL)**
- **Component**: `ProjectDashboard`
- **Features**:
  - Real-time data updates (30-second intervals)
  - Progressive ring animations (20-second intervals)
  - Dynamic chart rendering with SVG
  - Responsive design with CSS Grid

### **Styling (CSS)**
- **Modern design** with subtle shadows and gradients
- **Smooth animations** with cubic-bezier easing
- **Responsive breakpoints** for mobile devices
- **Accessibility features** with focus states

## 📁 File Structure

```
encode_project_dashboard/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   └── project.py
├── static/
│   └── src/
│       ├── css/
│       │   └── project_dashboard.css
│       ├── js/
│       │   └── project_dashboard.js
│       └── xml/
│           └── project_dashboard.xml
└── views/
    └── project_dashboard_views.xml
```

## 🚀 Usage

### **Accessing the Dashboard**
1. Navigate to **Project** module
2. Click on **"Dashboard"** in the main menu (appears before "Projects")
3. View all active projects with their performance metrics

### **Interacting with Projects**
- **Click any project card** to open its detailed form view
- **Hover over charts** to see enhanced visual effects
- **Watch live updates** as data changes automatically

### **Understanding the Metrics**
- **Completion %**: How much of the project is done (task-based)
- **SPI**: How efficiently time is being used (time-based)
- **Cost %**: How well the budget is being managed (budget-based)

## 🔍 Troubleshooting

### **Common Issues**

#### **All values showing as 0**
- Check if projects have tasks assigned
- Verify allocated hours are set on projects
- Ensure budget data exists in `budget.line` records

#### **Dashboard not appearing**
- Clear browser cache and reload
- Restart Odoo server
- Check module installation status

#### **Budget data not showing**
- Verify `encode_project_budget` module is installed
- Check if projects have linked budget records
- Ensure budget lines have `budget_amount` or `budgeted` fields

### **Debug Mode**
Enable debug logging in Odoo to see detailed calculation logs:
```python
# In Odoo shell or logs
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
```

## 🎯 Performance Considerations

### **Optimizations**
- **Lazy loading** of project data
- **Efficient queries** using Odoo's built-in fields
- **Minimal DOM updates** with targeted animations
- **Responsive design** for various screen sizes

### **Scalability**
- **Grid layout** automatically adjusts to project count
- **Efficient data processing** in JavaScript
- **Minimal server load** with client-side calculations

## 🤝 Contributing

### **Development Setup**
1. Clone the repository
2. Install in development mode
3. Make changes and test thoroughly
4. Submit pull request with detailed description

### **Code Standards**
- Follow Odoo coding standards
- Use meaningful variable names
- Add comments for complex logic
- Test edge cases thoroughly

## 📄 License

This module is licensed under AGPL-3.0, same as Odoo.

## 🙏 Acknowledgments

- **Odoo Community** for the excellent framework
- **Font Awesome** for the beautiful icons
- **Modern CSS** techniques for smooth animations

## 📞 Support

For support, questions, or feature requests:
- Create an issue on the repository
- Contact the development team
- Check the troubleshooting section above

---

**Made with ❤️ for the Odoo Community**
