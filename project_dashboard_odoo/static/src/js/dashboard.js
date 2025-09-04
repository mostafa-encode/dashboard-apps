/** @odoo-module */
import { registry} from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart} = owl
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";
import { onMounted, useRef, useState} from "@odoo/owl";

export class ProjectDashboardComponent extends Component {
    /**
     * Setup method to initialize required services and register event handlers.
     */
	setup() {
        this.action = useService("action");
        this.orm = useService("orm");

        this.project_task_doughnut = useRef("project_task_doughnut");
        this.project_doughnut = useRef("project_doughnut");
        this.project_selection = useRef("project_selection");
        this.start_date = useRef("start_date");
        this.end_date = useRef("end_date");
        this.tot_project = useRef("tot_project");
        this.tot_employee = useRef("tot_employee");
        this.tot_hrs = useRef("tot_hrs");
        this.tot_margin = useRef("tot_margin");
        this.total_task = useRef("tot_task");
        this.total_so = useRef("tot_so");
        this.employee_selection = useRef("employee_selection");
        this.top_selling_employees = useRef("top_selling_employees");
        this.material_requisitions_status = useRef("material_requisitions_status");
        this.gantt_chart = useRef("gantt_chart");
        this.rfq_cumulative_chart = useRef("rfq_cumulative_chart");


		this.state = useState({
            projects : '',
            employees: "",
            stages: '',
        });

        onWillStart(async () => {
            await this.willStart();
        });

        onMounted(async () => {
            await this.mounted();
        });
    }


	/**
     * Event handler for the 'onWillStart' event.
     */
	async willStart() {
		await this.fetch_data();
	}


	 /**
     * Event handler for the 'onMounted' event.
     * Renders various components and charts after fetching data.
     */
	async mounted() {
		// Render other components after fetching data
		this.render_project();
		this.render_project_task();
		this.render_top_employees_graph();
		this.render_material_requisitions_status_graph();
        this.render_gantt_chart();
        this.render_rfq_cumulative_chart();
		this.render_filter();
	}


	/**
     * Render the project task chart.
     */
	async render_project_task() {
		var datas = await rpc("/project/task/count")
        var ctx = this.project_task_doughnut;
        const chart = new Chart(this.project_task_doughnut.el, {
            type: "doughnut",
            data: {
                labels: datas.project,
                datasets: [{
                    backgroundColor: datas.color,
                    data: datas.task
                }]
            },
            options: {
                legend: {
                    position: 'left'
                },
                cutoutPercentage: 40,
                responsive: true,
            }
        });
	}



	/**
	function for getting values to employee graph
	*/
	async render_top_employees_graph() {
		var ctx = this.top_selling_employees
		var arrays = await rpc('/employee/timesheet')
        var data = {
            labels: arrays[1],
            datasets: [{
                label: "Hours Spent",
                data: arrays[0],
                backgroundColor: [
                    "rgba(190, 27, 75,1)",
                    "rgba(31, 241, 91,1)",
                    "rgba(103, 23, 252,1)",
                    "rgba(158, 106, 198,1)",
                    "rgba(250, 217, 105,1)",
                    "rgba(255, 98, 31,1)",
                    "rgba(255, 31, 188,1)",
                    "rgba(75, 192, 192,1)",
                    "rgba(153, 102, 255,1)",
                    "rgba(10,20,30,1)"
                ],
                borderColor: [
                    "rgba(190, 27, 75, 0.2)",
                    "rgba(190, 223, 122, 0.2)",
                    "rgba(103, 23, 252, 0.2)",
                    "rgba(158, 106, 198, 0.2)",
                    "rgba(250, 217, 105, 0.2)",
                    "rgba(255, 98, 31, 0.2)",
                    "rgba(255, 31, 188, 0.2)",
                    "rgba(75, 192, 192, 0.2)",
                    "rgba(153, 102, 255, 0.2)",
                    "rgba(10,20,30,0.3)"
                ],
                borderWidth: 1
                },
            ]
        };
        //options
        var options = {
            responsive: true,
            title: {
                display: true,
                position: "top",
                text: " Time by Employees",
                fontSize: 18,
                fontColor: "#111"
            },
            legend: {
                display: false,
            },
            scales: {
                yAxes: [{
                    ticks: {
                        min: 0
                    }
                }]
            }
        };
        //create Chart class object
        var chart = new Chart(ctx.el, {
            type: 'bar',
            data: data,
            options: options
        });

	}


    // ///////////////////////////// By Elian  /////////////////////////////
    /**
     * Render the project chart.
     */
	async render_project() {
		var datas = await rpc("/project/count")
        var ctx = this.project_doughnut;
        const chart = new Chart(this.project_doughnut.el, {
            type: "doughnut",
            data: {
                labels: datas.labels,
                datasets: [{
                    backgroundColor: datas.colors,
                    data: datas.data
                }]
            },
            options: {
                responsive: true,
                cutoutPercentage: 70,
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    position: "left",
                    text: " Project Status Overview",
                    fontSize: 18,
                    fontColor: "#111"
                },


            }
        });
	}



	/**
	function for getting values to Material Requisitions Status graph
	*/
	async render_material_requisitions_status_graph() {
    const ctx = this.material_requisitions_status;
    const result = await rpc('/dashboard/material_requisition_data');

    const data = {
        labels: result.labels, // e.g., project names
        datasets: result.datasets // array of status datasets
    };

    const options = {
        responsive: true,
        title: {
            display: true,
            text: "Material Requisition Status Tracker",
            fontSize: 18
        },
        legend: {
            position: "top"
        },
        scales: {
            xAxes: [{
                stacked: false,
                scaleLabel: {
                    display: true,
                    labelString: "Projects"
                }
            }],
            yAxes: [{
                stacked: false,
                ticks: {
                    beginAtZero: true,
                    stepSize: 1
                },
                scaleLabel: {
                    display: true,
                    labelString: "Number of MRs"
                }
            }]
        }
    };

    new Chart(ctx.el, {
        type: 'bar',
        data: data,
        options: options
    });
}



	/**
     * Function for getting task gantt.
     */

    getXByDate(gantt, date) {
        const firstDate = gantt.dates[0];
        const diff = (new Date(date) - new Date(firstDate)) / (1000 * 60 * 60 * 24); // in days
        let pxPerDay = 38;

        if (gantt.options.view_mode === 'Month') pxPerDay = 120 / 30;

        return diff * pxPerDay + (gantt.options.padding || 18);
    }


    async render_gantt_chart() {
        const waitForGantt = () => new Promise(resolve => {
            const interval = setInterval(() => {
                if (window.Gantt) {
                    clearInterval(interval);
                    resolve();
                }
            }, 100);
        });

        await waitForGantt();

        // Fetch data
        const [tasks, stages] = await Promise.all([
            rpc('/dashboard/task_gantt_data'),
            rpc('/dashboard/task_stages')
        ]);

        // Dynamically map stage names to CSS classes
        const stageClassMap = {};
        stages.forEach((stage, index) => {
            stageClassMap[stage.name] = `stage-${index}`;
        });

        const today = new Date();

        const formatted = tasks.map(task => {
            const end = new Date(task.end);
            const isOverdue = end < today;
            const overdueDays = isOverdue ? Math.ceil((today - end) / (1000 * 60 * 60 * 24)) : 0;


            const stageName = task.stage_id?.name || '';
            const stageIndex = stages.findIndex(s => s.name === stageName);
            const stageClass = `stage-${stageIndex}`;


            const daysUntilDue = Math.ceil((end - today) / (1000 * 60 * 60 * 24));
            console.log('daysUntilDue:', daysUntilDue)
            let custom_class = '';
            if (end < today) {
                custom_class = 'bar-red';
            }
            else if (daysUntilDue <= 3) {
                custom_class = 'bar-yellow';
            }
            else {
                custom_class = 'bar-green';
            }

            return {
                id: String(task.id),
                name: task.name,
                start: task.start,
                end: task.end,
                progress: task.progress,
//                custom_class: isOverdue ? 'bar-overdue' : stageClass,
                custom_class: custom_class,
                dependencies: [],
                overdue: isOverdue,
                overdue_days: overdueDays,
                stage_id: task.stage_id,
                project_id: task.project_id,
            };
        });

        console.log(formatted.map(t => ({
          id: t.id,
          class: t.custom_class,
          overdue: t.overdue,
          stage: t.stage_id?.name
        })));

        // Create Gantt
        const gantt = new Gantt("#gantt_chart", formatted, {
            view_mode: 'Day',
            date_format: 'YYYY-MM-DD',
            custom_popup_html: function(task) {
                const real = task._bar?.task || task;
                const className = real.custom_class || '';

                // Dynamically set popup warning color to match bar class
                let color = '#51cf66'; // default green
                if (className.includes('bar-red')) color = '#ff4d4d';
                else if (className.includes('bar-yellow')) color = '#ffea00';
                else if (className.includes('bar-green')) color = '#51cf66';


                return `
                    <div class="details-container">
                        <h5 style="color: #00bfff;">${real.name}</h5>
                        <p><b>From:</b> ${real.start}</p>
                        <p><b>To:</b> ${real.end}</p>
                        ${real.stage_id ? `<p><b>Stage:</b> ${real.stage_id.name}</p>` : ''}
                        ${real.project_id ? `<p><b>Project:</b> ${real.project_id.name}</p>` : ''}
                        ${real.overdue ? `<p style="color:${color};"><b>⚠ Overdue by ${real.overdue_days} day${real.overdue_days > 1 ? 's' : ''}</b></p>` : ''}
                    </div>`;
            }

            });

        // Attach to DOM for reference
        document.querySelector('#gantt_chart').gantt = gantt;

        // Add "Today" vertical line
        setTimeout(() => {
            const ganttSvg = document.querySelector('#gantt_chart svg');
            const chart = ganttSvg?.querySelector('.grid');
            if (!ganttSvg || !chart) return;

            const today = new Date();
            const x = this.getXByDate(gantt, today);

            const height = chart.getBBox().height;

            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', x);
            line.setAttribute('x2', x);
            line.setAttribute('y1', 0);
            line.setAttribute('y2', height);
            line.setAttribute('stroke', '#ff0000');
            line.setAttribute('stroke-width', '2');
            line.setAttribute('stroke-dasharray', '4');

            ganttSvg.appendChild(line);
        }, 300);
    }


    async render_rfq_cumulative_chart() {
        try {
            const ctx = this.rfq_cumulative_chart;
            const result = await rpc('/dashboard/rfq_cumulative_data');

            if (!ctx.el || !result.labels.length || !result.data.length) {
                console.warn("Chart skipped: missing DOM or data.");
                return;
            }


            new Chart(ctx.el, {
                type: 'line',
                data: {
                    labels: result.labels,  // e.g., ['2024-01', '2024-02']
                    datasets: [{
                        label: 'RFQs Created from MRs',
                        data: result.data,
                        backgroundColor: result.color,
                        borderColor: result.color,
                        borderWidth: 2,
                        fill: false,
                        tension: 0.3,
                        pointRadius: 2
                    }]
                },
                options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                scales: {
                    x: {
                        type: 'category',
                        title: {
                            display: true,
                            text: 'Month'
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 0
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        },
                        title: {
                            display: true,
                            text: 'Cumulative RFQs'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true
                    },
                    title: {
                        display: true,
                        text: 'RFQs Created from Approved MRs (Cumulative)',
                        font: {
                            size: 18
                        }
                    }
                }
            }
            });


        } catch (error) {
            console.error("Error rendering cumulative RFQ chart:", error);
        }
    }




    // ///////////////////////////// End By Elian  /////////////////////////////


	/**
     * Function for getting RFQ.
     */


	/**
     * Function for getting employees for filter.
     */
	async render_filter() {
		var data = await rpc('/project/filter')
        this.state.projects = data[0]
        this.state.employees = data[1]
        this.state.stages = await rpc('/dashboard/task_stages');
	}


	/**
     * Event handler to apply filters based on user selections and update the dashboard data accordingly.
     */
	async _onchangeFilter(ev) {
		this.flag = 1
		var start_date = this.start_date.el.value;
		var end_date = this.end_date.el.value;
		var employee_selection = this.employee_selection.el.value;
		var project_selection = this.project_selection.el.value;
		if (!start_date) {
			start_date = "null"
		}
		if (!end_date) {
			end_date = "null"
		}
		if (!employee_selection) {
			employee_selection = "null"
		}
		if (!project_selection) {
			project_selection = "null"
		}
		var data = await rpc('/project/filter-apply', {
			'data': {
				'start_date': start_date,
				'end_date': end_date,
				'project': project_selection,
				'employee': employee_selection
			}
		})
        self.tot_hrs = data['list_hours_recorded']
        self.tot_employee = data['total_emp']
        self.tot_project = data['total_project']
        self.tot_task = data['total_task']
        self.tot_so = data['total_so']
        this.tot_project.el.innerHTML = data['total_project'].length
        this.tot_employee.el.innerHTML = data['total_emp'].length
        this.total_task.el.innerHTML = data['total_task'].length
        this.tot_hrs.el.innerHTML = data['hours_recorded']
        this.tot_margin.el.innerHTML = data['total_margin']
        this.total_so.el.innerHTML = data['total_so'].length
    }


	/**
	function for getting values when page is loaded
	*/
	fetch_data() {
		this.flag = 0
		var self = this;
		var def1 = rpc('/get/tiles/data').then(function(result) {
			if (result['flag'] == 1) {
				self.total_projects = result['total_projects']
				self.total_tasks = result['total_tasks']
				self.tot_task = result['total_tasks_ids']
				self.total_hours = result['total_hours']
				self.total_profitability = result['total_profitability']
				self.total_employees = result['total_employees']
				self.total_sale_orders = result['total_sale_orders']
				self.project_stage_list = result['project_stage_list']
				self.project_status_list = result['project_status_list']
				self.tot_so = result['sale_orders_ids']
				self.flag_user = result['flag']
				self.total_projects_ids = result['total_projects_ids']
			} else {
				self.tot_task = result['total_tasks_ids']
				self.total_projects = result['total_projects']
				self.total_tasks = result['total_tasks']
				self.total_hours = result['total_hours']
				self.total_sale_orders = result['total_sale_orders']
				self.project_stage_list = result['project_stage_list']
				self.project_status_list = result['project_status_list']
				self.flag_user = result['flag']
				self.tot_so = result['sale_orders_ids']
				self.total_projects_ids = result['total_projects_ids']
			}
		});
		/**
		function for getting values to hours table
		*/
		var def3 = rpc('/get/hours')
			.then(function(res) {
				self.hour_recorded = res['hour_recorded'];
				self.hour_recorde = res['hour_recorde'];
				self.billable_fix = res['billable_fix'];
				self.non_billable = res['non_billable'];
				self.total_hr = res['total_hr'];
			});
		var def4 = rpc('/get/task/data')
			.then(function(res) {
				self.task_data = res['project'];
			});
			return Promise.all([def1, def3, def4])
        .then(() => {
            console.log('All data has been fetched successfully.');
        })
        .catch((error) => {
            console.error('An error occurred while fetching data:', error);
        });
	}


	/**
     * Event handler to open a list of projects and display them to the user.
     */
	tot_projects(e) {
		e.stopPropagation();
		e.preventDefault();
		var options = {
			on_reverse_breadcrumb: this.on_reverse_breadcrumb,
		};
		if (this.flag == 0) {
			this.action.doAction({
				name: _t("Projects"),
				type: 'ir.actions.act_window',
				res_model: 'project.project',
				domain: [
					["id", "in", this.total_projects_ids]
				],
				view_mode: 'kanban,form',
				views: [
					[false, 'kanban'],
					[false, 'form']
				],
				target: 'current'
			}, options)
		} else {
			if (this.tot_project) {
				this.action.doAction({
					name: _t("Projects"),
					type: 'ir.actions.act_window',
					res_model: 'project.project',
					domain: [
						["id", "in", this.tot_project]
					],
					view_mode: 'kanban,form',
					views: [
						[false, 'kanban'],
						[false, 'form']
					],
					target: 'current'
				}, options)
			}
		}
	}


	/**
     * Event handler to open a list of tasks and display them to the user.
     */
	tot_tasks(e) {
		e.stopPropagation();
		e.preventDefault();
		var options = {
			on_reverse_breadcrumb: this.on_reverse_breadcrumb,
		};
		this.action.doAction({
			name: _t("Tasks"),
			type: 'ir.actions.act_window',
			res_model: 'project.task',
			domain: [
				["id", "in", this.tot_task]
			],
			view_mode: 'tree,kanban,form',
			views: [
				[false, 'list'],
				[false, 'form']
			],
			target: 'current'
		}, options)
	}


	/**
	for opening account analytic line view
	*/
	hr_recorded(e) {
		e.stopPropagation();
		e.preventDefault();
		var options = {
			on_reverse_breadcrumb: this.on_reverse_breadcrumb,
		};
		if (this.flag == 0) {
			this.action.doAction({
				name: _t("Timesheets"),
				type: 'ir.actions.act_window',
				res_model: 'account.analytic.line',
				view_mode: 'tree,form',
				views: [
					[false, 'list']
				],
				target: 'current'
			}, options)
		} else {
			if (this.tot_hrs) {
				this.action.doAction({
					name: _t("Timesheets"),
					type: 'ir.actions.act_window',
					res_model: 'account.analytic.line',
					domain: [
						["id", "in", this.tot_hrs]
					],
					view_mode: 'tree,form',
					views: [
						[false, 'list']
					],
					target: 'current'
				}, options)
			}
		}
	}


	/**
	for opening sale order view
	*/
	tot_sale(e) {
		e.stopPropagation();
		e.preventDefault();
		var options = {
			on_reverse_breadcrumb: this.on_reverse_breadcrumb,
		};
		this.action.doAction({
			name: _t("Sale Order"),
			type: 'ir.actions.act_window',
			res_model: 'sale.order',
			domain: [
				["id", "in", this.tot_so]
			],
			view_mode: 'tree,form',
			views: [
				[false, 'list'],
				[false, 'form']
			],
			target: 'current'
		}, options)
	}


	/**
     * Event handler to view a list of employees.
     * @param {Event} e - The click event.
     */
	tot_emp(e) {
		e.stopPropagation();
		e.preventDefault();
		var options = {
			on_reverse_breadcrumb: this.on_reverse_breadcrumb,
		};
		if (this.flag == 0) {
			this.action.doAction({
				name: _t("Employees"),
				type: 'ir.actions.act_window',
				res_model: 'hr.employee',
				view_mode: 'tree,form',
				views: [
					[false, 'list'],
					[false, 'form']
				],
				target: 'current'
			}, options)
		} else {
			this.action.doAction({
				name: _t("Employees"),
				type: 'ir.actions.act_window',
				res_model: 'hr.employee',
				domain: [
					["id", "in", this.tot_employee]
				],
				view_mode: 'tree,form',
				views: [
					[false, 'list'],
					[false, 'form']
				],
				target: 'current'
			}, options)

		}
	}


}

ProjectDashboardComponent.template = "ProjectDashboardTemp"
registry.category("actions").add("project_dashboard", ProjectDashboardComponent)
