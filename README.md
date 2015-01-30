# BeurerScaleManagerCLI
CLI interface to access Beurer scales (and resellers like Sanitas) via USB connection.

For simply logging body measures, Beurer Healthmanager tool is just oversized. Its also only available for Windows
and I could not get it working inside a VM (download data aborted every time). Thanks to Urban82's excellent analysis of the
scale USB communication (https://github.com/Urban82/BeurerScaleManager/wiki/Analysis), I wrote this simple Python script,
which is accessing the scale internal memory via USB and downloads a data dump. It then decodes the dump
and outputs the entries as simple tab seperated values (TSV) for further processing e.g. via Calcsheets.

If you are looking for a UI, please check: https://github.com/Urban82/BeurerScaleManager

## Example output:
```
User	Date Time	Weight	Bodyfat%	Water%	Muscles%
1	2015-01-28 19:10	62.5	38.9	44.5	39.2
1	2015-01-28 19:11	62.4	38.9	44.5	39.2
1	2015-01-29 10:38	62.8	39.2	44.3	39.1
1	2015-01-30 09:25	61.8	38.7	44.6	39.3
```

## Dependencies
The python script requires:
 * pyusb (a python module to access USB via libusb backend)
 * libusb (a library to communicate with USB devices)
 
## Installation
There are many ways to get the dependencies resolved. On an Ubuntu 14.10 I realized it that way:

```
$ sudo apt-get install libusb-1.0-0
$ sudo apt-get install python-pip
$ sudo pip install pyusb --pre
```

Find further details on: https://github.com/walac/pyusb

## Usage
Once installed you can download a data dump and decode it via

    $ sudo python scale.py update
  
Once you downloaded the data dump, you can decode it again with
    $ python scale.py