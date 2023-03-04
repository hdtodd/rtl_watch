# rtl\_watch: Real-time rtl\_433 monitor

### Catalog and characterize ISM devices using rtl\_433

## Purpose

`rtl_watch` can help you understand the ISM environment in your neighborhood.  It catalogs devices near you that are broadcasting on the ISM band (433MHz in the US).  The values provided by `rtl_watch` for the mean signal-to-noise ratio and its standard deviation over a number of readings may help you identify devices that are close to your location and/or new devices in your neighborhood.  Devices with higher SNR and lower standard deviations are likely to be nearer to you.

## Use

These use instructions presume that you already have `rtl_433` in operation on your local-area network and that it publishes ISM-device packet information via `mqtt`.  Instructions for setting that up are included below if you aren't already running `rtl_433`.

To start the monitoring process, issue the command `python3 rtl_watch.py` after first editing the hostname of your `rtl_433` system in that Python program to replace the string `"<mymonitor>"`.

The program opens a display window in which it builds dynamically the table of devices recognized by `rtl_433` and for each device displays the device name (+ id if that field is present in the packet), number of de-duplicated packets received, and the signal-to-noise rato (SNR) mean,  standard deviation, minimum, and maximum values of those packets.  

Press one of the sort buttons (device name, number of records seen, or mean SNR) to sort the display in alphabetical order of model(+id), decreasing order of number of de-duplicated packets seen, or decreasing order of mean SNR.

Press the `print` button to see a summary of packets observed (printed in alphabetical order of device name + id).

The sort and print functions suspend briefly the processing of any incoming packets, so a small number of packets might be missed as those functions are performed.

Data collection continues until you press the `Quit` button.

## Installing `rtl_watch`

`rtl_watch` is a Python3 program.  It requires that the Python packages `tkinter` and `paho-mqtt` be installed on the computer on which `rtl_watch` is invoked.  `rtl_watch` has been tested on Mac OSX Catalina and Raspbian Bullseye. On Mac OSX, you may need to install Python3 if you haven't already done so ( https://www.python.org/downloads/macos/ ).

To install `rtl_watch`, edit the file `rtl_watch.py`to replace the placeholder "\<mymonitor\>" with the name of the `rtl_433` host on your local area network (which could be the same computer as `rtl_watch` is installed on). 

`rtl_watch` requires a class library, `class-stats.py`, which is included in the distribution package.

`rtl_watch` requires that a computer (the "monitoring computer") on your local-area network be running `rtl_433` and re-broadcasting the packets it recognizes via the `mqtt` protocol on the local-area network.  See instructions below if you do not have an `rtl_433` system set up or if it has not been set up to re-broadcast packets through the `mqtt` broker.

## [If Needed] Installing and Configuring The Monitoring Computer
Perform these steps on the computer you intend to use to monitor the ISM-band radio signals.

1. If you don't already have one, purchase an RTL-SDR receiver.  Use your favorite search engine to search for "rtl sdr receiver".  They cost about $30US.  But be sure to get one with an antenna appropriate for your region's ISM frequency band.  Then you simply plug it in to a USB port on your monitoring computer.
1. If you're not sure of the frequency of ISM bands in use in your location, use a tool such as `CubicSDR` (https://cubicsdr.com/) to observe the various ISM bands and discover which ones have activity in your region.  Set the frequency in `rtl_433` (below) accordingly.
1. Install mosquitto.  On Raspbian, for example, `sudo apt-get install mosquitto mosquitto-client`.  The broker will be started by `systemd` and will be restarted whenever the system is rebooted.
1. Connect to a download directory on your monitoring computer and use `git` to install `rtl_433`: `git clone https://github.com/merbanan/rtl_433`.
1. Connect to the installed rtl\_433 directory and follow the instructions in `./docs/BUILDING.md`to build and install the rtl\_433 program. **Be sure to install the prerequisite programs needed by rtl_433 before starting `cmake`.**  
1. **INITIAL TEST** Following the build and install, you can simply invoke `sudo /usr/local/bin/rtl_433` to verify that it starts up, finds the RTL_SDR dongle, and identifies ISM packets.  You may need to adjust the frequency via command line, e.g.,  `-f 315M`, if you're not in the US.
1. `rtl_433` is a *very* sophisticated program with *many* options, and you may want to explore its use by reading through the help message or browsing the configuration file.  But for regular operation, it's easiest to create the configuration file and, once it's working as you want it to, add `rtl_433` as a system service following instructions:
   * `cp /usr/local/etc/rtl_433/rtl_433.example.conf /usr/local/etc/rtl_433/rtl_433.conf`
   * Edit `/usr/local/etc/rtl_433/rtl_433.conf`:
     * If your regional ISM band is not 433.92MHz, set the correct frequency in the "frequency" entry.
     * Under `## Analyze/Debug options`, comment out stats reporting: `#report_meta stats`
     * Under `## Data output options`/`# as command line option:` add `output mqtt` and `output json:/var/log/rtl_433/rtl_433.json`.  The former has the program publish received packets via `mqtt` and the latter logs received packets to a log file in case you want to do subsequent analysis of devices in your neighborhood.  More options for `mqtt` publishing service are available, but this will get you started.
     *Create the directory for that log file: `sudo mkdir /var/log/rtl_433`
1. **PRODUCTION TEST** Now `sudo /usr/local/bin/rtl_433` from the command line of one terminal screen on the monitoring computer.  From the command line of another terminal screen on that computer, or from another computer with mosquitto client installed, type `mosquitto_sub -h <monitorhost> -t "rtl_433/<monitorhost>/events"`, where you substitute your monitoring computer's hostname for "\<monitorhost>".  If you have ISM-band traffic in your neighborhood, and if you've tuned `rtl_433` to the correct frequency, you should be seeing the JSON-format records of packets received by the RTL\_SDR dongle.  If you don't, first verify that you can publish to `mosquitto` on that monitoring computer and receive via a client (use the native `mosquitto_pub` and `mosquitto_sub` commands).  If `mosquitto` is functioning correctly, check that the rtl\_433 configuration file specifies mqtt output correctly.
1. Finally, install the `rtl_433` monitor as a service:

	* `sudo cp rtl_433.service /etc/systemd/system/`
	* `sudo systemctl enable rtl_433`
	* `sudo systemctl start rtl_433`
       
 Now, whenever the monitoring system is rebooted, it will restart the rtl_433 service and the mqtt service needed to broadcast in JSON format the information received by the RTL\_433 dongle as ISM packets.
 
## Known Issues

On occasion, pressing the Quit button in `rtl_watch`results in a hung application (at least on Mac OSX), requiring a forced-quit.  This appears to be related to the Python GIL issue and may disappear in future Python releases or on other systems.
       
## Related Tools
These related `rtl_433` tools might also be helpful:

* [`rtl_snr`](https://github.com/hdtodd/rtl_snr): Analyzes the JSON logs on the system that runs `rtl_433` to catalog the devices seen and analyze their SNR characteristics.  Equivalent to `rtl_watch` but for processing log files.
* [DNT](https://github.com/hdtodd/DNT): Display temperatures from remote thermometers in your neighborhood.  Use the information from `rtl_snr` or `rtl_watch` about thermometers in your neighborhood and then monitor them with a real-time display.

## Author

David Todd, hdtodd@gmail.com, 2023.03.04.
