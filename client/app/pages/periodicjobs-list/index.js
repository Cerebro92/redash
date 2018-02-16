import { Paginator } from '@/lib/pagination';
import template from './periodicjobs-list.html';


const stateClass = {
  true: 'label label-success',
  false: 'label label-danger',
};

class PeriodicJobListCtrl {
  constructor(PeriodicJob) {
    this.periodicjobs = new Paginator([], { itemsPerPage: 100 });
    PeriodicJob.query((periodicjobs) => {
      this.periodicjobs.updateRows(periodicjobs.map(periodicjob => ({
        name: periodicjob.name,
        user: periodicjob.user,
        status: periodicjob.task.is_running ? 'RUNNING' : 'STOPPED',
        class: stateClass[periodicjob.task.is_running],
        id: periodicjob.id,
        created_at: periodicjob.created_at,
      })));
    });
  }
}

export default function init(ngModule) {
  ngModule.component('jobsListPage', {
    template,
    controller: PeriodicJobListCtrl,
  });

  return {
    '/periodicjobs': {
      template: '<jobs-list-page></jobs-list-page>',
      title: 'Period Jobs',
    },
  };
}
