#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Set encoding default for python 2.7
# vim: syntax=python noexpandtab

# sysfstree implements a generator that will recursively iterate a file system, typically /sys, retrieving
# the contents of the files, and displaying the path names them in a fashion similar to the tree(1) command.
#

# e.g. sysfstree /sys/devices/platform/soc/ --include udc
#  [/sys/devices/platform/soc]
#  ┣━[fe980000.usb]
#  ┃   ┣━[udc]
#  ┃   ┃   ┗━[fe980000.usb]
#  ┃   ┃       ┣━device -> /sys/devices/platform/soc/fe980000.usb
#  ┃   ┃       ┣━subsystem -> /sys/class/udc
#  ┃   ┃       ┣━[power]
#  ┃   ┃       ┃   ┣━runtime_suspended_time: 0
#  ┃   ┃       ┃   ┣━autosuspend_delay_ms:
#  ┃   ┃       ┃   ┣━runtime_active_time: 0
#  ┃   ┃       ┃   ┣━control: auto
#  ┃   ┃       ┃   ┗━runtime_status: unsupported
#  ┃   ┃       ┣━current_speed: UNKNOWN
#  ┃   ┃       ┣━is_selfpowered: 0
#

# pigadgetinfo displays info about Gadget USB from the SysFS and ConfigFS.
# The display format is similar to tree(1) with the contents of the files shown.
#
# loosely adapted from FileTreeMaker.py

import os
import sys
import fnmatch
import magic
import struct
from termcolor import colored

"""sysfstree.py: ..."""

# __author__  = "Stuart.Lynne@belcarra.com"


class sysfstree(object):

	def __init__(self, root, maxlevel, include=None, exclude=None, bold=None, ordinary=False, nobold=False):

		self.maxlevel = maxlevel
		self.include = include
		self.exclude = exclude
		self.bold = bold
		self.ordinary = ordinary
		self.nobold = nobold
		self.root = root

		# print("sysfstree: maxlevel: %s include: %s exclude: %s bold: %s root: %s" %
		#       (self.maxlevel, self.include, self.exclude, self.bold, self.root))

	# match_exclude
	# Return False if matches is None or name not in matches
	#
	def match_exclude(self, name, level):

		if self.exclude is None:
			return False
		try:
			matches = self.exclude[level]
		except IndexError:
			return False

		if len(matches) == 0:
			# print("match_exclude: %s in %s len(matches) == 0" % (name, matches))
			return False
		if type(matches) is list:
			# print("match_exclude: %s in %s list" % (name, matches))
			return any(fnmatch.fnmatch(name, pattern) for pattern in matches)
		if type(matches) is str:
			# print("match_exclude: %s in %s str" % (name, matches))
			return fnmatch.fnmatch(name, matches)
		return False

	# match_include
	# Return True if matches is None or if name in matches
	#
	def match_include(self, name, level):
		if self.include is None:
			return True
		try:
			matches = self.include[level]
		except IndexError:
			return True

		# print("match_include: %s in %s" % (name, matches))
		if len(matches) == 0:
			return True
		if type(matches) is list:
			return any(fnmatch.fnmatch(name, pattern) for pattern in matches)
		if type(matches) is str:
			return fnmatch.fnmatch(name, matches)
		return True

	def _colored(self, text, color=None, attrs=None):
		if self.nobold:
			return text
		return colored(text, color, attrs=attrs)

	def _color(self, path, level):
		if self.bold is None:
			return path
		try:
			matches = self.bold[level]
		except IndexError:
			matches = None

		# print("_color: %s in %s" % (path, matches))

		if matches is None or len(matches) == 0:
			pass

		elif type(matches) is list:
			# print("color: %s in %s list" % (path, matches))
			if any(fnmatch.fnmatch(path, pattern) for pattern in matches):
				return self._colored(path, 'red', attrs=['bold'])

		elif type(matches) is str:
			# print("color: %s in %s str" % (name, matches))
			if fnmatch.fnmatch(path, matches):
				return self._colored(path, 'red', attrs=['bold'])
		return path

	def pathdescriptors(self, path):
		try:
			# XXX need to stat the file and limit how much
			# we are willing to read
			bdata = []
			with open(path, 'rb') as f:
				byte = f.read(1)
				while byte:
					bdata.append(struct.unpack('B', byte)[0])
					byte = f.read(1)

			length = 0
			descriptors = []
			hexstr = ''
			for x in bdata:
				t = "%02x" % (x)
				if length == 0:
					hexstr = t
					length = x - 1
				else:
					length -= 1
					hexstr += ' ' + t
				if length == 0:
					length = 0
					descriptors.append(hexstr)
					hexstr = ''

			return descriptors

		except Exception:
			return ''

	def pathread(self, path):

		try:
			fstat = os.stat(path)
			# print("fstat: size:%s" % (fstat.st_size))
		except (PermissionError):
			return ''

		# 4096 or 0 byte files should contain info
		if self.ordinary or fstat.st_size == 4096 or fstat.st_size == 0:
			try:
				f = open(path, "r")
				lines = f.readlines(1000)
				f.close()
				return lines
			except (PermissionError, OSError):
				return ''
			except UnicodeDecodeError:
				return '[UnicodeDecodeError]'

		# 65553 byte files are USB Descriptors
		if fstat.st_size == 65553:
			return self.pathdescriptors(path)

		# unknown - see if ELF module, this is special case
		# so we can list modules from /lib/.*/modules/
		#
		try:
			filetype = magic.from_file(path)
			if "ELF" in filetype:
				return ["ELF file"]
		except (magic.MagicException, PermissionError):
			return ''
		return '<UNKNOWN>'

	# recurse through the file system displaying information from the files
	# and symlinks found
	#
	def _tree(self, parent_path, file_list, prefix, level):

		# print("\"%s\" %s" % (prefix, parent_path))
		# print("dirs: %s" % (self.dirs))

		if level == -1:
			yield ("[%s]" % (self._colored(parent_path, attrs=['bold'])))
			yield from self._tree(parent_path, file_list, prefix, 0)
			return

		if len(file_list) == 0 or (self.maxlevel != -1 and self.maxlevel <= level):
			return

		for idx, sub_path in enumerate(sorted(file_list, key=str.casefold)):

			full_path = os.path.join(parent_path, sub_path)

			# if there is a set of includes for this level ensure that the we match
			# this path
			if not self.match_include(sub_path, level):
				continue

			# if there is a set of excludes for this level ensure that the we do not
			# match this path
			if self.match_exclude(sub_path, level):
				continue

			# set the tree decoration
			# idc = ("┣━━", "┗━━")[idx == len(file_list) - 1]
			idc = ("├──", "└──")[idx == len(file_list) - 1]

			# for directories yield the directory name and then yield from recursively
			if os.path.isdir(full_path) and not os.path.islink(full_path):

				yield ("%s%s[%s]" % (prefix, idc, self._color(sub_path, level)))

				tmp_prefix = (prefix + "    ", prefix + "│   ")[len(file_list) > 1 and idx != len(file_list) - 1]
				yield from self._tree(full_path, os.listdir(full_path), tmp_prefix, level + 1)

			# for symlinks yield the real pathname
			elif os.path.islink(full_path):
				yield ("%s%s%s -> %s" % (prefix, idc, self._color(sub_path, level), os.path.realpath(full_path)))

			# files yield as many lines of data as we read from the file, pathread() does
			# some interpretation so it will recognize ELF files and USB Descriptors
			#
			elif os.path.isfile(full_path):
				line = self.pathread(full_path)
				first = True
				if len(line) == 0:
					yield ("%s%s%s: [NULL]" % (prefix, idc, self._color(sub_path, level)))
				else:
					idc = "├──"
					for d in line:
						yield ("%s%s%s: %s" % (prefix, idc, self._color(sub_path, level), d.rstrip()))
						if not first:
							continue
						# blank sub_path and change idc
						sub_path = ' ' * (len(sub_path) + 1)
						idc = "│ "
						first = False


def _main(paths, maxlevel=-1, include=[], exclude=[], bold=[], ordinary=False, nobold=False):
	# print("include: %s" % (include))
	# print("exclude: %s" % (exclude))
	# print("bold: %s" % (bold))
	for p in paths:
		sysfs = sysfstree(p, maxlevel=maxlevel, include=include, exclude=exclude, bold=bold, ordinary=ordinary, nobold=nobold)
		try:
			for l in sysfs._tree(p, os.listdir(p), "", -1):
				print("%s" % (l), file=sys.stdout)
		except PermissionError:
			print("[%s] [PermissionError]" % (p))


def _test(args):
	import doctest
	doctest.testmod()

	# _main(["/sys/kernel/config/usb_gadget"])
	# _ main(["/sys/devices/platform/soc"], include=["*.usb"])
	# _main(["/sys/devices/platform/soc"], maxlevel=args.maxlevel, include=[["*.usb"]], exclude=[[],
	#  	["usb3", "subsystem", "driver", "power", "gadget", "of_node", "pools", "driver_override", "modalias", "uevent"]])

	# _main(["/sys/devices/platform/soc"], maxlevel=args.maxlevel, include=[["*.usb"], ["udc"]])

	_main(["/sys"], include=[["power"], ["pm_freeze_timeout", "state"]])
	_main(["/sys/devices/platform/soc"], include=[["*.usb"], ["usb3"], ["descriptors", "ep_00", "driver"]])

	_main(["/sys/kernel/debug/tracing/events/workqueue/workqueue_execute_end"], )

	(sysname, nodename, release, version, machine) = os.uname()
	path = "/lib/modules/" + release + "/kernel/drivers/usb/gadget/function/"
	_main([path], maxlevel=args.maxlevel, include=["usb_f_*"])


# this is mainly for testing standalone
#
def main():
	import argparse
	import json

	parser = argparse.ArgumentParser(
		description="Display information about Gadget USB from SysFS and ConfigFS",
		formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=999))

	parser.add_argument("-T", "--test", help="run tests", action='store_true')
	parser.add_argument("-O", "--ordinary", help="not in /sys", action='store_true')
	parser.add_argument("-P", "--path", nargs='*', help="include (shell pattern match)", default=[])
	parser.add_argument("-I", "--include", nargs='*', help="include (shell pattern match)", default=[])
	parser.add_argument("-E", "--exclude", nargs='*', help="exclude (shell pattern match)", default=[])

	parser.add_argument("-B", "--bold", nargs='*', help="bold (shell pattern match)", default=[])
	parser.add_argument("-N", "--nobold", nargs='*', help="bold (shell pattern match)", default=[])

	parser.add_argument("--include_list", type=json.loads, help="json list version of include")
	parser.add_argument("--exclude_list", type=json.loads, help="json list version of exclude")
	parser.add_argument("--bold_list", type=json.loads, help="json list version of bold")

	parser.add_argument("-m", "--maxlevel", help="max level", type=int, default=-1)
	parser.add_argument("paths", metavar='Path', type=str, nargs=argparse.REMAINDER, help="pathname", default=[])

	args = parser.parse_args()

	print("args: %s" % (args))

	if args.bold and args.bold_list:
		print("--bold and --bold_list are mutually incompatible, use only one")
		exit(1)

	if args.include and args.include_list:
		print("--include and --include_list are mutually incompatible, use only one")
		exit(1)

	if args.exclude and args.exclude_list:
		print("--exclude and --exclude_list are mutually incompatible, use only one")
		exit(1)

	if args.bold:
		args.bold_list = [args.bold]

	if args.include:
		args.include_list = [args.include]

	if args.exclude:
		args.exclude_list = [args.exclude]

	if args.test:
		_test(args)

	for path in args.path + args.paths:
		_main([path], maxlevel=args.maxlevel, include=args.include_list, exclude=args.exclude_list, bold=args.bold_list,
			ordinary=args.ordinary, nobold=args.nobold)


if __name__ == "__main__":
	main()
