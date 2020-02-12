# PiGadgetInfo

*GadgetInfo* displays *SysFS* information from the *Gadget USB* drivers.

## Loading Gadget ConfigFS

*GadgetInfo* Assumes these modules are loaded to active configfs gadget:

- dwc2 
- libcomposite

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

