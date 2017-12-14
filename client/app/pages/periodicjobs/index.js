import { reduce, extend } from 'underscore';
import template from './periodicjobs.html';


const cronTriggerRegex = {
  yearRegex: '^((\\*)|\\d{4})$',
  monthRegex: '^((\\*)|(0?[1-9])|(1[0-2]))$',
  dayRegex: '^((\\*)|(0?[1-9])|([12](\\d))|(3[01]))$',
  hourRegex: '^((\\*)|(0?\\d|1\\d+)|(2[0-3]))$',
  minuteRegex: '^((\\*)|(0?\\d)|([1-5]\\d))$',
  secondRegex: '^((\\*)|(\\d{1,1})|([0-5]\\d{1,1}))$',
};

function SchedulePeriodicJobCtrl($routeParams, $location, PeriodicJob, toastr) {
  this.jobId = $routeParams.jobId;

  if (this.jobId === 'new') {
    this.periodicJob = new PeriodicJob();
    this.triggerRegex = cronTriggerRegex;
    this.queryParams = [];
  } else {
    this.periodicJob = PeriodicJob.get({ id: this.jobId }, (periodicjob) => {
      this.triggerParams = periodicjob.task.trigger_params;
      this.queryParams = this.objectToListQueryParams(periodicjob.task.kwargs);
      this.isRunning = periodicjob.task.isRunning;
    });
  }

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
