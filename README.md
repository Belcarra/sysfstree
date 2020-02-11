# PiGadgetInfo

*GadgetInfo* displays *SysFS* information from the *Gadget USB* drivers.

## Loading Gadget ConfigFS

*GadgetInfo* Assumes these modules are loaded to active configfs gadget:

- dwc2 
- libcomposite

## Usage
```
usage: filetreemaker [-h] [-P [PATTERN [PATTERN ...]]] [-r ROOT] [-o OUTPUT]
                     [-if [INCLUDE_FOLDER [INCLUDE_FOLDER ...]]]
                     [-xf [EXCLUDE_FOLDER [EXCLUDE_FOLDER ...]]]
                     [-xn [EXCLUDE_NAME [EXCLUDE_NAME ...]]] [-m MAX_LEVEL]
                     [--usb_gadget] [--udc] [--soc-udc] [--soc-usb3]
                     [--gadget] [--usb_f]
                     [Path [Path ...]]

positional arguments:
  Path                  pathname

optional arguments:
  -h, --help            show this help message and exit
  -P [PATTERN [PATTERN ...]], --pattern [PATTERN [PATTERN ...]]
                        shell pattern match
  -r ROOT, --root ROOT  root of file tree
  -o OUTPUT, --output OUTPUT
                        output file name
  -if [INCLUDE_FOLDER [INCLUDE_FOLDER ...]], --include_folder [INCLUDE_FOLDER [INCLUDE_FOLDER ...]]
                        include folder
  -xf [EXCLUDE_FOLDER [EXCLUDE_FOLDER ...]], --exclude_folder [EXCLUDE_FOLDER [EXCLUDE_FOLDER ...]]
                        exclude folder
  -xn [EXCLUDE_NAME [EXCLUDE_NAME ...]], --exclude_name [EXCLUDE_NAME [EXCLUDE_NAME ...]]
                        exclude name
  -m MAX_LEVEL, --max_level MAX_LEVEL
                        max level
  --usb_gadget          /sys/kernel/config/usb_gadget
  --udc                 /sys/class/udc
  --soc-udc             /sys/devices/platform/soc/*.usb/udc
  --soc-usb3            /sys/devices/platform/soc/*.usb/usb3
  --gadget              /sys/kernel/config/usb_gadget
  --usb_f               /lib/modules/$(uname --kernel-
                        release)/kernel/drivers/usb/gadget/function/usb_f*

```

## SYSFS

Current configuration:
--usb_gadget - /sys/kernel/config/usb_gadget
--udc - /sys/class/udc/fe980000.usb
--soc - /sys/devices/platform/soc/fe980000.usb/gadget

Show gadget configuration:
--gadget - /sys/kernel/config/usb_gadget

Show loaded modules:
- /sys/module/usbf_f*
- /sys/module/udc_core
- /sys/module/dwc2
- /sys/module/libcomposite

## Gadget Function Modules available

--usb_f - /lib/modules/$(uname --kernel-release)/kernel/drivers/usb/gadget/function/usb_f_*


## Installation

Install with ``pip`` or ``easy_install``.

::

    pip install followname

## Examples


## Running Tests

GadgetInfo currently only has doctests.

Run tests with nose::

    nosetests --with-doctest src/pigadgetinfo

Run tests with doctest::

    python -m doctest -v src/pigadgetinfo/__init__.py
