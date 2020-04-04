#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Set encoding default for python 2.7
# vim: syntax=python noexpandtab

# sysfstree implements a recursive generator that will recursively iterate a file system, typically /sys, retrieving
# the contents of the files, and displaying the path names them in a fashion similar to the tree(1) command.
#
# sysfstree_raspbian provides numerous shortcuts to interesting data (mostly gadget related)
# in SysFS on the Raspberry PI running Raspbian
#


"""sysfstree_main.py: ..."""

# __author__="Stuart.Lynne@belcarra.com"

import os
import sys
import argparse

try:
	from sysfstree.sysfstree import sysfstree
except (ImportError):
	from sysfstree import sysfstree

def _main(paths, maxlevel=-1, pinclude=[], pexclude=[], include=[], exclude=[], bold=[], sort=True):
        # print("_main: bold: %s" % (bold))
        print("_main: pinclude: %s" % (pinclude))
        for p in paths:
                sysfs = sysfstree(p, maxlevel=maxlevel,
                        pinclude=pinclude, pexclude=pexclude,
                        include=include, exclude=exclude,
                        bold=bold, sort=sort)
                for l in sysfs._tree(p, os.listdir(p), "", -1):
                        print("%s" % (l), file=sys.stdout)

def _test(args):
	_main(["/sys/kernel/config/usb_gadget"])


def main():
	parser = argparse.ArgumentParser(
		description="Display information about Gadget USB from SysFS and ConfigFS",
		formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=999))

	parser.add_argument("-P", "--path", nargs='*', help="include (shell pattern match)", default=[])
	parser.add_argument("-I", "--include", nargs='*', help="include (shell pattern match)", default=[])
	parser.add_argument("-E", "--exclude", nargs='*', help="exclude (shell pattern match)", default=[])

	parser.add_argument("--test", help=argparse.SUPPRESS, action='store_true')

	config = parser.add_argument_group('Gadget Configuration')
	config.add_argument("--usb-gadget", "--gadget", help="/sys/kernel/config/usb_gadget", action='store_true')
	config.add_argument("--usb-gadget-udc", "--gadget-udc", help="/sys/kernel/config/usb_gadget/*/udc", action='store_true')

	modules = parser.add_argument_group('Gadget Modules')
	modules.add_argument("--usb_f", "--usbf",
		help="/lib/modules/$(uname --kernel-release)/kernel/drivers/usb/gadget/function/usb_f*",
		action='store_true')

	status = parser.add_argument_group('Status')
	status.add_argument("--udc", help="/sys/class/udc", action='store_true')
	status.add_argument("--soc-udc", help="/sys/devices/platform/soc/*.usb/udc", action='store_true')
	status.add_argument("--soc-udc-state", help="/sys/devices/platform/soc/*.usb/udc/state", action='store_true')
	status.add_argument("--soc-gadget", help="/sys/devices/platform/soc/*.usb/gadget", action='store_true')
	status.add_argument("--soc-usb3", help="/sys/devices/platform/soc/*.usb/usb3", action='store_true')
	status.add_argument("--modules", help="/sys/modules/", action='store_true')

	pi = parser.add_argument_group('Raspberry Pi')
	pi.add_argument("--pi",
		help="Raspberry Pi info from /proc/device-tree/",
		action='store_true')

	# usb = parser.add_argument_group('UDC')
	# usb.add_argument("--gadget", help="/sys/kernel/config/usb_gadget", action='store_true')

	misc = parser.add_argument_group('Misc', 'Other commands')
	misc.add_argument("-r", "--root", help="root of file tree", default=".")
	misc.add_argument("-o", "--output", help="output file name", default="")
	misc.add_argument("-m", "--maxlevel", help="max level", type=int, default=-1)

	# parser.add_argument("paths", metavar='Path', type=str, nargs="*", help="pathname", default=[])
	parser.add_argument("paths", metavar='Path', type=str, nargs=argparse.REMAINDER, help="pathname", default=[])

	args = parser.parse_args()
	# print("args: %s" % (args), file=sys.stderr)

	if args.test:
		_test(args)

	if args.usb_gadget:
		_main(["/sys/kernel/config/usb_gadget"], maxlevel=args.maxlevel)

	if args.usb_gadget_udc:
		_main(["/sys/kernel/config/usb_gadget/"], maxlevel=args.maxlevel,
				include=[[], ["UDC"]],
				bold=[[], ["UDC"]])

	if args.udc:
		for s in os.listdir("/sys/class/udc"):
			#print("udc: s: %s" % (s, ), file=sys.stderr)
			_main([os.path.realpath("/sys/class/udc/%s" % (s))], maxlevel=args.maxlevel)

	if args.soc_udc_state:
		_main(["/sys/devices/platform/soc"], maxlevel=args.maxlevel,
			include=["*.usb", ["udc"], [], ["state", "function"]],
			bold=[["*"], [], ["*"], ["state", "function"]])
		_main(["/sys/kernel/config/usb_gadget/"], maxlevel=args.maxlevel,
			include=[[], ["UDC", "id*", "functions", "strings"]],
			bold=[["*"], ["UDC", "id*", ], ["*.*"], ["manufacturer", "product"]])
		_main(["/sys//kernel/config/usb_gadget/"], maxlevel=args.maxlevel,
			include=[[], ["configs"]],)

	if args.udc or args.soc_udc:
		#_main(["/sys/devices/platform/soc"], maxlevel=args.maxlevel,
		#		include=["*.usb", ["udc"]],
		#		bold=[["*"], [], ["*"], ["state"]])
		_main(["/sys/devices/platform/"], maxlevel=args.maxlevel,
		pinclude=["ocp/*.usb/*/*.usb", "soc/*.usb/*/*.usb"],
		bold=[["*"], [], ["*"], ["state"]])


	if args.soc_gadget:
		_main(["/sys/devices/platform/soc"], maxlevel=args.maxlevel, include=["*.usb", ["gadget"], args.include])

	if args.soc_usb3:
		_main(["/sys/devices/platform/soc"], maxlevel=args.maxlevel, include=["*.usb", ["usb3", "gadget"]])

	if args.modules:
		_main(["/sys/module"], maxlevel=args.maxlevel,
			include=[["usb_f_*", "dwc2", "dwc_otg", "libcomposite", "udc_core", "usbcore"], ["holders", "initstate"]])

	if args.usb_f:
		(sysname, nodename, release, version, machine) = os.uname()
		path = "/lib/modules/" + release + "/kernel/drivers/usb/gadget/function/"
		_main([path], maxlevel=args.maxlevel, include=["usb_f_*"])

	if args.pi:
		_main(["/proc/device-tree"], maxlevel=args.maxlevel, include=["model", "serial-number"])

	# - /sys/module/usbf_f*

	for path in args.path + args.paths:
		_main([path], maxlevel=args.maxlevel)


if __name__ == "__main__":
	main()
