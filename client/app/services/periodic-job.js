function PeriodicJob($resource, $http) {
  const actions = {
    save: {
      method: 'POST',
      transformRequest: [(data) => {
        const newData = Object.assign({}, data);
        if (newData.query_id === undefined) {
          newData.query_id = newData.query.id;
          newData.destination_id = newData.destinations;
          delete newData.query;
          delete newData.destinations;
        }

        return newData;
      }].concat($http.defaults.transformRequest),
    },
    scheduleJob: {
      method: 'POST',
      url: '/api/periodicjobs/:id',
      params: { id: '@id' },
    },
    pause: {
      method: 'post',
      url: '/api/periodicjobs/:id',
      params: { id: '@id' },
    },
    resume: {
      method: 'post',
      url: '/api/periodicjobs/:id',
      params: { id: '@id' },
    },
  };
  const resource = $resource('api/periodicjobs/:id', { id: '@id' }, actions);
  return resource;
}

export default function init(ngModule) {
  ngModule.factory('PeriodicJob', PeriodicJob);
}
