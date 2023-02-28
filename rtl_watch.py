import tkinter as tk
import tkinter.font as tkf
import random
import json
import time
import getopt, sys
from paho.mqtt import client as mqtt_client
from datetime import datetime
import class_stats as stats

#Device                      #Recs  Mean SNR ± 𝜎    Min    Max

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

    global useF
    options = "hcf"
    long_options = ["Help", "Celsius", "Fahrenheit"]

    def helper():
        print("rtl_watch: program to monitor devices observed by rtl_433")
        print("           on the ISM band (433MHz in the US)")
        print("           Reports devices, number of records received from device,")
        print("             and signal-to-noise mean, std deviation, min, & max.")
        print("rtl_watch -h for this help message")
        print("rtl_watch -f (placeholder for future)")
        print("rtl_watch -c (placeholder for future)")

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
            elif currentArgument in ("-c", "--Celsius"):
                useF=False
            elif currentArgument in ("-f", "--Fahrenheit"):
                useF=True

    except getopt.error as err:
        # output error msg, help, and quit
        print (str(err))
        helper()
        quit()

# Button action routines
def sortDevice():
    return

def sortRecCnt():
    return

def sortSnr():
    return

def stop(event=None):
    mqtt.loop_stop()
    mqtt.disconnect()
    win.quit()

def printsum():
    global devices
    global dedups, totrecs
    mqtt.loop_stop()
    mqtt.disconnect()
    print("\n\nrtl_watch: Printing summary")
    print("First entry recorded at: ", earliest_time.get())
    print("Last entry recorded at:  ", last_time.get()) 
    print("Processed ", dedups, " de-duplicated records of a total of ", totrecs, " records")
    for device in sorted(devices):
        (n,avg,std,min,max) = devices[device].get()
        print("{:<25} {:>8} {:>8.1f} ±{:>5.2f} {:>8.1f} {:>8.1f}".format(device,n,avg,std,min,max))
    quit()

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

        # count this new record
        totrecs += 1
        # parse the json payload
        y = json.loads(msg.payload.decode())
        # Get time in seconds since Epoch for comparison purposes, with 2 sec threshhold
        eTime = time.mktime(time.strptime(y["time"], "%Y-%m-%d %H:%M:%S"))
        # Is this a duplicate record?  Use time+model+id as a fingerprint to tell.
        # If not a duplicate entry, then process & record; else skip
        device = y["model"]+" "+ str(y["id"])
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
                devices[device].append(snr)
            else:
                devices[device] = stats.stats(snr)
                
            
            # Update labels to device data
#            if drow in range(displaySize):
#                try:
#                    locs[drow].set(loc)
#                    temp[drow].set(round(ltemp,1))
#                    rh[drow].set(hum)
#                except:
#                    print("exception when trying to set display values")
#                    pass
#            resize()
            # Now note this entry's fingerprint for subsequent de-duping
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

def add_row(rownum, device, reccnt, snr, stdev, min, max):
    row = tk.Frame(frm_table)
    tblrow.append(row)
    lbl_device = tk.Label(row, width=25, text=device, font=dfont)
    lbl_reccnt = tk.Label(row, width=10, text=reccnt, font=dfont)
    lbl_snr    = tk.Label(row, width=10, text=snr,    font=dfont)
    lbl_stdev  = tk.Label(row, width=10, text=stdev,  font=dfont)
    lbl_min    = tk.Label(row, width=10, text=min,    font=dfont)
    lbl_max    = tk.Label(row, width=10, text=max,    font=dfont)
    lbl_device.grid(row=rownum, column=0, padx=5, pady=6, sticky="W")
    lbl_reccnt.grid(row=rownum, column=1, padx=5, pady=6, sticky="W")
    lbl_snr.grid(   row=rownum, column=2, padx=5, pady=6, sticky="W")
    lbl_stdev.grid( row=rownum, column=3, padx=5, pady=6, sticky="W")
    lbl_min.grid(   row=rownum, column=4, padx=5, pady=6, sticky="W")
    lbl_max.grid(   row=rownum, column=5, padx=5, pady=6, sticky="W")
    return row


#######################################################################################
#  Main script

getarg()

devices = {}
totrecs = 0
dedups  = 0
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
tblrow = []
rowcnt = 0
frm_table = tk.Frame(win, borderwidth=5, relief="groove")
frm_table.pack(side="top", fill="both", expand=True, padx=5, pady=5)

row = add_row(rowcnt,"Device model+id", "Record\nCount", "SNR",
               "SNR\nStd Dev", "SNR Min", "SNR Max")
tblrow.append(row)
row.pack(side="top")

for i in range (6):
    row = add_row(++rowcnt, "Device %s" %i, "%s" % 12345, "%s" % 19.4, "%s" % 3.5,
                     "%s" % 9.9, "%s" % 25.0)
    tblrow.append(row)
    row.pack(side="top")

mqtt = connect_mqtt()
mqtt.loop_start()

win.mainloop()

