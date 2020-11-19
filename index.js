
var Blynk = require('blynk-library');

var AUTH = 'goHQikL3hfv-uYQcrgAl0iFkM5_0Y_uZ';

var blynk = new Blynk.Blynk(AUTH);

var v1 = new blynk.VirtualPin(1);
var v9 = new blynk.VirtualPin(11);

v1.on('write', function(param) {
  console.log('V1:', param[0]);
});

v9.on('read', function() {
  v9.write(25.09);
});

var term = new blynk.WidgetTerminal(6);
term.on('write', function(data) {
  	term.write('Time        Sys Timer   Temp        Buzzer');
	term.write('21:17:09    00:00:00    22.83 C     *');
	term.write('21:17:14    00:00:05    23.48 C');
	term.write('21:17:19    00:00:10    23.80 C');
	term.write('21:17:24    00:00:15    23.16 C');
	term.write('21:17:29    00:00:20    22.83 C');
	term.write('21:17:34    00:00:25    24.44 C     *');
	term.write('21:17:40    00:00:31    23.48 C');
	term.write('21:17:45    00:00:36    22.51 C');
	term.write('21:17:50    00:00:41    23.16 C');
	term.write('21:18:00    00:00:51    24.44 C');

	term.write('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n');
	term.write('The logging has stopped..\nPress power button to continue sampling');

	term.write('Time        Sys Timer   Temp        Buzzer');
	term.write('22:10:57    00:00:00    24.44 C     *');
	term.write('22:11:02    00:00:05    23.80 C');
	term.write('22:11:07    00:00:10    22.83 C');
	term.write('22:11:12    00:00:15    23.16 C');
	term.write('22:11:17    00:00:20    22.83 C');
	term.write('22:11:22    00:00:25    23.16 C     *');
	term.write('22:11:27    00:00:30    22.83 C');
	term.write('22:11:32    00:00:35    22.83 C');
	term.write('22:11:37    00:00:40    23.16 C');
	term.write('22:11:42    00:00:45    22.83 C');
	term.write('22:11:47    00:00:50    22.83 C     *');
	term.write('22:11:52    00:00:55    23.16 C');

	term.write('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n');

	term.write('Time        Sys Timer   Temp        Buzzer');
	term.write('22:30:43    00:00:00    24.44 C     *');
	term.write('22:30:48    00:00:05    25.41 C');
	term.write('22:30:53    00:00:10    24.44 C');
	term.write('22:30:55    00:00:00    26.38 C');
	term.write('22:31:05    00:00:10    24.77 C');
	term.write('22:31:15    00:00:20    24.77 C     *');
	term.write('22:31:17    00:00:00    26.38 C');
	term.write('22:31:19    00:00:02    26.06 C');
	term.write('22:31:21    00:00:04    24.77 C');
	term.write('22:31:23    00:00:06    25.09 C');


});
