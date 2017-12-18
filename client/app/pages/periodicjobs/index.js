import { reduce, extend } from 'underscore';
import template from './periodicjobs.html';


const cronTriggerRegex = {
  yearRegex: '^((\\*)|\\d{4,4})$',
  monthRegex: '^((\\*)|(0?\\d{1,1})|(1[0-2]))$',
  dayRegex: '^((\\*)|(\\d{1,1})|([0-2]\\d{1,1})|(3[01]))$',
  hourRegex: '^((\\*)|(\\d{1,1})|([0-1]\\d{1,1})|(2[0-3]))$',
  minuteRegex: '^((\\*)|(\\d{1,1})|([0-5]\\d{1,1}))$',
  secondRegex: '^((\\*)|(\\d{1,1})|([0-5]\\d{1,1}))$',
};

function SchedulePeriodicJobCtrl($routeParams, $location, PeriodicJob, Query, toastr) {
  this.jobId = $routeParams.jobId;
  this.triggerRegex = cronTriggerRegex;

  if (this.jobId === 'new') {
    this.periodicJob = new PeriodicJob();
    this.queryParams = [];
  } else {
    this.periodicJob = PeriodicJob.get({ id: this.jobId }, (periodicjob) => {
      this.triggerParams = periodicjob.task.trigger_params;
      this.queryParams = this.objectToListQueryParams(periodicjob.task.kwargs);
      this.isRunning = periodicjob.task.isRunning;
    });
  }

  Query.options({ minimal: true }, (queries) => {
    this.queryOptions = queries;
  });

  this.triggerName = 'cron';

  // Interval, Date triggers
  this.triggers = ['cron'];
  this.paramTypes = ['String', 'Integer', 'Time'];

  this.objectToListQueryParams = (args) => {
    return Object.keys(args).reduce((acc, cur) => {
      acc.push({ name: cur, val: args[cur] });
      return acc;
    }, []);
  };

  this.listToObjectQueryParams = (args) => {
    return reduce(
      args,
      (a, b) => {
        const d = Object();
        d[b.name] = b.val;
        return extend(a, d);
      },
      {},
    );
  };

  this.addQueryParams = () => {
    this.queryParams.push({ name: '', val: '' });
  };

  this.dataTypes = ['string', 'number', 'Date'];

  this.submit = () => {
    this.periodicJob.queryparams = this.listToObjectQueryParams(this.queryParams);
    this.periodicJob.trigger = this.triggerName;
    this.periodicJob.triggerparams = this.triggerParams;
    this.periodicJob.$scheduleJob(
      (periodicjob) => {
        toastr.success('Job Scheduled.');
        if (this.jobId === 'new') {
          $location.path(`/periodicjobs/${periodicjob.id}`).replace();
        }
      },
      () => {
        toastr.error('Failed saving alert.');
      },
    );
  };

  this.pause = () => {
    PeriodicJob.pause(
      {
        pause: true,
        id: this.jobId,
      },
      (periodicjob) => {
        toastr.success('Paused.');
        this.periodicJob = periodicjob;
        $location.path(`/periodicjobs/${periodicjob.id}`).replace();
      },
    );
  };

  this.resume = () => {
    PeriodicJob.resume(
      {
        resume: true,
        id: this.jobId,
      },
      (periodicjob) => {
        toastr.success('Resumed');
        this.periodicJob = periodicjob;
        $location.path(`/periodicjobs/${periodicjob.id}`).replace();
      },
    );
  };

  this.closeDialog = () => {
    $location.path('/periodicjobs').replace();
  };
}

export default function init(ngModule) {
  ngModule.component('schedulePeriodicJobPage', {
    template,
    controller: SchedulePeriodicJobCtrl,
  });

  return {
    '/periodicjobs/:jobId': {
      template: '<schedule-periodic-job-page></schedule-periodic-job-page>',
      title: 'Schedule Periodic Job',
    },
  };
}
