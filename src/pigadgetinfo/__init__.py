#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Set encoding default for python 2.7
# vim: syntax=python noexpandtab



"""FileTreeMaker.py: ..."""

__author__  = "legendmohe"

import os
import argparse
import time
import fnmatch
import magic
import struct


class FileTreeMaker(object):

	
	def match_exclude(self, name, matches):
		if len(matches) == 0:
			return False

		if type(matches) is list:
			return any(fnmatch.fnmatch(name, pattern) for pattern in matches)

		if type(matches) is str:
			return fnmatch.fnmatch(name, matches)

		return False
			
	def match_include(self, name, matches):
		if len(matches) == 0:
			return True

		if type(matches) is list:
			return any(fnmatch.fnmatch(name, pattern) for pattern in matches)

		if type(matches) is str:
			return fnmatch.fnmatch(name, matches)

		return True
			



	def _recurse(self, parent_path, file_list, prefix, output_buf, level):
		#print("\"%s\" %s" % (prefix, parent_path))
		if len(file_list) == 0 \
			or (self.max_level != -1 and self.max_level <= level):
			return
		else:
			file_list.sort(key=lambda f: os.path.isfile(os.path.join(parent_path, f)))
			for idx, sub_path in enumerate(file_list):

				#if any(exclude_name in sub_path for exclude_name in self.exn):
				#	continue

				try:
					if not self.match_include(sub_path, self.dirs[level]):
						continue
				except IndexError:
					pass

				full_path = os.path.join(parent_path, sub_path)

				idc = ("┣━", "┗━")[idx == len(file_list) - 1];

				if os.path.isdir(full_path) and not os.path.islink(full_path):
					
					# exclude any directories that match anything in self.exf list
					#if level is 0 and len(self.exf):
					#	if any(fnmatch.fnmatch(sub_path, pattern) for pattern in self.exf):
					#		continue

					# include any directories that match anything in self.exf list
					#if level is 0 and len(self.ixf):
					#	if not any(fnmatch.fnmatch(sub_path, pattern) for pattern in self.ixf):
					#		continue
					#	else:
					#		print("sub_path: %s in ixf: %s" % (sub_path, self.ixf))
					#else:
					#	# self.ixf empty 
					#	pass


					output_buf.append("%s%s[%s]" % (prefix, idc, sub_path))
					tmp_prefix = (prefix +"    ", prefix +"┃   ") [len(file_list) > 1 and idx != len(file_list) - 1]
					self._recurse(full_path, os.listdir(full_path), tmp_prefix, output_buf, level + 1)

				elif os.path.islink(full_path):
					output_buf.append("%s%s%s -> %s" % (prefix, idc, sub_path, os.path.realpath(full_path)))

				elif os.path.isfile(full_path):
					#if not self.pattern or fnmatch.fnmatch(os.path.basename(full_path), self.pattern):
					data = self.pathread(full_path)

					#print("data: %s path: %s" % (data, sub_path))	
					if data == "[UnicodeDecodeError]" and sub_path == "descriptors":
						descriptors = self.pathdescriptors(full_path)

						output_buf.append("%s%s%s:" % (prefix, idc, sub_path))
						for d in descriptors:
							output_buf.append("%s┃  ┣━[%s]" % (prefix, d))
						continue
						
					output_buf.append("%s%s%s: %s" % (prefix, idc, sub_path, data))


	def pathread(self,path):
		#print("pathread: %s" % (path))
		c = ''
		#print("pathread: %s %s" % (path, magic.from_file(path)))

		try:
			filetype = magic.from_file(path)
			if "ELF" in filetype:
				return "ELF file"
		except (magic.MagicException, PermissionError):
			pass

		try:
			f = open(path, "r")
			c = f.readline()
			f.close()
			return c.rstrip()
		except (PermissionError, OSError):
			return ''
		except UnicodeDecodeError:
			return '[UnicodeDecodeError]'

	def pathdescriptors(self,path):
		try:
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
					
		except:
			return ''


	def make(self, root, dirs, args):
		#self.root = args.root
		self.root = root
		self.exf = args.exclude_folder
		self.exn = args.exclude_name
		self.max_level = args.max_level
		self.pattern = args.pattern
		self.dirs = dirs
		self.ixf = args.include_folder

		#print("root:%s" % self.root)

		buf = []
		path_parts = self.root.rsplit(os.path.sep, 1)
		#buf.append("[%s]" % (path_parts[-1],))
		buf.append("%s" % (self.root))
		try:
			self._recurse(self.root, os.listdir(self.root), "", buf, 0)
		except FileNotFoundError:
			print("%s NOT FOUND" % (root))
			return ''


		output_str = "\n".join(buf)
		if len(args.output) != 0:
			with open(args.output, 'w') as of:
				of.write(output_str)
		return output_str

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-P", "--pattern", nargs='*', help="shell pattern match", default=[])
	parser.add_argument("-r", "--root", help="root of file tree", default=".")
	parser.add_argument("-o", "--output", help="output file name", default="")
	parser.add_argument("-if", "--include_folder", nargs='*', help="include folder", default=[])
	parser.add_argument("-xf", "--exclude_folder", nargs='*', help="exclude folder", default=[])
	parser.add_argument("-xn", "--exclude_name", nargs='*', help="exclude name", default=[])
	parser.add_argument("-m", "--max_level", help="max level", type=int, default=-1)

	parser.add_argument("--usb_gadget", help="/sys/kernel/config/usb_gadget", action='store_true')
	parser.add_argument("--udc", help="/sys/class/udc", action='store_true')
	parser.add_argument("--soc-udc", help="/sys/devices/platform/soc/*.usb/udc", action='store_true')
	parser.add_argument("--soc-usb3", help="/sys/devices/platform/soc/*.usb/usb3", action='store_true')
	parser.add_argument("--gadget", help="/sys/kernel/config/usb_gadget", action='store_true')
	parser.add_argument("--usb_f", help="/lib/modules/$(uname --kernel-release)/kernel/drivers/usb/gadget/function/usb_f*", action='store_true')

	parser.add_argument("paths", metavar='Path', type=str, nargs="*", help="pathname", default=[])

	args = parser.parse_args()
	#print("args: %s" % (args))

	if args.usb_gadget:
		print(FileTreeMaker().make("/sys/kernel/config/usb_gadget", [], args))

	if args.udc:
		print(FileTreeMaker().make("/sys/class/udc", [], args))

	if args.soc_udc:
		dirs = ["*.usb", ["udc", "gadget"]]
		print(FileTreeMaker().make("/sys/devices/platform/soc", dirs, args))

	if args.soc_usb3:
		dirs = ["*.usb", ["usb3", "gadget"]]
		print(FileTreeMaker().make("/sys/devices/platform/soc", dirs, args))

	if args.gadget:
		print(FileTreeMaker().make("/sys/kernel/config/usb_gadget", [], args))

	if args.usb_f:
		(sysname, nodename, release, version, machine) = os.uname()
		path = "/lib/modules/" + release + "/kernel/drivers/usb/gadget/function/"
		dirs = [ "usb_f_*" ]
		print(FileTreeMaker().make(path, dirs, args))

#- /sys/module/usbf_f*

	for path in args.paths:
		print(FileTreeMaker().make(path, [], args))

