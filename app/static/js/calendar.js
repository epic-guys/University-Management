const Calendar = require('@toast-ui/calendar');
require('@toast-ui/calendar/dist/toastui-calendar.min.css');


var Calendar = window.tui.Calendar;

      var cal = new Calendar('#app', {
        defaultView: 'month',
        calendars: MOCK_CALENDARS,
      });