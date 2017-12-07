import { Paginator } from '@/lib/pagination';
import template from './periodictasks-list.html';


const stateClass = {
  true: 'label label-success',
  false: 'label label-danger',
};

class PeriodicTaskListCtrl {
	constructor(PeriodicTask) {
		this.periodictasks = new Paginator([], { itemsPerPage: 20 });
		PeriodicTask.query((periodictasks) => {
			this.periodictasks.updateRows(periodictasks.map(periodictask => ({
				name: periodictask.task_name,
				user: periodictask.user,
				status: periodictask.is_running?'RUNNING': 'STOPPED',
				class: stateClass[periodictask.is_running],
				id: periodictask.id,
				created_at: periodictask.created_at,
			})));
		});
	}
}

export default function init(ngModule) {
	ngModule.component('jobsListPage', {
		template,
		controller: PeriodicTaskListCtrl
	});

	return {
		'/periodictasks': {
			template: '<jobs-list-page></jobs-list-page>',
			title: 'Jobs',
		}
	}
}