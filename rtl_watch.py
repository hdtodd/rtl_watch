#! /usr/bin/python3 rtl_watch.py
#  Python program for real-time monitoring of ISM packets.
#
#  Uses an ISM-band monitoring computer that runs rtl_433 to
#  collect and analyze ISM-band (433MHz in the US) packet
#  broadcast by remote-sensing devices and received at the
#  monitoring computer via RTL_SDR dongle.
#  rtl_433 on the monitoring computer analyzes radio packets
#  and broadcasts the information about recognized packets via
#  mqtt broker.
#
#  rtl_watch subscribes to that published mqtt stream to
#  record, count, and analyze signal strength of packets
#  received by that RTL_SDR dongle.  rtl_watch can run on
#  the monitoring computer or any number of other computers
#  on the LAN to which the monitoring computer is connected.
#
#  Devices and analyzed data are displayed in real time in
#  a window on the computer running rtl_watch.
#  Analyzed data includes
#     Device Name, # of records seen,
#        and signal-to-noise ratio mean, standard deviation,
#        min, and max
#  The data are updated dynamically, as the packets are seen.
#
#  At any time, user can print a summary of devices seen
#  to date, and then analysis continues.
#
#  Written by H. David Todd, hdtodd@gmail.com, 2023.03.02

import tkinter as tk
import tkinter.font as tkf
import random
import json
import time
import getopt, sys
from paho.mqtt import client as mqtt_client
from datetime import datetime
import class_stats as stats

###############################################################################
##  *** BEGIN LOCAL MODIFICATIONS ***

# MQTT connection parameters
# Parameters used to establish the mqtt connection to the rtl_433 receiver mqtt publisher
broker = 'pi-1'
port = 1883
topic = "rtl_433/pi-1/events"
# If your mqtt broker is secured, provide login info
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = '<myusername>'
password = '<mypassword>'
##  *** END LOCAL MODIFICATIONS ***
###############################################################################

###############################################################################
# Global variable initialization

# Set 2-sec threshhold for rejecting duplicate records
thresh = 2.0

# Set blank "lastEntry" key record fields for rejecting duplicate records
#   time+/-2sec with model+id the same count as a duplicate record
lastEntry = { "time":0.0, "device":"" }

first_rec = True


###############################################################################
# Command line processor: options are [<none> | -h | -f | -c]
def getarg():

    options = "hxy"
    long_options = ["Help", "X", "Y"]

    def helper():
        print("rtl_watch: program to monitor devices observed by rtl_433")
        print("           on the ISM band (433MHz in the US)")
        print("           Reports devices, number of records received from device,")
        print("             and signal-to-noise mean, std deviation, min, & max.")
        print("rtl_watch -h for this help message")
        print("rtl_watch -x (placeholder for future)")
        print("rtl_watch -y (placeholder for future)")

    # Remove program name from the list of command line arguments
    argumentList = sys.argv[1:]

    try:
        # Parse argument
        arguments, values = getopt.getopt(argumentList, options, long_options)

        # Act on it if valid, else give help msg and quit
        for currentArgument, currentValue in arguments:

            if currentArgument in ("-h", "-H", "--Help"):
                helper()
                quit()
            elif currentArgument in ("-x", "--X"):
                print("Option ", currentArgument, " not assigned")
            elif currentArgument in ("-y", "--Y"):
                print("Option ", currentArgument, " not assigned")

    except getopt.error as err:
        # output error msg, help, and quit
        print (str(err))
        helper()
        quit()

# Button action routines
def sortDevice():
    mqtt.loop_stop()
    row = 1
    for	device in sorted(devices):
        print("-> Moving ", device, " to row ", row)
        (cnt,snr,sigma,min,max) = devices[device].get()
        tbl[row][0].set(device)
        tbl[row][1].set(cnt)
        tbl[row][2].set(round(snr,1))
        tbl[row][3].set(round(sigma,2))
        tbl[row][4].set(round(min,1))
        tbl[row][5].set(round(max,1))
        row += 1

    mqtt.loop_start()
    return

def sortRecCnt():
    mqtt.loop_stop()
    cntlist = {}
    for device in devices:
        print(device)
        (cnt,snr,sigma,min,max) = devices[device].get()
        key = f"{cnt:06}" + device
        cntlist[key] = device
    print(cntlist)
    row = 1
    for rec in sorted(cntlist, reverse=True):
        print("-> Moving ", cntlist[rec], " to row ", row)
        (cnt,snr,sigma,min,max) = devices[cntlist[rec]].get()
        tbl[row][0].set(cntlist[rec])
        tbl[row][1].set(cnt)
        tbl[row][2].set(round(snr,1))
        tbl[row][3].set(round(sigma,2))
        tbl[row][4].set(round(min,1))
        tbl[row][5].set(round(max,1))
        row += 1

    mqtt.loop_start()    
    return

def sortSnr():
    mqtt.loop_stop()
    cntlist = {}
    for device in devices:
        print(device)
        (cnt,snr,sigma,min,max) = devices[device].get()
        key = f"{snr:05.1f}" + device
        cntlist[key] = device
    print(cntlist)
    row = 1
    for rec in sorted(cntlist, reverse=True):
        print("-> Moving ", cntlist[rec], " to row ", row)
        (cnt,snr,sigma,min,max) = devices[cntlist[rec]].get()
        tbl[row][0].set(cntlist[rec])
        tbl[row][1].set(cnt)
        tbl[row][2].set(round(snr,1))
        tbl[row][3].set(round(sigma,2))
        tbl[row][4].set(round(min,1))
        tbl[row][5].set(round(max,1))
        row += 1

    mqtt.loop_start()    
    return

def stop(event=None):
    mqtt.loop_stop()
    mqtt.disconnect()
    win.quit()

def printsum():
    global devices
    global dedups, totrecs
    mqtt.loop_stop()
    print("\n____________________________________________________________________")
    print("\n\nrtl_watch: Printing summary of recorded rtl_433 packets\n")
    print("First entry recorded at: ", earliest_time.get(),
          "\nLast entry recorded at:  ", last_time.get()) 
    print("Processed ", dedups, " de-duplicated records of a total of ", totrecs, " records")
    print("\n{:<25} {:>8} {:>8} ±{:>5} {:>8} {:>8}".format(
          "Device", "Rec Cnt", "Mean", "𝜎  ", "Min", "Max"))
    for device in sorted(devices):
        (n,avg,std,min,max) = devices[device].get()
        print("{:<25} {:>8} {:>8.1f} ±{:>5.2f} {:>8.1f} {:>8.1f}".format(device,n,avg,std,min,max))
    print("\n____________________________________________________________________")
    mqtt.loop_start()
#    quit()

###############################################################################
# MQTT functions and display updating
# Connect to  MQTT broker 
def connect_mqtt() -> mqtt_client:
    def on_connect(mqtt, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed attempt to connect to ", mqtt)
            print("  with userdata ", userdata)
            print("Return code %d\n", rc)

    mqtt = mqtt_client.Client(client_id, clean_session=False)
    mqtt.username_pw_set(username, password)
    mqtt.on_connect = on_connect
    mqtt.connect(broker, port)
    subscribe(mqtt)
    return mqtt

# Subscribe to rtl_433 publication & process records we receive
def subscribe(mqtt: mqtt_client):

    # on_message does the real work
    # When we get a record, ignore if it's a duplicate, update display if it isn't
    def on_message(mqtt, userdata, msg):
        global first_rec, last_rec
        global devices
        global dedups, totrecs
        global tbl, devnum
        
        # count this new record
        totrecs += 1
        # parse the json payload
        y = json.loads(msg.payload.decode())
        # Get time in seconds since Epoch for comparison purposes, with 2 sec threshhold
        eTime = time.mktime(time.strptime(y["time"], "%Y-%m-%d %H:%M:%S"))
        # Is this a duplicate record?  Use time+model+id as a fingerprint to tell.
        # If not a duplicate entry, then process & record; else skip
        # Some records don't have an "id" field, so just use "model" in those cases
        if "id" in y:
             device = y["model"]+" "+ str(y["id"])
        else:
             device = y["model"]
        if eTime>lastEntry["time"]+thresh and device != lastEntry["device"]:
            dedups += 1
            drow = -1
            snr = 0.0 if not ('snr' in y) else float(y['snr'])
            print("{:<25} {:<20} snr={:>4.1f}".format(
                device, y["time"], snr) )

            if first_rec:
                earliest_time.set( y["time"])
                first_rec = False
            last_time.set(y["time"])

            if device in devices:
                # We've seen this device, so just update the values
                #   in the data table and in the display table
                devices[device].append(snr)
                (cnt,snr,sigma,min,max) = devices[device].get()
                for i in range (1, devnum+1):
                    if tbl[i][0].get()==device:
                        tbl[i][1].set(cnt)
                        tbl[i][2].set(round(snr,1))
                        tbl[i][3].set(round(sigma,2))
                        tbl[i][4].set(round(min,1))
                        tbl[i][5].set(round(max,1))
                        
            else:
                # This is a new device: 1) create a table entry for it;
                #   2) create a display table row for it
                #   3) connect the display variables to the table
                #   4) assign the values to the display
                devnum += 1
                tbl.append( (tk.StringVar(), tk.StringVar(), tk.StringVar(),
                             tk.StringVar(), tk.StringVar(), tk.StringVar() ) )
                row = add_row(devnum, tbl[devnum][0], tbl[devnum][1], tbl[devnum][2],
                              tbl[devnum][3], tbl[devnum][4], tbl[devnum][5])
                devices[device] = stats.stats(snr)
                (cnt,snr,sigma,min,max) = devices[device].get()
                tbl[devnum][0].set(device)
                tbl[devnum][1].set(cnt)
                tbl[devnum][2].set(round(snr,1))
                tbl[devnum][3].set(round(sigma,2))
                tbl[devnum][4].set(round(min,1))
                tbl[devnum][5].set(round(max,1))
                row.pack(side="top")
                
            lastEntry["time"] = eTime
            lastEntry["device"] = device
            
    mqtt.subscribe(topic)
    mqtt.on_message = on_message
    print("subscribed to mqtt feed")

def quit_prog(event=None):
    mqtt.loop_stop()
    mqtt.disconnect()
    win.quit()
        




#######################################################################################
# Table management and display

def add_row(devnum, device, reccnt, snr, stdev, min, max):
    row = tk.Frame(frm_table)
    tblrow.append(row)
    bg = "skyblue2" if devnum==0 else "white"
    lbl_device = tk.Label(row, width=25, textvariable=device, font=dfont, bg=bg)
    lbl_reccnt = tk.Label(row, width=10, textvariable=reccnt, font=dfont, bg=bg)
    lbl_snr    = tk.Label(row, width=10, textvariable=snr,    font=dfont, bg=bg)
    lbl_stdev  = tk.Label(row, width=10, textvariable=stdev,  font=dfont, bg=bg)
    lbl_min    = tk.Label(row, width=10, textvariable=min,    font=dfont, bg=bg)
    lbl_max    = tk.Label(row, width=10, textvariable=max,    font=dfont, bg=bg)
    lbl_device.grid(row=devnum, column=0, padx=5, pady=6, sticky="W")
    lbl_reccnt.grid(row=devnum, column=1, padx=5, pady=6, sticky="W")
    lbl_snr.grid(   row=devnum, column=2, padx=5, pady=6, sticky="W")
    lbl_stdev.grid( row=devnum, column=3, padx=5, pady=6, sticky="W")
    lbl_min.grid(   row=devnum, column=4, padx=5, pady=6, sticky="W")
    lbl_max.grid(   row=devnum, column=5, padx=5, pady=6, sticky="W")
    return row


#######################################################################################
#  Main script

getarg()

devices = {}
totrecs = 0
dedups  = 0
devnum = 0
t = datetime.now()
win = tk.Tk()
hfont = tkf.Font(size=40)
bfont = tkf.Font(size=24)
dfont = tkf.Font(size=18)

win.title("rtl_watch")
# Build the title
frm_title = tk.Frame(win, borderwidth=10, relief="groove")
frm_title.pack(side="top", fill="x", expand=True)
lbl_title  = tk.Label(frm_title, text="rtl_watch: monitor devices broadcasting over ISM bands using rtl_433",
                      font=hfont, bg="medium sea green", fg="white")
lbl_title.pack(anchor="center", fill="x", padx=10, pady=10)

# Build the button menu
frm_toolbar = tk.Frame(win)
frm_toolbar.pack(side="top", fill="x", expand=True)
btn_device  = tk.Button(frm_toolbar, text="Sort Device",       command=sortDevice, font=bfont)
btn_reccnt  = tk.Button(frm_toolbar, text="Sort Record Count", command=sortRecCnt, font=bfont)
btn_snr     = tk.Button(frm_toolbar, text="Sort SNR",          command=sortSnr,    font=bfont)
btn_prtsum  = tk.Button(frm_toolbar, text="Print Summary",     command=printsum,   font=bfont, fg="green")
btn_stop    = tk.Button(frm_toolbar, text="Stop",              command=stop,       font=bfont, fg="red")
btn_device.pack(side="left")
btn_reccnt.pack(side="left")
btn_snr.pack(side="left")
btn_stop.pack(side="right")
btn_prtsum.pack(side="right")

# Build the information section
frm_info = tk.Frame(win, borderwidth=5, relief="raised")
frm_info.pack(side="top", fill="x", expand=True)
earliest_time = tk.StringVar()
earliest_time.set(t.strftime('%Y-%m-%d %H:%M:%S'))
last_time = tk.StringVar()
last_time.set(t.strftime('%Y-%m-%d %H:%M:%S'))
lbl_monitor = tk.Label(frm_info, text="Monitoring host: %s and topic: %s" % (broker, topic), font=dfont)
lbl_monitor.pack(side="top", padx=5, pady=5)
#lbl_first = tk.Label(frm_info, text="Earliest record:\n%s" % earliest_time, font=dfont)
lbl_first = tk.Label(frm_info, text="Earliest record:", font=dfont)
lbl_first.pack(side="left", padx=5, pady=5)
#lbl_last = tk.Label(frm_info, text="Latest record:\n%s" % last_time, font=dfont)
lbl_ltime = tk.Label(frm_info, textvariable=last_time,     font=dfont)
lbl_ltime.pack(side="right", padx=5, pady=5)
lbl_last = tk.Label(frm_info, text="Latest record:",    font=dfont)
lbl_last.pack(side="right", padx=5, pady=5)
lbl_ftime = tk.Label(frm_info, textvariable=earliest_time, font=dfont)
lbl_ftime.pack(side="left", padx=5, pady=5)

# Build the table, column header first
frm_table = tk.Frame(win, borderwidth=5, relief="groove")
frm_table.pack(side="top", fill="both", expand=True, padx=5, pady=5)
tblrow = []
tbl = []
devnum = 0
tbl.append( (tk.StringVar(), tk.StringVar(), tk.StringVar(),
               tk.StringVar(), tk.StringVar(), tk.StringVar() ) )
row = add_row(devnum, tbl[devnum][0], tbl[devnum][1], tbl[devnum][2], tbl[devnum][3], tbl[devnum][4], tbl[devnum][5])
tbl[devnum][0].set("Device\nmodel+id")
tbl[devnum][1].set("Record\nCount")
tbl[devnum][2].set("mean\nSNR")
tbl[devnum][3].set("SNR\nStd Dev")
tbl[devnum][4].set("Min\nSNR")
tbl[devnum][5].set("Max\nSNR")

tblrow.append(row)
row.pack(side="top")

mqtt = connect_mqtt()
mqtt.loop_start()

win.mainloop()

