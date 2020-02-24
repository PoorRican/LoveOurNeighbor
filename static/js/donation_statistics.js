const f_str = 'MM DD, YYYY';    // Constant for date formatting
let dates = [];                 // label field to use for storing dates

// Top-Level Wrapper function that fetches data and draws URL
function drawGraph(objJsonURL, donationJsonURL) {
  $.getJSON(objJsonURL,
    function (data) {
      let campaign = data;
      let start_date = moment(campaign.start_date);
      buildGraph(donationJsonURL);
    }
  );
}

function buildGraph(donationJsonUrl) {
  $.getJSON(donationJsonUrl,
    function (data) {
      let donations = data['donations'];
      console.log(donations);
      let temp = buildDatasets(data['donations']);

      console.log(temp);
      initGraph(temp.labels, temp.datasets);
    }
  );
}

function buildDatasets(donations) {
  // Calculate $ per day
  let labels = [];
  let amounts = {};
  for (let i = 0; i < donations.length; i++) {
    let _date = moment(donations[i].payment_date).format(f_str);
    if (!amounts.hasOwnProperty(_date)) {
      amounts[_date] = 0;
    }
    amounts[_date] += donations[i].amount;
  }
  amounts = sortDict(amounts);
  labels = Object.keys(amounts);
  amounts = Object.values(amounts);

  // Calculate donations per day
  let count = {};
  for (let i = 0; i < donations.length; i++) {
    let _date = moment(donations[i].payment_date).format(f_str);
    if (!count.hasOwnProperty(_date)) {
      count[_date] = 0;
    }
    count[_date] += 1;
  }
  count = Object.values(sortDict(count));

  return {
    'labels': labels,
    'datasets': [
      {'label': '$ per day', 'data': amounts},
      {'label': 'Donations per Day', 'data': count}
    ]
  }
}

function sortDict(dict) {
  let keys = Object.keys(dict);
  keys.sort();

  let temp = {};
  for (let i = 0; i < keys.length; i++) {
    temp[keys[i]] = dict[keys[i]];
  }

  return temp;
}

// Takes a given date and finds an appropriate resolution to fit within a window
// This is used to determine the scale of the
function findResolution(_date, min = 10) {
  let resolution = -1;
  let units = 0;
  const resolutions = ['days', 'weeks', 'months'];

  do {
    resolution += 1;
    units = moment().diff(_date, resolutions[resolution])
  } while (units > min);

  return resolutions[resolution];
}

// Returns an Array of moment.js Date objects from days from _date to today
function getArrayOfDates(_date) {
  let dates = [];
  let i = -1;

  do {
    dates.concat(_date.add(++i, 'day').format(f_str));
  } while (_date.add(i, 'day').format(f_str) !== moment().format(f_str));

  return dates;
}

function initGraph(labels, datasets) {
  let ctx = document.getElementById('donation-graph');
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: datasets
    },
    options: {
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true
          }
        }]
      }
    }
  });
}
