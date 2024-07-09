# rtl\_watch: Real-time rtl\_433 monitor, Version 2.1.0
## Catalog and characterize ISM devices using rtl\_433

`rtl_watch` monitors output from `rtl_433` to display, in real time, the characteristics of the ISM-band devices broadcasting in your neighborhood.

`rtl_watch` can help you understand the ISM environment in your neighborhood by cataloging devices near you that are broadcasting on the ISM band (433MHz in the US).  The values provided by `rtl_watch` for the device signal characteristics over a number of readings may help you identify devices that are close to your location and/or new devices in your neighborhood.
![](https://github.com/hdtodd/rtl_watch/blob/main/rtl_watch.png)

## Use

If your system already has the required components, the command `./rtl_watch` is all that's needed to begin monitoring.  `./rtl_watch` starts the program and  prompts for the name of the `rtl_433` host on your local area network that provides MQTT subscription service.  `./rtl_watch -H <hostname>` starts the program without the prompt.

The program opens a scrollable, resizable display window with a table with columns that characterize the signals from the devices observed by your `rtl_433` system; it appends to the table new remote devices and associated data as they are observed by the `rtl_433` host system; and it updates subsequent readings as they are reported.

`./rtl_watch -h` provides more information about command-line options.  Additional configuration options are described in a later section.

## The Display Window

The display window is divided into several sections:

### The Upper Information Section
This section provides general information about the monitoring process.  It indicates:

1. the `rtl_433` host that it is monitoring;
1. the total number of packets received (many of which are duplicates since devices may send multiple packets for a single observation);
1. the total number of tranmissions -- de-duplicated packets -- received;
1. the date and time of the earliest and latest transmission observed.

### The Lower Information Section
This section is the table of characteristics of the signals observed from the various devices:

1. the device name, which is a concatenated string of "device model"/"channel"/"device id", as observed and reported by `rtl_433`;
1. warning flags observed from the device (see below);
1. the count of packets observed from each device;
1. the count of transmissions (de-duplicated packets) observed from each device;
1. the mean and standard deviation of the signal-to-noise ratio (SNR) of the transmissions observed from each device, as reported by `rtl_433`;
1. the mean and standard deviation of the frequencies of the transmissions observed from each device, as reported by `rtl_433`;
1. the mean and standard deviation of the inter-transmission gap times (ITGT) between transmissions from each device;
1. the mean and standard deviation of the number of packets per transmission (PPT) from each device.

### The Control Buttons
This section is located just below the title bar and provides the following controls for program operation:

1. **Sort Device** sorts the table entries in alphabetical order by device name.
1. **Sort Count** sorts the table entries in decreasing order of packet counts.  This may help identify the most active devices in your neighborhood.
1. **Sort SNR** sorts the table entries in decreasing order of SNR (signal-to-noise ratio values).  This may help identify the devices that are closest to your RTL-SDR receiver.
1.  **Heading Info** pops up a window to describe the table column contents.
1. **Reset Warn**  clears the warning flags for all devices (see below).
1. **Print Summary** prints to the controlling terminal session the contents of the table, sorted in alphabetical order by the device name/chnl/id string..
1. **Togl** toggles the display window between full screen and reduced size.
1. **Quit** exits the program.  (CNTL-C in the controlling terminal window also works) 

The sort and print functions suspend briefly the processing of any incoming packets, so a small number of packets might be missed as those functions are performed.

Data collection continues until you press the **Quit** button or type the \<CNTL-C\> character on the controlling keyboard.

### Warning Flags

`DNT` monitors packets decoded by `rtl_433` for two signals that might indicate that maintenance of a remote sensor is needed:

1. *Battery Low* is indicated by "!!" in the warning flags column.  Though not universally standard, devices generally indicate an impending low-battery condition by changing the `battery_low` flag from 1 to 0 in its broadcast packets.  *Any* occurence of `battery_low` = 0 causes `DNT` to post the "!!" warning flag for that device.  That flag is sticky: the warning flag remains, even if `battery_low` returns to 1, since the battery voltage may be fluctuating with ambient temperature and the device may need attention in any case.
1. *Status Change* is indicated by "?!" in the warning flags column.  The remote-device status field is not present in the packets for all devices and is not standardized.  But a change in status may indicate that the device needs attention and so is flagged.  The "Status Change" flag is also sticky: once set for a device, it remains set despite any subsequent changes in packet status field values.

*Battery Low* takes precedence over *Status Change*, so only "!!" will be displayed if the battery-low flag has been seen even if a status-change has occurred.

The **Reset Warn** button clears both the battery-low and status-change flags for *all* devices.  If warning flags reappear after a reset, they are due to new warning conditions appearing for the device.

### Using the Information

The information from `rtl_watch` can be helpful in several ways to understand your ISM neighborhood:

1.  Which devices are closest to you?  High values of SNR mean (e.g., 15-20) and standard deviation indicate that the device is likely close to your RTL-SDR receiver.  Also, high values for packet or transmit count likely indicate a device close to your receiver, as their packets are received routinely, relative to those with low counts (but check correlation with ITG and PPT).
1.  Which devices may either be remote or experiencing interference from other devices?  A high standard deviation value for ITG (inter-transmission gap) or PPT (packets per transmission) indicate that the transmitting device's packets are not being received routinely.  That could be because of interference from other devices (which prevent the packets from being decoded correctly) or because the device is remote from your receiver (check for correlation SNR mean and standard deviation).
1.  Which devices have unreliable oscillators?  A high value for frequency standard deviation likely indicate an unstable (possibly older) device clock.

## Installing `rtl_watch`

`rtl_watch` is a Python3 program.  It requires that the Python packages `tkinter` and `paho-mqtt` be installed on the computer on which `rtl_watch` is invoked.  `rtl_watch` has been tested on Mac OSX Catalina and Raspbian Bullseye. On Mac OSX, you may need to install Python3 if you haven't already done so ( <https://www.python.org/downloads/macos/> ).

`rtl_watch` requires Python3 and Paho-MQTT on the displaying computer and an `rtl_433` system running on your local area network (description in subsequent section).  Paho-MQTT v2 broke v1 callback invocations, but v2.1.0 of `rtl_watch` incorporates a workaround so that it will operate with either v1.x or v2.x of Paho-MQTT.  However, invocation on a system running v2.x will generate a warning, since `rtl_watch` continues to use the deprecated v1-style callback invocation for now.

`rtl_watch` requires that a computer (the "monitoring computer") on your local-area network be running `rtl_433` and re-broadcasting the packets it recognizes via the `mqtt` protocol on the local-area network.  See instructions below if you do not have an `rtl_433` system set up or if it has not been set up to re-broadcast packets through the `mqtt` broker.

### Providing MQTT parameters

`rtl_watch` requires information about the `rtl_433` MQTT publishing host:

*  MQTT host name
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
     * Under **Data output options** as command line option:` add `output mqtt` and `output json:/var/log/rtl_433/rtl_433.json`.  The former has the program publish received packets via MQTT and the latter logs received packets to a log file in case you want to do subsequent analysis of devices in your neighborhood.  More options for MQTT publishing service are available, but this will get you started.
     *Create the directory for that log file: `sudo mkdir /var/log/rtl_433`
1. **PRODUCTION TEST** Now `sudo /usr/local/bin/rtl_433` from the command line of one terminal screen on the monitoring computer.  From the command line of another terminal screen on that computer, or from another computer with mosquitto client installed, type `mosquitto_sub -h <monitorhost> -t "rtl_433/<monitorhost>/events"`, where you substitute your monitoring computer's hostname for "\<monitorhost\>".  If you have ISM-band traffic in your neighborhood, and if you've tuned `rtl_433` to the correct frequency, you should be seeing the JSON-format records of packets received by the RTL\_SDR dongle.  If you don't, first verify that you can publish to `mosquitto` on that monitoring computer and receive via a client (use the native `mosquitto_pub` and `mosquitto_sub` commands).  If `mosquitto` is functioning correctly, check that the rtl\_433 configuration file specifies mqtt output correctly.
1. Finally, install the rtl_433 monitor as a service:
  * `sudo cp rtl_433.service /etc/systemd/system/` to copy the .service file from this download directory (where this README file is located) into the systemd directory
  * `sudo systemctl enable rtl_433` and `sudo systemctl start rtl_433` to enable and start the service
  * Now, whenever the monitoring system is rebooted, it will restart the rtl_433 service and the mqtt service needed to broadcast in JSON format the information received by the RTL\_433 dongle as ISM packets.

The JSON log file grows quickly, so you will, over time, need to remove the JSON log file on the monitoring computer (`/var/log/rtl_433/rtl_433.json`).  Or you may want to use `logrotate` to manage those JSON files, in which case you could `sudo mv rtl_433.logrotate /etc/logrotate.d/rtl_433` on the host monitoring system to compress and manage the log files.

The developers of `rtl_433` continually update the list of devices that the program recognizes, so connect to the `rtl_433` download directory, `git pull`, re-build, and re-install `rtl_433` periodically to add recognition of new devices in your neighborhood.
 
## Known Issues

On occasion, pressing the Stop button in `rtl_watch` results in a hung application (at least on Mac OSX), requiring a forced-quit.  This appears to be related to the Python GIL issue and may disappear in future Python releases or on other systems.
       
## Related Tools
These related `rtl_433` tools might also be helpful:

* [`rtl_snr`](https://github.com/hdtodd/rtl_snr): Analyzes the JSON logs on the system that runs `rtl_433` to catalog the devices seen and analyze their SNR characteristics.  Equivalent to `rtl_watch` but for processing log files.
* [DNT](https://github.com/hdtodd/DNT): Display temperatures from remote thermometers in your neighborhood.  Use the information from `rtl_snr` or `rtl_watch` about thermometers in your neighborhood and then monitor them with a real-time display.

## Release History

*  V1.0: First operational version
*  V2.0: Extend table contents; revise parameter-entry options
*  V2.1: Add workaround for paho_mqtt v1/v2 callback incompatibility; finish docs.

## Author

David Todd, hdtodd@gmail.com, v1: 2023.03; v2.0: 2023.05; v2.1 2024.07.
