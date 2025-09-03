/** @odoo-module **/

import { Component, onWillStart, onMounted, useState, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

console.log("🔧 Loading Project Dashboard module...");

class ProjectDashboard extends Component {

    /**
     * Setup method to initialize required services and register event handlers.
     */
	setup() {
		super.setup();
        console.log("🔧 Setting up ProjectDashboard component...");
		this.orm = useService("orm");

		this.state = useState({
            projects: [],
            filteredProjects: [],
            loading: true,
            error: null,
            lastUpdate: null,
            searchQuery: '',
            statusFilters: { all: true, active: false, completed: false },
            activeFilters: false,
            activeFilterType: 'all' // Track which filter is active for badge color
        });

        // Force sticky header behavior
        this.forceStickyHeader();


		onWillStart(async () => {
            console.log("🔧 onWillStart triggered...");
            await this.loadDashboardData();
        });

        // runs once right after your component is first rendered and its DOM is attached ,
        // things that need the DOM (charts, animations, timers, sockets).
        onMounted(() => {
            console.log("🔧 ProjectDashboard mounted");
            this.renderCharts();
            //  // Progressive ring movement every 20 seconds to show live data
            // not used
            //            this.startLiveAnimations();

            // Update data every 30 seconds without page refresh
            this.startDataUpdates();
        });

        onWillUnmount(() => {
            // Clean up intervals when component is destroyed
            if (this.updateInterval) {
                clearInterval(this.updateInterval);
            }
        });
    }
    //  End setup

    //  TODO: Not called.
    // mounted
    mounted() {
        console.log("🔧 mounted...");
        // Ensure sticky header works after component is mounted
        this.forceStickyHeader();

        // Add scroll event listener to maintain sticky behavior
        window.addEventListener('scroll', () => {
            this.forceStickyHeader();
        });
    }

    // Load Data
    async loadDashboardData() {
        console.log("🔧 Loading dashboard data...");
        try {
            this.state.loading = true;
            const rawData = await this.orm.call(
                "project.project",
                "get_all_dashboard_data",
                []
            );

            // Process raw data and calculate metrics , return to (state > projects)
            this.state.projects = rawData.map(project => {
                const processed = this.calculateProjectMetrics(project);
                return processed;
            });

            console.log("🔧 Loading dashboard data...projects:",this.state.projects);
            // Initialize filtered projects, return to (state > filteredProjects)
            this.state.filteredProjects = [...this.state.projects];

            this.state.loading = false;
        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.state.error = error.message;
            this.state.loading = false;
        }
    }

    // Load Matrics
    calculateProjectMetrics(rawProject) {
        // Use Odoo's built-in task count fields
        const totalTasks = rawProject.total_tasks || 0;
        const completedTasks = rawProject.closed_tasks || 0;
        const openTasks = rawProject.open_tasks || 0;
        const totalTimeSpent = rawProject.total_time_spent || 0;

        // Calculate budget metrics
        const totalAchieved = rawProject.budget_lines.reduce((sum, line) => sum + (line.achieved_amount || 0), 0);
        const totalBudgeted = rawProject.budget_lines.reduce((sum, line) => sum + (line.budgeted || 0), 0);

        console.log(`🔍 Project ${rawProject.name} budget data:`, {
            budget_lines: rawProject.budget_lines,
            totalAchieved,
            totalBudgeted,
            budget_lines_length: rawProject.budget_lines?.length || 0,
            raw_project_keys: Object.keys(rawProject)
        });

        // Check if budget data might be in a different format
        if (totalBudgeted === 0 && totalAchieved === 0) {
            console.log(`⚠️ No budget data found for project ${rawProject.name}, checking alternative fields...`);
            console.log(`📊 Raw project data:`, rawProject);
        }

        // Calculate Completion % based on completed tasks
        let completionPercentage = 0;
        if (totalTasks > 0) {
            completionPercentage = (completedTasks / totalTasks) * 100;
        }

        // Calculate SPI based on total time spent vs allocated hours
        let spiValue = 0;
        if (rawProject.allocated_hours > 0 && totalTimeSpent > 0) {
            spiValue = totalTimeSpent / rawProject.allocated_hours;
        } else if (rawProject.allocated_hours > 0 && totalTimeSpent === 0) {
            // If there are allocated hours but no time spent, SPI should be 0
            spiValue = 0;
        } else if (totalTasks > 0 && completedTasks === totalTasks && totalTimeSpent > 0) {
            // If all tasks are completed and there's time spent, SPI should be 1.0 (on schedule)
            spiValue = 1.0;
        } else {
            // For all other cases, SPI should be 0
            spiValue = 0;
        }

        // Calculate Cost Spent % based on achieved vs budgeted amounts
        let costSpentPercentage = 0;
        if (totalBudgeted > 0) {
            costSpentPercentage = (totalAchieved / totalBudgeted) * 100;
        } else if (totalAchieved > 0) {
            // If there's achieved amount but no budget, show 100% (over budget)
            costSpentPercentage = 100;
        }

        console.log(`💰 Project ${rawProject.name} cost calculation:`, {
            totalAchieved,
            totalBudgeted,
            costSpentPercentage
        });

        // Determine colors
        const getColorClass = (metricType, value) => {
            if (metricType === 'completion') {
                return 'completion'; // Always blue for completion
            } else if (metricType === 'spi') {
                if (value >= 1.0) return 'good';
                else if (value >= 0.9) return 'warning';
                else return 'danger';
            } else if (metricType === 'cost') {
                const ratio = value / 100.0;
                if (ratio >= 1.0) return 'good';
                else if (ratio >= 0.9) return 'warning';
                else return 'danger';
            }
        };

        return {
            id: rawProject.id,
            name: rawProject.name,
            completion: {
                value: Math.round(completionPercentage * 10) / 10,
                color_class: getColorClass('completion', completionPercentage)
            },
            spi: {
                value: parseFloat(spiValue.toFixed(2)),
                color_class: getColorClass('spi', parseFloat(spiValue.toFixed(2)))
            },
            cost: {
                value: Math.round(costSpentPercentage * 10) / 10,
                color_class: getColorClass('cost', costSpentPercentage)
            },
            allocated_hours: rawProject.allocated_hours,
            total_time_spent: totalTimeSpent,
            total_tasks: totalTasks,
            completed_tasks: completedTasks,
            open_tasks: openTasks,
            budget_achieved: totalAchieved,
            budget_budgeted: totalBudgeted,
            budget_achieved_formatted: this.formatNumberWithSuffix(totalAchieved),
            budget_budgeted_formatted: this.formatNumberWithSuffix(totalBudgeted),
        };
    }

    // render Charts
    renderCharts() {
        this.state.projects.forEach((project, index) => {
            setTimeout(() => {
                // Completion chart (large)
                const completionContainer = document.querySelector(`[data-project-id="${project.id}"] .encode-completion-chart`);
                if (completionContainer) {
                    this.renderRingChart(completionContainer, project.completion.value, project.completion.color_class, 'large', 'completion');
                }

                // SPI chart (small)
                const spiContainer = document.querySelector(`[data-project-id="${project.id}"] .encode-spi-chart`);
                if (spiContainer) {
                    this.renderRingChart(spiContainer, project.spi.value, project.spi.color_class, 'small', 'spi');
                }

                // Cost chart (small)
                const costContainer = document.querySelector(`[data-project-id="${project.id}"] .encode-cost-chart`);
                if (costContainer) {
                    this.renderRingChart(costContainer, project.cost.value, project.cost.color_class, 'small', 'cost');
                }
            }, index * 200); // Stagger the animations
        });
    }

    // render Ring Chart
    renderRingChart(container, percentage, colorClass, size = 'large', chartType = 'completion') {
        if (!container) return;

        const radius = size === 'large' ? 60 : 40;
        const strokeWidth = size === 'large' ? 8 : 6;
        const circumference = 2 * Math.PI * radius;

        // Handle SPI values differently (they're not percentages)
        let progress, displayValue;
        if (chartType === 'spi') {
            // SPI is an index, normalize so that 1.0 = full ring (perfect efficiency)
            // Range: 0-2, where 1.0 is perfect, >1.0 is efficient, <1.0 is inefficient
            progress = Math.min(percentage, 2) / 2; // This makes 1.0 = 0.5 (half ring)
            // Let's adjust so 1.0 = full ring, 2.0 = full ring, 0.5 = quarter ring
            if (percentage <= 1.0) {
                progress = percentage; // 0-1 range maps to 0-100% ring
            } else {
                progress = 1.0; // Anything above 1.0 shows as full ring
            }
            displayValue = parseFloat(percentage).toFixed(2); // Always show two decimal places
        } else {
            // Regular percentage handling
            progress = Math.min(percentage, 100) / 100;
            displayValue = `${Math.round(percentage)}%`;
        }

        const strokeDasharray = circumference * progress;

        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("width", radius * 2 + 20);
        svg.setAttribute("height", radius * 2 + 20);
        svg.setAttribute("viewBox", `0 0 ${radius * 2 + 20} ${radius * 2 + 20}`);
        svg.style.transition = 'all 0.5s ease';

        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", radius + 10);
        circle.setAttribute("cy", radius + 10);
        circle.setAttribute("r", radius);
        circle.setAttribute("fill", "none");
        circle.setAttribute("stroke", "#e9ecef");
        circle.setAttribute("stroke-width", strokeWidth);

        const progressCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        progressCircle.setAttribute("cx", radius + 10);
        progressCircle.setAttribute("cy", radius + 10);
        progressCircle.setAttribute("r", radius);
        progressCircle.setAttribute("fill", "none");
        progressCircle.setAttribute("stroke", this.getColorValue(colorClass));
        progressCircle.setAttribute("stroke-width", strokeWidth);
        progressCircle.setAttribute("stroke-linecap", "round");
        progressCircle.setAttribute("stroke-dasharray", `${strokeDasharray} ${circumference - strokeDasharray}`);
        progressCircle.setAttribute("stroke-dashoffset", 0);
        progressCircle.setAttribute("transform", `rotate(-90 ${radius + 10} ${radius + 10})`);
        progressCircle.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
        progressCircle.style.filter = 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1))';

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", radius + 10);
        text.setAttribute("y", radius + 10);
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("dominant-baseline", "middle");
        text.setAttribute("font-size", size === 'large' ? "16" : "12");
        text.setAttribute("font-weight", "bold");
        text.setAttribute("fill", "#2c3e50");
        text.textContent = displayValue; // Use displayValue here
        text.style.transition = 'all 0.3s ease';

        svg.appendChild(circle);
        svg.appendChild(progressCircle);
        svg.appendChild(text);

        container.innerHTML = '';
        container.appendChild(svg);

        // Add entrance animation
        setTimeout(() => {
            progressCircle.style.opacity = '1';
            text.style.opacity = '1';
        }, 100);
    }

    // get Color Value
    getColorValue(colorClass) {
        switch (colorClass) {
            case 'completion': return '#007bff'; // Blue
            case 'good': return '#28a745'; // Green
            case 'warning': return '#ffc107'; // Yellow
            case 'danger': return '#dc3545'; // Red
            default: return '#6c757d'; // Gray
        }
    }
    getColorClass(value) {
        // For SPI values (0-2 range, where 1.0 is perfect)
        if (value >= 1.0) {
            return 'good'; // Green
        } else if (value >= 0.9) {
            return 'warning'; // Yellow
        } else {
            return 'danger'; // Red
        }
    }
    getColorClassForCost(value) {
        // For Cost percentage values (0-100 range)
        if (value >= 100) {
            return 'good'; // Green (100% or more is good)
        } else if (value >= 90) {
            return 'warning'; // Yellow (90-99% is warning)
        } else {
            return 'danger'; // Red (below 90% is danger)
        }
    }


    // open Project
    openProject(projectId) {
        // Navigate to project form view using window.location
        window.location.href = `/web#id=${projectId}&model=project.project&view_type=form`;
    }

    // update Status Filter
    updateStatusFilter(filterType, checked) {
        // Reset all filters
        this.state.statusFilters = { all: false, active: false, completed: false };

        // Set the selected filter
        this.state.statusFilters[filterType] = true;
        this.state.activeFilterType = filterType;

        this.applyFilters();
    }

    // apply Filters
    applyFilters() {
        let filtered = [...this.state.projects];

        // Apply search filter
        if (this.state.searchQuery) {
            const query = this.state.searchQuery.toLowerCase();
            filtered = filtered.filter(project =>
                project.name.toLowerCase().includes(query)
            );
        }

        // Apply status filters
        if (this.state.statusFilters.active) {
            filtered = filtered.filter(project =>
                project.completion.value < 100
            );
        }
        if (this.state.statusFilters.completed) {
            filtered = filtered.filter(project =>
                project.completion.value === 100
            );
        }

        // Check if any filters are active
        this.state.activeFilters = this.state.searchQuery ||
                                  this.state.statusFilters.active ||
                                  this.state.statusFilters.completed;

        // Update filtered projects
        this.state.filteredProjects = filtered;

        // Re-render charts for filtered projects
        setTimeout(() => {
            this.renderCharts();
        }, 100);
    }

    // Search and Filter Methods
    filterProjects(searchQuery) {
        this.state.searchQuery = searchQuery;
        this.state.activeFilterType = searchQuery ? 'search' : 'all';
        this.applyFilters();
    }


    // Refresh data
    refresh() {
        console.log("🔧 Refreshing data...");
        this.loadDashboardData(); 
    }

    // Clear Search
    clearSearch() {
        this.state.searchQuery = '';
        this.state.activeFilterType = 'all';
        this.applyFilters();
    }

    // Force sticky header to work properly
    forceStickyHeader() {
        setTimeout(() => {
            const header = document.querySelector('.encode-dashboard-header');
            console.log("🔧 header...",header);
            if (header) {
                // Force sticky positioning
                header.style.position = 'sticky';
                header.style.top = '0';
                header.style.zIndex = '100';
                header.style.background = 'rgba(255, 255, 255, 0.7)';
                header.style.backdropFilter = 'blur(10px)';
                header.style.webkitBackdropFilter = 'blur(10px)';

                // Ensure parent containers allow sticky positioning
                const parentContainers = header.closest('.o_action_manager');
                if (parentContainers) {
                    parentContainers.style.overflow = 'visible';
                }

                const contentContainer = header.closest('.o_content');
                if (contentContainer) {
                    contentContainer.style.overflow = 'visible';
                }
            }
        }, 100);
    }

    // Progressive ring movement every 20 seconds to show live data
    startLiveAnimations() {
        // Progressive ring movement every 20 seconds to show live data
        setInterval(() => {
            this.animateRingProgressive();
        }, 20000);
    }
    animateRingProgressive() {
        this.state.projects.forEach(project => {
            // Animate completion ring
            this.animateRingProgressiveMovement(project.id, 'completion', project.completion.value);

            // Animate SPI ring
            this.animateRingProgressiveMovement(project.id, 'spi', project.spi.value * 100);

            // Animate cost ring
            this.animateRingProgressiveMovement(project.id, 'cost', project.cost.value);
        });
    }
    animateRingProgressiveMovement(projectId, chartType, currentValue) {
        const card = document.querySelector(`[data-project-id="${projectId}"]`);
        if (!card) return;

        // Get the specific chart container
        let chartContainer;
        switch (chartType) {
            case 'completion':
                chartContainer = card.querySelector('.encode-completion-chart');
                break;
            case 'spi':
                chartContainer = card.querySelector('.encode-spi-chart');
                break;
            case 'cost':
                chartContainer = card.querySelector('.encode-cost-chart');
                break;
        }

        if (chartContainer) {
            const progressCircle = chartContainer.querySelector('circle[stroke-dasharray]');
            if (progressCircle) {
                const radius = chartType === 'completion' ? 60 : 40;
                const circumference = 2 * Math.PI * radius;
                const currentProgress = Math.min(currentValue, 100) / 100;
                const currentStrokeDasharray = circumference * currentProgress;
                const remaining = circumference - currentStrokeDasharray;

                // Set CSS variables for progressive filling animation
                progressCircle.style.setProperty('--circumference', circumference);
                progressCircle.style.setProperty('--current-progress', currentStrokeDasharray);
                progressCircle.style.setProperty('--remaining', remaining);

                // Add updating class to trigger filling animation
                card.classList.add('ring-updating');

                // Remove updating class after animation
                setTimeout(() => {
                    card.classList.remove('ring-updating');
                }, 2000);
            }
        }
    }


    startDataUpdates() {
        // Update data and trigger synchronized animations every 10 seconds
        this.updateInterval = setInterval(async () => {
            await this.updateDashboardData();
        }, 10000); // 10 seconds
    }
    async updateDashboardData() {
        try {
            console.log("🔧 Updating dashboard data...");
            const rawData = await this.orm.call(
                "project.project",
                "get_all_dashboard_data",
                []
            );

            // Update state with new data
            const updatedProjects = rawData.map(project => this.calculateProjectMetrics(project));

            // Animate transitions from current values to new values
            await this.animateDataTransition(updatedProjects);

            // Update state with new data
            this.state.projects = updatedProjects;
            this.state.filteredProjects = updatedProjects;
            this.state.lastUpdate = new Date().toLocaleTimeString();

            console.log("🔧 Dashboard data updated successfully");
        } catch (error) {
            console.error("Error updating dashboard data:", error);
        }
    }

    // removed : not used
    animateRingUpdates(newProjects) {
        this.state.projects.forEach((oldProject, index) => {
            const newProject = newProjects[index];
            if (newProject && oldProject) {
                // Check if completion percentage changed
                if (Math.abs(oldProject.completion.value - newProject.completion.value) > 0.1) {
                    this.animateRingUpdate(oldProject.id, 'completion', newProject.completion.value);
                }

                // Check if SPI changed
                if (Math.abs(oldProject.spi.value - newProject.spi.value) > 0.01) {
                    this.animateRingUpdate(oldProject.id, 'spi', newProject.spi.value);
                }

                // Check if cost changed
                if (Math.abs(oldProject.cost.value - newProject.cost.value) > 0.1) {
                    this.animateRingUpdate(oldProject.id, 'cost', newProject.cost.value);
                }
            }
        });
    }
    animateRingUpdate(projectId, chartType, newValue) {
        const card = document.querySelector(`[data-project-id="${projectId}"]`);
        if (!card) return;

        // Get the specific chart container
        let chartContainer;
        switch (chartType) {
            case 'completion':
                chartContainer = card.querySelector('.encode-completion-chart');
                break;
            case 'spi':
                chartContainer = card.querySelector('.encode-spi-chart');
                break;
            case 'cost':
                chartContainer = card.querySelector('.encode-cost-chart');
                break;
        }

        if (chartContainer) {
            // Animate the ring update
            const progressCircle = chartContainer.querySelector('circle[stroke-dasharray]');
            if (progressCircle) {
                const radius = chartType === 'completion' ? 60 : 40;
                const circumference = 2 * Math.PI * radius;

                // Handle SPI values differently
                let newProgress;
                if (chartType === 'spi') {
                    if (newValue <= 1.0) {
                        newProgress = newValue; // 0-1 range maps to 0-100% ring
                    } else {
                        newProgress = 1.0; // Anything above 1.0 shows as full ring
                    }
                } else {
                    newProgress = Math.min(newValue, 100) / 100;
                }

                const newStrokeDasharray = circumference * newProgress;

                // Update the ring smoothly
                setTimeout(() => {
                    progressCircle.setAttribute('stroke-dasharray', `${newStrokeDasharray} ${circumference - newStrokeDasharray}`);

                    // Update the text
                    const text = chartContainer.querySelector('text');
                    if (text) {
                        if (chartType === 'spi') {
                            text.textContent = parseFloat(newValue).toFixed(2); // Always show two decimal places
                        } else {
                            text.textContent = `${Math.round(newValue)}%`;
                        }
                    }
                }, 500);
            }
        }
    }

    // new
    animateNumberChange(element, startValue, endValue, suffix, stepDuration, steps) {
        if (!element) return;

        const difference = endValue - startValue;
        const increment = difference / steps;
        let currentStep = 0;

        const animate = () => {
            currentStep++;
            const currentValue = startValue + (increment * currentStep);

            // Format the value based on suffix/type
            let displayValue;
            if (suffix === '%') {
                displayValue = Math.round(currentValue) + suffix;
            } else if (suffix === 'hours') {
                displayValue = parseFloat(currentValue).toFixed(2); // No 'h' suffix
            } else if (suffix === 'currency') {
                displayValue = this.formatCurrency(currentValue);
            } else if (element.classList.contains('encode-spi-value')) {
                displayValue = parseFloat(currentValue).toFixed(2);
            } else {
                displayValue = Math.round(currentValue);
            }

            element.textContent = displayValue;

            if (currentStep < steps) {
                setTimeout(animate, stepDuration);
            }
        };

        animate();
    }
    animateRingTransition(card, oldProject, newProject, stepDuration, steps) {
        // Animate completion ring
        this.animateRingValue(
            card.querySelector('.encode-completion-chart'),
            oldProject.completion.value,
            newProject.completion.value,
            stepDuration,
            steps,
            'completion'
        );

        // Animate SPI ring
        this.animateRingValue(
            card.querySelector('.encode-spi-chart'),
            oldProject.spi.value,
            newProject.spi.value,
            stepDuration,
            steps,
            'spi'
        );

        // Animate cost ring
        this.animateRingValue(
            card.querySelector('.encode-cost-chart'),
            oldProject.cost.value,
            newProject.cost.value,
            stepDuration,
            steps,
            'cost'
        );
    }
    animateRingValue(chartContainer, startValue, endValue, stepDuration, steps, chartType) {
        if (!chartContainer) return;

        const progressCircle = chartContainer.querySelector('circle[stroke-dasharray]');
        const textElement = chartContainer.querySelector('text');
        if (!progressCircle || !textElement) return;

        const radius = chartType === 'completion' ? 60 : 40;
        const circumference = 2 * Math.PI * radius;
        const difference = endValue - startValue;
        const increment = difference / steps;
        let currentStep = 0;

        const animate = () => {
            currentStep++;
            const currentValue = startValue + (increment * currentStep);

            // Calculate ring progress
            let progress;
            if (chartType === 'spi') {
                if (currentValue <= 1.0) {
                    progress = currentValue;
                } else {
                    progress = 1.0;
                }
            } else {
                progress = Math.min(currentValue, 100) / 100;
            }

            const strokeDasharray = circumference * progress;
            progressCircle.setAttribute('stroke-dasharray', `${strokeDasharray} ${circumference - strokeDasharray}`);

            // Update text
            if (chartType === 'spi') {
                textElement.textContent = parseFloat(currentValue).toFixed(2);
            } else {
                textElement.textContent = `${Math.round(currentValue)}%`;
            }

            // Update color for SPI and Cost rings
            if (chartType === 'spi') {
                const colorClass = this.getColorClass(currentValue);
                progressCircle.setAttribute("stroke", this.getColorValue(colorClass));
            } else if (chartType === 'cost') {
                const colorClass = this.getColorClassForCost(currentValue);
                progressCircle.setAttribute("stroke", this.getColorValue(colorClass));
            }

            if (currentStep < steps) {
                setTimeout(animate, stepDuration);
            }
        };

        animate();
    }
    async animateDataTransition(newProjects) {
        const animationPromises = [];

        this.state.filteredProjects.forEach((oldProject, index) => {
            const newProject = newProjects[index];
            if (newProject && oldProject) {
                // Animate ring and number changes together
                const promise = this.animateProjectTransition(oldProject, newProject);
                animationPromises.push(promise);
            }
        });

        // Wait for all animations to complete
        await Promise.all(animationPromises);
    }
    async animateProjectTransition(oldProject, newProject) {
        const card = document.querySelector(`[data-project-id="${oldProject.id}"]`);
        if (!card) {
            return;
        }

        const animationDuration = 2000; // 2 seconds animation
        const steps = 60; // 60 steps for smooth animation
        const stepDuration = animationDuration / steps;

        // Find all indicator text elements
        const indicatorTexts = card.querySelectorAll('.encode-indicator-text');

        // Animate each indicator based on its position
        indicatorTexts.forEach((element, index) => {
            let startValue, endValue, suffix;

            switch (index) {
                case 0: // Tasks
                    startValue = oldProject.total_tasks;
                    endValue = newProject.total_tasks;
                    suffix = 'number';
                    break;
                case 1: // Completed tasks
                    startValue = oldProject.completed_tasks;
                    endValue = newProject.completed_tasks;
                    suffix = 'number';
                    break;
                case 2: // Allocated hours
                    startValue = oldProject.allocated_hours;
                    endValue = newProject.allocated_hours;
                    suffix = 'hours';
                    break;
                case 3: // Total hours
                    startValue = oldProject.total_time_spent;
                    endValue = newProject.total_time_spent;
                    suffix = 'hours';
                    break;
                case 4: // Budget
                    startValue = oldProject.budget_budgeted;
                    endValue = newProject.budget_budgeted;
                    suffix = 'currency';
                    break;
                default:
                    return;
            }

            this.animateNumberChange(element, startValue, endValue, suffix, stepDuration, steps);
        });

        // Animate ring charts with synchronized timing
        this.animateRingTransition(card, oldProject, newProject, stepDuration, steps);
    }


    formatNumberWithSuffix(number) {
        if (number === 0) return '0';

        const absNumber = Math.abs(number);
        if (absNumber >= 1000000000) {
            return (number / 1000000000).toFixed(1) + 'B';
        } else if (absNumber >= 1000000) {
            return (number / 1000000).toFixed(1) + 'M';
        } else if (absNumber >= 1000) {
            return (number / 1000).toFixed(1) + 'K';
        } else {
            return number.toString();
        }
    }
    formatCurrency(amount) {
        if (amount === 0) return '0';

        const absAmount = Math.abs(amount);
        if (absAmount >= 1000000000) {
            return (amount / 1000000000).toFixed(2) + 'B';
        } else if (absAmount >= 1000000) {
            return (amount / 1000000).toFixed(2) + 'M';
        } else if (absAmount >= 1000) {
            return (amount / 1000).toFixed(2) + 'K';
        } else {
            return amount.toFixed(2);
        }
    }
}





ProjectDashboard.template = "ProjectDashboardTemplate";

// test before call component
console.log("🔧 Registering project_dashboard action...");

// Keep your chosen tag registration
registry.category('actions').add('project_dashboard_tag', ProjectDashboard);

// test after call component (all good)
console.log("🔧 Project Dashboard module loaded successfully!");
