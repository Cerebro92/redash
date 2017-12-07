import { has, reduce, extend, map } from 'underscore';
import template from './periodictasks.html';

function ScheduleJobCtrl($routeParams, $location, PeriodicTask, toastr) {
  this.taskId = $routeParams.taskId;

  if (this.taskId == 'new') {
    this.periodictask = new PeriodicTask();
    this.periodictask.trigger_params = {second: '*', minute: '*', hour: '*'};
  } else {
      this.periodictask = PeriodicTask.get({ id: this.taskId}, (periodictask) => {
      this.isCronEnable = periodictask.trigger === 'cron';
      this.args = periodictask.task_params;
      this.is_running = periodictask.is_running
      delete periodictask.task_params;
      delete periodictask.is_running;
    });
  }

  this.triggers = ['cron', 'interval', 'date'];
  this.paramTypes = ['String', 'Integer', 'Time'];

  this.showCronTimings = () => {
    this.isCronEnable = this.periodictask.trigger === 'cron';
  };
  this.args = [];

  this.getArgs = (args) => {
    return map(args, {})
  }
  this.addArgs = () => {
    this.args.push({ name: '', value: '' });
  };

  this.cleanArgs = (args) => {
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

  this.dataTypes = ['string', 'number', 'Date'];

  this.submit = () => {
    PeriodicTask.scheduleJob({
      periodictask: this.periodictask,
      queryparams: this.cleanArgs(this.args)
    }, (periodictask) => {
        toastr.success('Job Scheduled.');
        if (this.taskId === 'new') {
          $location.path(`/periodictasks`).replace();
        }
    });
  }

  this.pause = () => {
    PeriodicTask.pause({
      pause: true,
      id: this.taskId,
    },
    (res) => {
      toastr.success('Paused.');
      $location.path(`/periodictasks`).replace();
    });
  }

  this.resume = () => {
    PeriodicTask.resume({
      resume: true,
      id: this.taskId
    },
    (res) => {
      toastr.success('Resumed');
      $location.path(`/periodictasks`).replace();
    });
  }

  this.closeDialog = () => {
    $location.path(`/periodictasks`).replace();
  }

}

export default function init(ngModule) {
  ngModule.component('scheduleJobPage', {
    template,
    controller: ScheduleJobCtrl,
  });

  return {
    '/periodictasks/:taskId': {
      template: '<schedule-job-page></schedule-job-page>',
      title: 'Schedule Periodic Task',
    },
  };
}
