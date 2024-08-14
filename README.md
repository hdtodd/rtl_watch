# rtl\_watch: Real-time rtl\_433 monitor v4.0.0
## Catalog and characterize ISM devices using rtl\_433

`rtl_watch` monitors output from `rtl_433` to display, in real time, the characteristics of the ISM-band devices broadcasting in your neighborhood.

`rtl_watch` can help you understand the ISM environment in your neighborhood by cataloging devices near you that are broadcasting on the ISM band (433MHz in the US).  The values provided by `rtl_watch` for the device signal characteristics over a number of readings may help you identify devices that are close to your location and/or new devices in your neighborhood.
<img width="1589" alt="rtl_watch-v3-0" src="https://github.com/user-attachments/assets/ac6b40d6-4cc9-421f-96f8-79c65ff4d78e">

## Use

If your system already has the required components, the command `./rtl_watch` is all that's needed to begin monitoring.  `./rtl_watch` starts the program and  prompts for the name of the `rtl_433` host on your local area network that provides either MQTT or HTTP subscription service.  `./rtl_watch -H <hostname>` starts the program without the prompt and connects to the `rtl_433` service via MQTT.  To connect via HTTP to that service, add `-S HTTP` to the command line.

The program opens a scrollable, resizable display window with a table with columns that characterize the signals from the devices observed by your `rtl_433` system; it appends to the table new remote devices and associated data as they are observed by the `rtl_433` host system; and it updates subsequent readings as they are reported.

`./rtl_watch -h` provides more information about command-line options.  Additional configuration options are described in a later section.

## The Display Window

The display window is divided into several sections:

### The Upper Information Section
This section provides general information about the monitoring process.  It indicates:

1. the network protocol (HTTP or MQTT) used for the connection;
1. the `rtl_433` host that it is monitoring;
2. the `rtl_433` port that it is connected through;
1. the total number of packets received (many of which are duplicates since devices may send multiple packets for a single observation);
1. the total number of tranmissions received (de-duplicated packets);
1. the date and time of the earliest and latest transmission observed.

### The Lower Information Section
This section is the table of characteristics of the signals observed from each device:

1. the device name, which is a concatenated string of "device model"/"channel"/"device id", as observed and reported by `rtl_433`;
1. warning flags observed from the device (see below);
1. the count of packets observed from each device;
1. the count of transmissions (de-duplicated packets) observed from each device;
1. the mean and standard deviation of the signal-to-noise ratio (SNR) of the transmissions observed from each device, as reported by `rtl_433`;
1. the mean and standard deviation of the frequencies of the transmissions observed from each device, as reported by `rtl_433`;
1. the mean and standard deviation of the inter-transmission gap times (ITGT) between transmissions from each device;
1. the mean and standard deviation of the number of packets per transmission (PPT) from each device.

>[!NOTE]
>ITGT and PPT statistics *lag one transmission behind readings*, since the past transmission isn't recognized until a new one begins.

### The Control Buttons
This section is located just below the title bar and provides the following controls for program operation:

1. **Sort Device** sorts the table entries in alphabetical order by device name.
1. **Sort Count** sorts the table entries in decreasing order of packet counts.  This may help identify the most active devices in your neighborhood.
1. **Sort SNR** sorts the table entries in decreasing order of SNR (signal-to-noise ratio values).  This may help identify the devices that are closest to your RTL-SDR receiver.
1. **Heading Info** pops up a window to describe the table column contents.
1. **Reset Warn**  clears the warning flags for all devices (see below).
1. **Print Summary** appends to the file "rtl_watch.prn", in the directory of the controlling console, the contents of the table, sorted in alphabetical order by the device name/chnl/id string.
1. **Togl** toggles the display window between full screen and reduced size.
1. **Quit** exits the program.  (CNTL-C in the controlling terminal window also works) 

Data collection continues until you press the **Quit** button or type the \<CNTL-C\> character on the controlling keyboard.

### Warning Flags

`rtl_watch` monitors packets decoded by `rtl_433` for two signals that might indicate that maintenance of a remote sensor is needed:

1. *Battery Low* is indicated by "!!" in the warning flags column.  Though not universally standard, devices generally indicate an impending low-battery condition by changing the `battery_low` flag from 1 to 0 in its broadcast packets.  *Any* occurence of `battery_low` = 0 causes `rtl_watch` to post the "!!" warning flag for that device.  That flag is sticky: the warning flag remains, even if `battery_low` returns to 1, since the battery voltage may be fluctuating with ambient temperature and the device may need attention in any case.
1. *Status Change* is indicated by "?!" in the warning flags column.  The remote-device status field is not present in the packets for all devices and is not standardized.  But a change in status may indicate that the device needs attention and so is flagged.  The "Status Change" flag is also sticky: once set for a device, it remains set despite any subsequent changes in packet status field values.

*Battery Low* takes precedence over *Status Change*, so only "!!" will be displayed if the battery-low flag has been seen even if a status-change has occurred.

The **Reset Warn** button clears both the battery-low and status-change flags for *all* devices.  If warning flags reappear after a reset, they are due to new warning conditions appearing for the device.

### Using the Information

The information from `rtl_watch` can be helpful in several ways to understand your ISM neighborhood:

1.  Which devices are closest to you?  High values of SNR mean (e.g., 15-20) may indicate that the device is close to your RTL-SDR receiver.  Also, high values for packet or transmit count likely indicate a device close to your receiver, as their packets are received routinely, relative to those with low counts (but check correlation with ITGT and PPT).
1.  Which devices may either be remote or experiencing interference from other devices?  A high standard deviation value for ITGT (inter-transmission gap time) or PPT (packets per transmission) indicate that the transmitting device's packets are not being received routinely.  That could be because of interference from other devices (which prevent the packets from being decoded correctly) or because the device is remote from your receiver (check for correlation with SNR mean and standard deviation).
1.  Which devices have unreliable oscillators?  A high value for frequency standard deviation likely indicate an unstable (possibly older) device clock.

## Installing `rtl_watch`

`rtl_watch` is a Python3 program.  It requires that the Python packages `tkinter` and `paho-mqtt` be installed on the computer on which `rtl_watch` is invoked.  `rtl_watch` has been tested on Mac OSX Catalina and Sonoma and Raspbian Bullseye and Bookworm. On Mac OSX, you may need to install Python3 if you haven't already done so ( <https://www.python.org/downloads/macos/> ).

To install, connect to an appropriate directory for downloading code and issue the command
   `git clone http://github.com/hdtodd/rtl_watch`
then `cd rtl_watch` and `./rtl_watch` to run the program.  See below for command-line options.

>[!NOTE]
>Paho-MQTT v2 broke v1 callback invocations, but v3 of `rtl_watch` incorporates a workaround so that it will operate with either v1.x or v2.x of Paho-MQTT.  However, invocation on a system running v2.x will generate a warning, since `rtl_watch` continues to use the deprecated v1-style callback invocation for now.  `check_paho_vers` is included in this distribution: executing it will tell you which version you're running.

`rtl_watch` requires that a computer (the "monitoring computer") on your local-area network be running `rtl_433` and re-broadcasting the ISM packets it recognizes as JSON messages via either the `http` or `mqtt` protocol on the local-area network.  See instructions below if you do not have an `rtl_433` system set up or if it has not been set up to re-broadcast packets via MQTT or HTTP..

## Using `rtl_watch`

### Command-line Options

The following options may be provided on the command line to provide parameters and manage program operation:

*  \[`-h` | `--help`\]  
   Describes the command-line options
*  \[`-S` | `--source`\] `\[HTTP | MQTT\]`
   Connect to the `rtl_433` service via HTTP or MQTT protocol (default MQTT)
*  \[`-H` | `--host`\] `<MQTT Broker host name (string)>`  
   Identify the MQTT broker on your local-area network that is publishing `rtl_433` packet infomation in JSON format
*  \[`-T` | `--topic`\] `<MQTT Broker rtl_433 topic (string)>`  
   Identify the rtl_433 topic as it is being broadcast by the MQTT broker
*  \[`-U` | `--username`\] `<MQTT Broker rtl_433 username (string)>`  
   *Only needed if broker is secured*:  Username needed to access the MQTT broker
*  \[`-P` | `--password`\] `<MQTT Broker rtl_433 password>`  
   *Only needed if broker is secured*: Password  needed to access the MQTT broker
*  \[`-p` | `--port`\] `<`rtl_433` service MQTT publishing port or HTTP stream port (integer)>`  
   *Only needed if modified on the server from the default 1883 for MQTT or 8433 for HTTP)*:  Specifies the port the rtl_433 service is using to broadcast rtl_433 messages 
*  \[`-x` | `--exclude_noise`\] `<noise threshhold (integer)>`  
   Don't display devices with fewer than \<threshhold\> packets seen
*  \[`-w` | `--xmit_window`\] `<max transmission time (float, in sec)>`  
   Devices generally send multiple packets in hope that one will be received ungarbled; this sets the maximum time for packets from one device to be considered to be the transmission of a single observation.  Default: 2.0 seconds.
*  \[`-t` | `--TPMS`\]  
   Enable display of tire pressure monitoring system observations.  In areas with heavy automobile traffic, a significant number of tire-pressure monitor system (TPMS) readings, many just one transmission, will be observed and clutter the table.  By default, TPMS observations are **not displayed**.  This option will enable their display.
*  \[`-o` | `--omit`\] `[ SNR &| Freq &| ITGT &| PPT ]`  
   Omit any combination of the signal analysis data from the display table
*  \[`-d` | `--debug`\]  
   Print debugging information on the controlling console
*  \[`-W` | `--warn`\]  
   Inject warning notations at packets 20 and 40 to verify operation; requires `-d` option also enabled
*  \[`-v` | `--version`\]  
   Displays the version of rtl_watch.

### Providing the `rtl_433` server hostname

`rtl_watch` requires the identity of the `rtl_433` server to which it should connect for MQTT subscription or HTTP streaming.  You can specifiy that hostname (or IP address) on the command line with the `-H` option.  If not provided on the command line or environment, `rtl_watch` prompts for the hostname and assumes the default port 8433.

For HTTP service, only the hostname is needed to start operation (unless the streaming port is not 8433).

The HTTP hostname and port may also be specified by environment variables `HTTP_HOST` and `HTTP_PORT`.  The environment values are overridden by command-line values if they're provided.

### Providing MQTT Parameters (if using MQTT protocol)

If you're using MQTT protocol, `rtl_watch` requires additional information about the `rtl_433` MQTT publishing host:

*  MQTT topic (default "rtl\_433/+/events")
*  MQTT login username [if MQTT is secured] 
*  MQTT login password [if MQTT is secured] 
*  host MQTT port [if the MQTT port is not the 1883 standard]

All but the host name are set to default values and may not need to be provided or changed.  But if your `rtl_433` host MQTT broker parameters are set differently, these parameters may be provided in four different ways.  In decreasing order of precedence:

1.  Command line switches [-H, -T, -U,-P, -p] override all other sources to specify HOST, TOPIC, USER, PASSWORD, or PORT, respectively.
2.  These environment variables override internal variable assignments and avoid prompting:
  *  MQTT\_HOST
  *  MQTT\_TOPIC (defaults to "rtl\_433/+/events" if not specified and not provided on command line)
  *  MQTT\_USER (defaults to \"\" if not specified and not provided on command line)
  *  MQTT\_PASSWORD (defaults to \"\" if not specified and not provided on command line)
  *  MQTT\_PORT (defaults to 1883 if not specified and not provided on command line).
3.  The required parameter values can be assigned within the program source code.   Default values are  set near the beginning of the `rtl_watch` source code.
4. If not specified on command line, provided via environment, or set as internal variable assignments in the Python source code, the program prompts for HOST and assigns defaults to TOPIC, USER, PASSWORD, and PORT.

## [If Needed] Installing and Configuring The Monitoring Computer

These instructions are for a Linux system.  It should be possible to install the monitoring system on OSX as well since the software
 components of the monitoring system are available for Mac (not tried -- use `brew` or `port` to install the MQTT component).

Perform these steps on the computer you intend to use to monitor the ISM-band radio signals.

1. If you don't already have one, purchase an RTL-SDR receiver.  Use your favorite search engine to search for "rtl sdr receiver".  They cost about $30US.  But be sure to get one with an antenna appropriate for your region's ISM frequency band.  Then you simply plug it in to a USB port on your monitoring computer.
1. If you're not sure of the frequency of ISM bands in use in your location, use a tool such as `CubicSDR` (https://cubicsdr.com/) to observe the various ISM bands and discover which ones have activity in your region.  Set the frequency in `rtl_433` (below) accordingly.
1. Install mosquitto: `sudo apt-get install mosquitto mosquitto-client`.  The broker will be started by `systemd` and will be restarted whenever the system is rebooted.
1. Connect to a download directory on your monitoring computer and use `git` to install `rtl_433`: `git clone https://github.com/merbanan/rtl_433`.
1. Connect to the installed rtl\_433 directory and follow the instructions in `./docs/BUILDING.md`to build and install the rtl\_433 program. **Be sure to install the prerequisite programs needed by rtl_433 before starting `cmake`.**  
1. **INITIAL TEST** Following the build and install, you can simply invoke `sudo /usr/local/bin/rtl_433` to verify that it starts up, finds the RTL_SDR dongle, and identifies ISM packets.  You may need to adjust the frequency via command line, e.g.,  `-f 315M`, if you're not in the US.
1. `rtl_433` is a *very* sophisticated program with *many* options, and you may want to explore its use by reading through the help message or browsing the configuration file.  But for regular operation, it's easiest to create the configuration file and, once it's working as you want it to, add `rtl_433` as a system service following instructions:
   * `cp /usr/local/etc/rtl_433/rtl_433.example.conf /usr/local/etc/rtl_433/rtl_433.conf`
   * Edit `/usr/local/etc/rtl_433/rtl_433.conf`:
     * If your regional ISM band is not 433.92MHz, set the correct frequency in the "frequency" entry.
     * Under **Analyze/Debug options**, comment out stats reporting: `#report_meta stats`
     * If you plan to use HTTP as your streaming option, under **Data output options**, add `output http`.
     * If you plan to use MQTT as your publishing option, under **Data output options**, add `output mqtt`.
     * Under **Data output options**, add `output json:/var/log/rtl_433/rtl_433.json` to tell `rtl_433` to log received packets to a log file in case you want to do subsequent analysis of devices in your neighborhood.  More options for HTTP streaming and MQTT publishing service are available, but this will get you started.
     *Create the directory for that log file: `sudo mkdir /var/log/rtl_433`
1. **PRODUCTION TEST** Now `sudo /usr/local/bin/rtl_433` from the command line of one terminal screen on the monitoring computer.  From the command line of another terminal screen on that computer, or from another computer with mosquitto client installed, type `mosquitto_sub -h <monitorhost> -t "rtl_433/<monitorhost>/events"`, where you substitute your monitoring computer's hostname for "\<monitorhost\>".  If you have ISM-band traffic in your neighborhood, and if you've tuned `rtl_433` to the correct frequency, you should be seeing the JSON-format records of packets received by the RTL\_SDR dongle.  If you don't, first verify that you can publish to `mosquitto` on that monitoring computer and receive via a client (use the native `mosquitto_pub` and `mosquitto_sub` commands).  If `mosquitto` is functioning correctly, check that the rtl\_433 configuration file specifies mqtt output correctly.
1. Finally, install the rtl_433 monitor as a service:
  * `sudo cp rtl_433.service /etc/systemd/system/` to copy the .service file from this download directory (where this README file is located) into the systemd directory
  * `sudo systemctl enable rtl_433` and `sudo systemctl start rtl_433` to enable and start the service
  * Now, whenever the monitoring system is rebooted, it will restart the rtl_433 service and the mqtt service needed to broadcast in JSON format the information received by the RTL\_433 dongle as ISM packets.

The JSON log file grows quickly, so you will, over time, need to remove the JSON log file on the monitoring computer (`/var/log/rtl_433/rtl_433.json`).  Or you may want to use `logrotate` to manage those JSON files, in which case you could `sudo mv rtl_433.logrotate /etc/logrotate.d/rtl_433` on the host monitoring system to compress and manage the log files.

The developers of `rtl_433` continually update the list of devices that the program recognizes, so connect to the `rtl_433` download directory, `git pull`, re-build, and re-install `rtl_433` periodically to add recognition of new devices in your neighborhood.
 
## Known Issues

The current version of Python Paho-MQTT is v2 on MacOS Sonoma with Python v3.12.4, and it is v1.6 on RaspiOS 6.6 Bookworm with Python v3.11.2 as installed with apt-get/pip3.  Paho-MQTT v2 broke the callback invocation for v1.  `rtl_watch` has a workaround (invokes v1 compatibility on a v2 system), but v2 issues a deprecation warning.  `rtl_watch` will be updated to use v2 invocation when the RaspiOS Paho-MQTT library has been updated to v2.

When using HTTP streaming as the connection protocol, there may be a delay between pressing the Quit button and actual termination of the program as threads terminate themselves.

>[!NOTE]
>`rtl_watch` uses message queuing between process threads to buffer message processing and window updating from packet collection.  It has not been tested on  a single-core system in a high-traffic location and may not be able to respond well in that environment.  If you notice problems, please report them to the author with details about the system on which you're running `rtl_watch`.

## Related Tools
These related `rtl_433` tools might also be helpful:

* [`rtl_snr`](https://github.com/hdtodd/rtl_snr): Analyzes the JSON logs on the system that runs `rtl_433` to catalog the devices seen and analyze their SNR characteristics.  Equivalent to `rtl_watch` but for processing log files.
* [DNT](https://github.com/hdtodd/DNT): Display temperatures from remote thermometers in your neighborhood.  Use the information from `rtl_snr` or `rtl_watch` about thermometers in your neighborhood and then monitor them with a real-time display.

## Release History

*  V1.0: First operational version
*  V2.0: Extend table contents; revise parameter-entry options
*  V2.1: Add workaround for paho_mqtt v1/v2 callback incompatibility; finish docs.
*  V3.0: Add queuing and threads to separate packet collection from processing; correct error in window updating for duplicate packets
*  V4.0: Add HTTP streaming as an alternative data source instead of MQTT; correct error in handling noTPMS option; add additional filters to ignore packets that can't be cataloged. 

## Author

David Todd, hdtodd@gmail.com, v1: 2023.03; v2.0: 2023.05; v2.1 2024.07; v3.0 2024.08; v4.0 2024.08


