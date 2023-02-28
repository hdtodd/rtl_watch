# rtl_watch

## Live monitor of rtl_433 for devices broadcasting on the ISM band (433MHz in the US) in your neighborhood

## Use

To start the monitoring process, `python3 rtl_watch.py`.

The program opens a display window in which builds the table of seen devices dynamically, as those devices are recognized by `rtl_433`.  Press the `print` button to see a summary of packets observed.  Data collection continues until you press the `Quit` button.

## Requirements

`rtl_watch` is a Python3 program.  It requires that the Python packages `tkinter` and `pah-mqtt` be installed on the computer on which `rtl_watch` is invoked.

`rtl_watch` has been tested on Mac OSX Catalina and Raspbian Bullseye. On Mac OSX, you may need to install Python3 if you haven't already done so https://www.python.org/downloads/macos/.


## Author

David Todd, hdtodd@gmail.com, 2023.02.28



