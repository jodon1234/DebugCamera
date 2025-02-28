1.	Connect camera to power using the 24v m12 connector on the side of the camera or using the USB C power supply included.
2.	Upon powering up a window should appear asking you for your trigger type.
  a.	Ethernet: Select this for use with the Debug_Camera AOI, the cam must be connected to the corporate network over wifi or ethernet.
  b.	External: Select this for a hard wire trigger through the male 5 pin connector (Only works with 24v power supply connected to the male 5 pin connector)
  c.	Internal: Select this for when a PLC trigger is not possible. Connect a sensor or switch to the female 5 pin connector. (Only works with 24v power supply connected to the male 5 pin connector)
3.	If using Ethernet trigger, enter the corporate IP address of the PLC you wish to connect to.
4.	Enter a value into the Pre Trigger time box, this defines the amount of time before the trigger that will be recorded.
5.	Press the done button and a video preview window should appear.
6.	To view the saved videos navigate to the /home/admin folder, files should be labeled with the date and time they were saved. This can be done on the camera display or over the network with SFTP, login is User: admin Pass : password
7.	If the preview window closes shortly after it opens that indicates an error and the application has crashed, the most likely cause of this is a failure to connect to the PLC, make sure the camera is connected to the corporate network.
8.	If you notice a lightning bolt symbol in the top right corner of the screen you may be using a power supply that can’t supply enough power, it is recommended you use the one supplied with the camera.
9.	If you have any questions feel free to contact me jordan.shrauger@gentex.com


Note: AOI available in the /home/admin/ folder
