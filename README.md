# SANTA event display

## Pre-requisites
* Reasonbly up-to date icetray
* PyQt5 

```
python3 -m pip install PyQt5
```

## Getting started

Modify the file in python/modules/usr_cfg.py to point to a GCD file (preferably an Upgrade one).

From the python directory, inside an icetray environment:
```
python3 santa-event-display.py
```

Open a file, and explore the displays. You can also add a filename as an argument to the python call.

If you have qtconsole installed, an ipython console will show up. If you modify the frame and want to see the results in the viewer, run:
```
viewer.refreshLists()
```

**If you run into issues, please submit them via git**
