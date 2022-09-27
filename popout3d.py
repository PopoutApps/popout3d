#! /usr/bin/python3

'''
--------------------------------------------------------------------------------
Popout3D Stereo Image Creation

GNU GENERAL PUBLIC LICENSE GPLv3

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
	GNU General Public License for more details.

	You should have a copy of the GNU General Public License
	in /usr/share/common-licenses/GPL-3. If not, 
	see <http://www.gnu.org/licenses/>.
	
--------------------------------------------------------------------------------
'''
# Depends on hugin_tools for align_image_stack.
import sys, os, shutil, subprocess, shlex #153 remove colorsys, math
#from PIL import Image, ExifTags, ImageOps, __version__ #153 remove ImageEnhance add ImageOps for orientation
from PIL import Image, ImageOps, __version__ #153 remove ImageEnhance add ImageOps for orientation
from PIL.ExifTags import TAGS

try:
	import gi
except:
	sys.exit('Failed to import gi')

try:
	gi.require_version('Gtk', '3.0')
except:
	print(gi.__version__)
	sys.exit('gi wrong version')

from gi.repository import Gtk, GdkPixbuf, Gdk #Gdk for colour button RGB

#-------------------------------------------------------------------------------
# create global variables and set default values
version = 'Popout3D V1.5.3'
firstrun = True
firstpress = True							# whether this is firstpress of '<' or '>'

view = 'All'
viewlist = []									# list of images to view
viewind = 0										# index of image to view
viewtext = ''

dummyfile = 'dummy.png'       # blank image to display when one is missing.
gladefile = 'popout3d.glade'
preffile = 'popout3d.dat'			# user preference file
myfile = '{None}'							# current file
myext = '{None}'							# current extension
#myfold set later
scope = 'Folder'

formatcode = 'A'							# first letter of format
stylecode = 'N'								# first letter of style
pairlist = []								  # list of pairs to process
warnings = ''									# list of Processed warnings

okchar = ['0','1','2','3','4','5','6','7','8','9','L','R'] #last char in 2D filename
okext	= ['jpg','JPG','jpeg','JPEG','png','PNG','tif','TIF','tiff','TIFF']
okformat = ['A','S','C']			# Anaglyph/Side-by-Side/Crossover
okstyle	= ['N','P'] 					# Normal/Popout

'''
Added by exalm:
	$XDG_DATA_HOME defines the base directory relative to which user specific data files should be stored. 
	If $XDG_DATA_HOME is either not set or empty, a default equal to $HOME/.local/share should be used.
	Done.
	$XDG_CONFIG_HOME defines the base directory relative to which user specific configuration files should be stored. 
	If $XDG_CONFIG_HOME is either not set or empty, a default equal to $HOME/.config should be used.
	Not done.
'''

#-----home folder
homefold = os.getenv('XDG_HOME')
if homefold != None:
	homefold = homefold + '/'
else:
	homefold = os.getenv('HOME') + '/'

# work folder for processing files
workfold = homefold + '.popout3d/'
if os.path.isdir(workfold):
	shutil.rmtree(workfold, True)

result = os.system('mkdir '+ workfold)
if result != 0:
	print('Cannot create work directory')
	sys.exit(result)

#-----config folder
configfold = os.getenv('XDG_CONFIG_HOME')
if configfold != None:
	configfold = configfold + '/'
else:
	configfold = os.getenv('HOME') + '/.config/popout3d/'

#-----project folder for Glade file	
package = ''
if os.path.exists('/.flatpak-info'): 
	datafold = '/app/share/popout3d/'
elif package == 'debian':
	datafold = os.getenv('XDG_DATA_HOME')
	if datafold != None:
		datafold = datafold + '/popout3d/'
	else:
		datafold = os.getenv('HOME') + '/.config/popout3d/'
		#datafold = '/usr/share/popout3d/' #1.5.3
else: # no package
	datafold = ''

#-------------------------------------------------------------------------------		
def getpreferences():
	global version, myfold, myfile, myext, formatcode, stylecode, view, scope, firstrun
	#choiceBright, choiceBal, preferenceBright, preferenceBal
	# local okpref, okcol, x, i
	# Prference files is not present when program in installed, so is a guide to
	# whether this is the first run.
	
	# create preferences array
	prefdata = []
	for i in range(7): #153 was 9
		prefdata.append('')

	# load preferences file, if file not found or is wrong version skip to end
	# if any fields are bad, replace with default
	okpref = True
	try:
		with open(configfold + preffile, 'r') as infile:
			for i in range(0, 7):
				prefdata[i] = infile.readline()
				prefdata[i] = prefdata[i][:-1] # remove linefeed
	except:
		okpref = False

	if okpref:
		if not prefdata[0] == version:
			okpref = False
	
	if okpref:			
		if os.path.exists(prefdata[1]):
			myfold = prefdata[1]
		else:
			myfold = homefold
						
		myfile = prefdata[2] ; myext = prefdata[3]; scope = 'Set'
		if not os.path.exists(myfile+myext):
			myfile == '{None}'; myext == '{None}'; scope = 'Folder'

		if prefdata[4] in ['A', 'S', 'C']: # Anaglyph/Side-by-Side/Crossover
			formatcode = prefdata[4]
		else:
			formatcode = 'A'

		if prefdata[5] in ['N','P']: # Normal (Level)/Popout
			stylecode = prefdata[5]
		else:
			stylecode = 'N'

		if prefdata[6] in ['All', '2D', '3D', 'Triptych']:
			view = prefdata[6]
		else:
			view = 'All'

		#153 prefdata[7] was for firstrun
		'''153 prefdata(8) was for colour and brightness balance
		okcol = True
		x = [0, 0]		 
		for i in range (0, 2):
			try:
				x[i] = int(prefdata[8].split(' ')[i])
			except:
				okcol = False

		if okcol:		 
			if x[0] >= -100 and x[0] <= 100:
				preferenceBright = x[0]
			else:	 
				preferenceBright = 0
			if x[1] >= -100 and x[1] <= 100:
				preferenceBal = x[1]					
			else:
				preferenceBright = 0
				
		choiceBright = preferenceBright; choiceBal = preferenceBal	
		'''

	if okpref:
 		firstrun = False
	else: # defaults
		#version
		myfold = '{None}'
		myfile = '{None}'
		myext = '{None}'
		formatcode = 'A'
		stylecode = 'N'
		view = 'All'
		#153 preferenceBright = 0; preferenceBal = 0

	# write pref file anyway in case mydir/myfile have been deleted or any other problem
	with open(configfold + preffile, 'w') as fn:			
		fn.write(version+'\n')
		fn.write(myfold+'\n')
		fn.write(myfile+'\n')
		fn.write(myext+'\n')
		fn.write(formatcode+'\n')
		fn.write(stylecode+'\n')
		fn.write(view+'\n')
		#152 fn.write('No\n')
		#153 fn.write(str(preferenceBright)+' '+str(preferenceBal)+'\n')

	#153 choiceBright = preferenceBright; choiceBal = preferenceBal

#===============================================================================
def showMessage(self, which, message):
	if which == 'warn':
		self.messageWarning.format_secondary_text(message)
		self.result = self.messageWarning.run() ; self.messageWarning.hide()
	elif which == 'ask':
		self.messageQuestion.format_secondary_text(message)
		self.result = self.messageQuestion.run() ; self.messageQuestion.hide()
		if self.result == Gtk.ResponseType.YES:
			return 'Yes'
		else:
			return 'No'
	else: #153
		return 'No'
	#else: #info		
	#	self.messageInfo.format_secondary_text(message)
	#	self.result = self.messageInfo.run() ; self.messageInfo.hide()	

#===============================================================================		 
def exif(newfilename, newext, processing):
	global pixbuf, error
	# local orientation
	orientation = -1
	
	if os.path.isfile(myfold+newfilename+'.'+newext):
		image = Image.open(myfold+newfilename+'.'+newext)
	else:		
		return -2
	
	try:
		image_exif = image.getexif()
	except AssertionError as error:
		print('image.exif() error: ', error)
		return -1

	for tag_id in image_exif:
		tag=TAGS.get(tag_id,tag_id)
		data=image_exif.get(tag_id)
		if isinstance(data,bytes):
			try:
				data=data.decode()
			except:
				continue	
		#print(f"{tag:20}:{data}")
		if tag == 'Orientation':
			orientation = data
		
	# save rotated file for processing
	if processing:
		if orientation in [3, 6, 8]: #rotate image	
			image = ImageOps.exif_transpose(image)
			image.save(workfold+newfilename+'.'+newext, quality=95, subsampling='4:4:4')
			image.close
			return orientation
		else:
			image.close
			return -1
	else: # for showImage
		image.close
		return orientation
	
#===============================================================================
def findMatch():
	global viewind # local searchlength, char1, char2, charN, viewindL, viewindR, viewindN

	if len(viewlist) > 0 and view != 'All': # Can use same image if TO All
		searchfilename = viewlist[viewind][0]; searchlength = -1 
		searchext = viewlist[viewind][1]; dimensions = viewlist[viewind][2]
		char1 = char2 = ''; viewindL = viewindR = viewindN = -1

		if not (view == 'All' or view == dimensions or (view == 'Triptych' and dimensions == '3D')):		
			# TO 2D
			# get basic filename, length and 2 characters
			if view == '2D' and dimensions == '3D':
				searchname = searchfilename[:-4];	searchlength = len(searchname)
				char1 = searchfilename[-4]; char2 = searchfilename[-3]	

				# search through list
				viewindL = viewindR = viewindN = -1
				for record in viewlist:
					if record[1] == searchext and record[2] == '2D':					
						if viewindL < 0 and searchname+char1 in record[0][:searchlength+1]:
							viewindL = viewlist.index(record) # L of 3D image matches a 2D image
						elif viewindR < 0 and searchname+char2 in record[0][:searchlength+1]:
							viewindR = viewlist.index(record) # R of 3D image matches a 2D image
						elif viewindN < 0 and searchname in record[0][:searchlength]:
							viewindN = viewlist.index(record) # match for basic name
		
			# TO 3D
			# get basic filename and 1 character
			elif view in ('3D', 'Triptych') and dimensions == '2D':
				searchname = searchfilename[:-1];	searchlength = len(searchname)
				char1 = searchfilename[-1]; char2 = ''
			
				# search through list
				viewindL = viewindR = viewindN = -1
				for record in viewlist:
					if record[1] == searchext and record[2] == '3D':					
						if viewindL < 0 and searchname+char1 in record[0][:searchlength+1]:
							viewindL = viewlist.index(record) # char of 2D image matches 1st char of a 3D image
						elif viewindR < 0 and searchname+char1 in record[0][:searchlength]+record[0][-3]:
							viewindR = viewlist.index(record) # char of 2D image matches 2nd char of a 3D image
						elif viewindN < 0 and searchname in record[0][:searchlength]:
							viewindN = viewlist.index(record) # match for basic name

			if viewindL > -1:
				viewind = viewindL
			elif viewindR > -1:
				viewind = viewindR
			elif viewindN > -1:
				viewind = viewindN
			else:
				viewind = -1
	'''
	if len(viewlist) > 0:
		if viewind > len(viewlist) -1:
			print('List indicator too big', len(viewlist), viewind)
		elif viewind < 0:
			print('List indicator negative', len(viewlist), viewind)
			#viewind = -1	
	'''
			
#===============================================================================
def findNext(direction):
	global viewind
	#local showit

	tryviewind = viewind; showit = False
	if direction == '>':
		tryviewind = tryviewind +1
	else:
		tryviewind = tryviewind -1
 			
	while showit == False and len(viewlist) > 0 and tryviewind > -1 and tryviewind < len(viewlist): 
		if (view in ('All', '3D', 'Triptych') and viewlist[tryviewind][2] == '3D') or (view in ('All', '2D') and viewlist[tryviewind][2] == '2D'):
			showit = True	
			viewind = tryviewind
		elif direction == '>':
			tryviewind = tryviewind +1
		else:
			tryviewind = tryviewind -1

#===============================================================================
def showImage(self):
	global viewind, firstpress
	
	self.image1.clear(); self.imageL.clear(); self.imageR.clear()
	self.labelImage1.set_text(''); self.labelImageL.set_text(''); self.labelImageR.set_text('')

	# valid image
	if len(viewlist) > 0 and viewind > -1 and not firstpress:
		# select currently indicated image from viewlist			
		newfilename = viewlist[viewind][0]; newext = viewlist[viewind][1]
		allocation = self.window.get_allocation()
		width = int(allocation.width*7/10); height = int(allocation.height*8/10)

		orientation = exif(newfilename, newext, False)
		if orientation == 3: # upside down, so rotate 180 clockwise
			pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilename+'.'+newext, width, height, True), 180)
		elif orientation == 6: # top at right so rotate 270 clockwise
			pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilename+'.'+newext, height, width, True), 270)
		elif orientation == 8: #top pointing left so rotate 90 clockwise
			GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilename+'.'+newext, height, width, True), 90)
		elif orientation == -2:
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(workfold+dummyfile+'.'+newext, width, height, True)		
		else: #already upright
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilename+'.'+newext, width, height, True)

		# two 2D images for triptych	
		if view == 'Triptych':
			width = int(width/2) ; height = int(height/2)
			# Left 2D image
			newfilenameL = viewlist[viewind][0][:-4]+viewlist[viewind][0][-4]; newextL = viewlist[viewind][1] 
			orientationL = exif(newfilenameL, newextL, False)

			if orientationL == 3: # upside down, so rotate 180 clockwise
				pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilenameL+'.'+newextL, width, height, True), 180)
			elif orientationL == 6: # top at right so rotate 270 clockwise
				pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilenameL+'.'+newextL, height, width, True), 270)
			elif orientationL == 8: #top pointing left so rotate 90 clockwise
				GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilenameL+'.'+newextL, height, width, True), 90)
			elif orientation == -2:
				pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(workfold+dummyfile+'.'+newext, width, height, True)
			else: #already upright
				pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilenameL+'.'+newextL, width, height, True)

			self.imageL.set_from_pixbuf(pixbuf)
			self.labelImageL.set_text(newfilenameL+'.'+newextL)

			# Right 2D image
			newfilenameR = viewlist[viewind][0][:-4]+viewlist[viewind][0][-3]; newextR = viewlist[viewind][1]
			orientationR = exif(newfilenameR, newextR, False)

			if orientationR == 3: # upside down, so rotate 180 clockwise
				pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilenameR+'.'+newextR, width, height, True), 180)
			elif orientationR == 6: # top at right so rotate 270 clockwise
				pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilenameR+'.'+newextR, height, width, True), 270)
			elif orientationR == 8: #top pointing left so rotate 90 clockwise
				GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilenameR+'.'+newextR, height, width, True), 90)
			elif orientation == -2:
				pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(workfold+dummyfile+'.'+newext, width, height, True)
			else: #already upright
				pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilenameR+'.'+newextR, width, height, True)

			self.imageR.set_from_pixbuf(pixbuf)
			self.labelImageR.set_text(newfilenameR+'.'+newextR)

		# image 1 must be last so it doesn't take all the space in a Triptych
		self.image1.set_from_pixbuf(pixbuf)
		self.labelImage1.set_text(newfilename+'.'+newext)
#===============================================================================
def makeviewlist(self):
	global viewlist, viewind, pairlist
	#local variables newfile, newext, viewtext

	viewlist = []
	for newfile in os.listdir(myfold):			 
		newfile, newext = os.path.splitext(newfile) ; newext = newext[1:]		
		if len(newfile) > 1:
			if newext in okext and newfile[-1] in okchar:
				# set: only add files in set to viewlist
				if scope == 'Set':
					if len(newfile) == len(myfile) +1:
						if newfile[0:-1] == myfile and newext == myext:						
							viewlist.append([newfile, newext, '2D'])

				# folder: add all files to viewlist
				elif scope == 'Folder':
					viewlist.append([newfile, newext, '2D'])

	for newfile in os.listdir(myfold):
		newfile, newext = os.path.splitext(newfile) ; newext = newext[1:]
		if len(newfile) > 4:
			if (newext in okext
			and newfile[-4] in okchar and newfile[-3] in okchar 
			and newfile[-2] in okformat and newfile[-1] in okstyle):

				# set: only add files in set to viewlist
				if scope == 'Set':
					if len(newfile) == len(myfile) +4:												 
						if newfile[0:-4] == myfile and newext == myext:
							viewlist.append([newfile, newext, '3D'])

				# folder: add all files to viewlist
				elif scope == 'Folder':
					viewlist.append([newfile, newext, '3D'])

		viewlist = sorted(viewlist)
							
	# Viewing title
	if view == 'All':
		self.labelViewingTitle.set_label('All Images')
	elif view == '2D':
		self.labelViewingTitle.set_label('2D Images')
	elif view in ('3D', 'Triptych'):
		self.labelViewingTitle.set_label('3D Images')

	#Window title
	if scope == 'Folder':
		self.window.set_title(version + '			Folder: ' + myfold)
	else:
		self.window.set_title(version + '			Set: ' + myfold + myfile + '*.' + myext)
		
	# viewtext
	viewtext = ''
	if viewlist != []:	
		for i in viewlist: # only show images relevant to view
			if view in ('All', '2D') and len(i[0]) > 1: 	#2D image
				if i[1] in okext and i[0][-1] in okchar:
					viewtext = viewtext+i[0]+'.'+i[1]+'\n'
			if view in ('All', '3D', 'Triptych'): 				#3D image
				if len(i[0]) > 4:
					if (i[1] in okext
					and i[0][-4] in okchar and i[0][-3] in okchar 
					and i[0][-2] in okformat and i[0][-1] in okstyle):
						viewtext = viewtext+i[0]+'.'+i[1]+'\n'
	else:
		viewtext = '{None}'

	self.labelViewing.set_text(viewtext)
	self.image1.clear() ; self.labelImage1.set_text('') 

#===============================================================================
def makepairlist(self, newfile, newformatcode, newstylecode, newext):
	global warnings, pairlist, viewtext, view
	# local imagestodo, imagesok

	# find out how many images there are in this set
	imagestodo = 0 ; imagesok = False

	# check for one with a digit at end
	for i in range (0, 10):
		if os.path.isfile(myfold+newfile+str(i)+'.'+newext):
			imagestodo = imagestodo + 1

	if imagestodo > 1:
		imagesok = True
			
	# check for pair with L at end and R at end

	if os.path.isfile(myfold+newfile+'L'+'.'+newext) and os.path.isfile(myfold+newfile+'R'+'.'+newext):
		imagesok = True
		
	# if there are at least two images in the set, call processPair to process, 
	if imagesok:
		# loop through all valid image pairs

		# digits at the end
		leftn = 0 ; rightn = 1
		while leftn < 9: # only single digits

			# look for images ending in 1-9
			rightn = leftn + 1
			while rightn < 10: # top number is 9
				# if left and right images exist and there is no existing 3D one
				if (os.path.isfile(myfold+newfile+str(leftn)+'.'+newext) and os.path.isfile(myfold+newfile+str(rightn)+'.'+newext)
 					and not os.path.isfile(myfold+newfile+str(leftn)+str(rightn)+newformatcode+newstylecode+'.'+newext)) and [newfile, str(leftn), str(rightn), newformatcode, newstylecode, newext] not in pairlist:
					pairlist.append([newfile, str(leftn), str(rightn), newformatcode, newstylecode, newext])
				rightn = rightn + 1
			leftn = leftn + 1

		# look for images ending in L and R
		if (os.path.isfile(myfold+newfile+'L'+'.'+newext) and os.path.isfile(myfold+newfile+'R'+'.'+newext)
 		 and not os.path.isfile(myfold+newfile+'LR'+newformatcode+newstylecode+'.'+newext)) and [newfile, 'L', 'R', newformatcode, newstylecode, newext] not in pairlist:
			 pairlist.append([newfile, 'L', 'R', newformatcode, newstylecode, newext])

#===============================================================================
def processPair(self, newfile, leftn, rightn, newformatcode, newstylecode, newext):
	global warnings
	#local orientationL, orientationR, infold
		
	# make filenames then call align_image_stack
	#153 fileout	 = newfile+leftn+rightn+formatcode+stylecode+'.'+newext
	fileout	= newfile+leftn+rightn+newformatcode+newstylecode+'.'+newext
	fileleft	= newfile+leftn+'.'+newext
	fileright = newfile+rightn+'.'+newext
	# turn image if needed and put into workfold
	orientationL = exif(newfile+leftn, newext, True)
	orientationR = exif(newfile+rightn, newext, True)

	# get from workfold if turned
	if orientationL in (3, 6, 8) or orientationR in (3, 6, 8): #turned
		infold = workfold
	else: # not turned -1 or not found -2
		infold = myfold			

	#replace A and P with styleAIS
	if stylecode == 'N':		
		styleAIS = 'A'
	else:
		styleAIS = 'P'

	command	 = 'align_image_stack -a "'+workfold+fileout+'" -m -i --use-given-order -"'+styleAIS+'" -C "'+infold+fileright+'" "'+infold+fileleft+'"' #-v {verbose}
		#command	 = 'align_image_stack -a "'+workfold+fileout+'" -m -i -P -C "'+workfold+'right.'+newext+'" "'+workfold+'left.'+newext+'"' 

	args = shlex.split(command) 
	print ('Aligning ', workfold+fileout) # For checking which files cause the problem
	result = subprocess.run(args) # this is no longer spawned
	result = str(result)[str(result).find("returncode")+11] # Output of command is CompletedProcess(args='?', returncode=0)
	result = int(result)

	# remove turned images if they exist
	if os.path.isfile(workfold+fileleft):
		os.remove(workfold+fileleft)
	if os.path.isfile(workfold+fileright):
		os.remove(workfold+fileright) 

	# align_image_stack has worked
	if result == 0: 
		# load left and right images

		image_left = Image.open(workfold+fileout+'0001.tif')
		image_right = Image.open(workfold+fileout+'0000.tif')
	
		# merge the files, put result in myfold
		if formatcode == 'A': # Anaglyph			

			'''#153 separate the colour bands then apply colours
			Lred, Lgreen, Lblue, Ljunk = image_left.split()
			Rred, Rgreen, Rblue, Rjunk = image_right.split()			 				
			'''		
			Lred	 = image_left.getchannel('R')
			Rgreen = image_right.getchannel('G')
			Rblue	 = image_right.getchannel('B')
			
			'''#153 Bright and Bal adjustments
			#adjL = (choiceBright+100)/100 * (100-choiceBal)/100
			#adjR = (choiceBright+100)/100 * (choiceBal+100)/100

			#Lred		 = Lred.point	(lambda i: i * adjL)
			#Rgreen = Rgreen.point(lambda i: i * adjR)
			#Rblue	= Rblue.point (lambda i: i * adjR)
			'''
			# merge the 3 colours
			image_new = Image.merge('RGB', (Lred, Rgreen, Rblue))
			
		elif formatcode == 'S': # Side-by-Side
			image_width = int(image_left.size[0]) ; image_height = int(image_left.size[1])
			# create double-width blank new image
			image_new = Image.new('RGB', (image_width * 2, image_height), color=0)
			# paste left image into new image on the left
			image_new.paste(image_left, (0, 0, image_width, image_height))
			# paste right image into new image on the right
			image_new.paste(image_right, (image_width, 0, 2 * image_width, image_height))

		else : # Crossover
			image_width = int(image_left.size[0]) ; image_height = int(image_left.size[1])
			# create double-width blank new image
			image_new = Image.new('RGB', (image_width * 2, image_height), color=0)
			# paste right image into new image on the left
			image_new.paste(image_right, (0, 0, image_width, image_height))
			# paste left image into new image on the right
			image_new.paste(image_left, (image_width, 0, 2 * image_width, image_height))

		# save new image, write .view file, remove process file and aligned images
		#?image_new.save(myfold+'3D'+fileout)
		image_new.save(myfold+fileout, quality=95, subsampling='4:4:4')

		# close delete input and delete intermediate files 
		image_left.close ; image_right.close
					 
		if os.path.isfile(workfold+fileout+'0001.tif'):
			os.remove(workfold+fileout+'0001.tif')
		if os.path.isfile(workfold+fileout+'0000.tif'):
			os.remove(workfold+fileout+'0000.tif') 
	else:
		warnings = warnings + 'It was not possible to align '+fileout+'.\n'
 	
#===============================================================================
#===============================================================================
# Load the UI, define UI class and actions
class GUI:

	def on_window1_destroy(self, object): # close window with 0 or X
		Gtk.main_quit()

	def menuitemQuit(self, menuitem): # quit with File > Quit
		Gtk.main_quit()

	def menuitemFolder(self, menuitem):
		global myfold, myfile, myext, scope, pairlist, view
		pairlist = []; self.buttonProcess.set_label('Queue')	
		scope = 'Folder'; view = 'All'
			
		filechooser = Gtk.FileChooserNative.new(title='Select the Folder where the images are', parent = self.window, action=Gtk.FileChooserAction.SELECT_FOLDER)
		filechooser.set_current_folder(myfold)
		response = filechooser.run();
		filechooser.hide()
		if response == Gtk.ResponseType.ACCEPT:	
			newfold = filechooser.get_filename()
			newfold = newfold+'/'	
			myfold = newfold; os.chdir(myfold) 
			myfile = '{None}' ;	myext = '{None}' 
			#self.window.set_title(version + '			Folder: ' + myfold)	
			makeviewlist(self) ; showImage(self)
		
	def menuitemSet(self, menuitem):
		global myfold, myfile, myext, scope, pairlist, view
		#local okfold
		pairlist = []; self.buttonProcess.set_label('Queue')	
		scope = 'Set'; view = 'All'

		filechooser = Gtk.FileChooserNative.new(title="Select any file from a set of images", parent = self.window, action=Gtk.FileChooserAction.OPEN)
		
		fileFilter = Gtk.FileFilter()
		fileFilter.add_pattern('*.jpg')	; fileFilter.add_pattern('*.JPG')
		fileFilter.add_pattern('*.jpeg') ; fileFilter.add_pattern('*.JPEG')
		fileFilter.add_pattern('*.tif')	; fileFilter.add_pattern('*.TIF')
		fileFilter.add_pattern('*.tiff') ; fileFilter.add_pattern('*.TIFF')
		fileFilter.add_pattern('*.png')	; fileFilter.add_pattern('*.PNG')
		fileFilter.set_name('Image files') ; filechooser.add_filter(fileFilter)
	 
		filechooser.set_current_folder(myfold)
		response = filechooser.run();	filechooser.hide()
		
		if response == Gtk.ResponseType.ACCEPT:		
			newfile = filechooser.get_filename()
		else: # answered No or closed window
			newfile = '{None}'	 
		
		newfold, newfile = os.path.split(newfile)
		newfile, newext = os.path.splitext(newfile)				

		okfile = True			
		if len(newfile) > 1:
			if newfile[-1] in okchar:
				myfold = newfold +'/' ; myfile = newfile[:-1]; myext = newext[1:]
			elif len(newfile) > 4:
				if (newfile[-4] in okchar and newfile[-3] in okchar and newfile[-2] in okformat and newfile[-1] in okstyle):
					myfold = newfold +'/' ; myfile = newfile[:-4]; myext = newext[1:] 
				else:
					okfile = False
			else:
				okfile = False
								
		if okfile == True:
			os.chdir(newfold)
			makeviewlist(self) ; showImage(self)
		else:
			if newfile != '{None}':
				showMessage(self, 'warn', 'Filename must follow rules in Help on File Selection.')

	def menuitemPreferences(self, menuitem):
		result = showMessage(self, 'ask', 'This will save your current settings as the defaults.')
		if result == 'Yes':
			with open(configfold + preffile, 'w') as fn:			
				try:
					fn.write(version+'\n')
					fn.write(myfold+'\n')
					fn.write(myfile+'\n')
					fn.write(myext+'\n')
					fn.write(formatcode+'\n')
					fn.write(stylecode+'\n')
					fn.write(view+'\n')
					#153fn.write(str(choiceBright)+' '+str(choiceBal)+'\n')
					#153preferenceBright = choiceBright; preferenceBal = choiceBal
				except:
					print('Failed to write preference file.')
			
	def menuitemHelp(self, menuitem):
		self.dialogHelp.run(); self.dialogHelp.hide()
			
	def buttonClose(self, menuitem):
		self.dialogHelp.hide()
				
	def menuitemAbout(self, menuitem):
		self.dialogboxAbout.run() ; self.dialogboxAbout.hide()

	def radiobuttontoggledAll(self, menuitem): 
		global view
		if menuitem.get_active():	
			view = 'All'
			findMatch(); showImage(self)
				
	def radiobuttontoggled2D(self, menuitem):
		global view
		if menuitem.get_active():
			view = '2D'
			findMatch(); showImage(self)
			
	def radiobuttontoggled3D(self, menuitem):
		global view
		if menuitem.get_active():
			view = '3D'
			findMatch(); showImage(self)
			
	def radiobuttontoggledTriptych(self, menuitem):
		global view
		if menuitem.get_active():
			view = 'Triptych'
			findMatch(); showImage(self)
			
	def radiobuttontoggledAnaglyph(self, radiobutton):
		global formatcode, pairlist
		if radiobutton.get_active():
			formatcode = 'A'			
			pairlist = []; self.buttonProcess.set_label('Queue')	
			makeviewlist(self); showImage(self)
						
	def radiobuttontoggledSidebyside(self, radiobutton):
		global formatcode, pairlist
		if radiobutton.get_active():
			formatcode = 'S'
			pairlist = []; self.buttonProcess.set_label('Queue')	
			makeviewlist(self); showImage(self)
				
	def radiobuttontoggledCrossover(self, radiobutton):
		global formatcode, pairlist
		if radiobutton.get_active():
			formatcode = 'C'
			pairlist = []; self.buttonProcess.set_label('Queue')	
			makeviewlist(self); showImage(self)

	def radiobuttontoggledNormal(self, radiobutton):
		global stylecode, pairlist
		if radiobutton.get_active():
			stylecode = 'N'
			pairlist = []; self.buttonProcess.set_label('Queue')	
			makeviewlist(self); showImage(self)
		
	def radiobuttontoggledPopout(self, radiobutton):
		global stylecode, pairlist
		if radiobutton.get_active():
			stylecode = 'P'
			pairlist = []; self.buttonProcess.set_label('Queue')	
			makeviewlist(self); showImage(self)
		
	def buttonProcess(self, button):
		global warnings, view, pairlist, viewtext #viewtext 154
		# local okleft, okright
		# pairlist filename style is name less last digit (no 3D at start)		
		warnings = ''
		if pairlist == []: 
			firstlist = [];	warnings = ''
			
			if scope == 'Folder': # store one filename for each set in firstlist
				for newfile in os.listdir(myfold):
					newfile, newext = os.path.splitext(newfile) ; newext = newext[1:]
					if len(newfile) > 1:
						if (newext in okext
						 and newfile[-1] in okchar 
						 and [newfile[:-1], formatcode, stylecode, newext] not in firstlist):
							firstlist.append([newfile[:-1], formatcode, stylecode, newext])

			elif scope == 'Set': #store one filename for the set in firstlist
				if (myfile != '{None}' and myext != '{None}'
				 and [myfile, formatcode, stylecode, myext] not in firstlist): #135
					firstlist.append([myfile, formatcode, stylecode, myext])

			# create pairs
			firstlist = sorted(firstlist)		
			for record in firstlist:
				makepairlist(self, record[0], record[1], record[2], record[3])
			firstlist = []

			if pairlist != []:
				viewtext = '' 
				for record in pairlist: #need this rather than firstlist to get left and right letters
					viewtext = viewtext+record[0]+record[1]+record[2]+formatcode+stylecode+'.'+record[5]+'\n'	
					self.labelViewing.set_text(viewtext)		
				self.buttonProcess.set_label('Process')		
			else:
				showMessage(self,	'warn', 'Nothing to process.')			

		else: #list not empty so process them
			self.image1.clear(); self.labelImage1.set_text('')

			warnings = ''
			for i in pairlist: # open images and get image type and size
				try:
					image = Image.open(myfold+i[0]+i[1]+'.'+i[5])
					imageLeftFormat = image.format ; imageLeftSize = image.size
					okleft = True
					image.close
				except:
					warnings = warnings +'Unable to load left image '+myfold+i[0]+i[1]+'.'+i[5]+'.\n'
					okleft = False
					image.close

				try:
					image = Image.open(myfold+i[0]+i[2]+'.'+i[5])
					imageRightFormat = image.format ; imageRightSize = image.size
					okright = True
					image.close
				except:
					warnings = warnings +'Unable to load right image '+myfold+i[0]+i[2]+'.'+i[5]+'.\n'
					okright = False
					image.close
			
				if okleft and okright:
					# if images match on type and size align them, else skip and warn
					if (imageLeftFormat == imageRightFormat
					and imageLeftSize == imageRightSize):
						processPair(self,i[0],i[1],i[2],i[3],i[4],i[5]) 
					else:
						if imageLeftFormat != imageRightFormat:
							warnings = warnings +i[0]+i[1]+'.'+i[5]+' and '+i[0]+i[2]+'.'+i[5]+' can not be used as they have different filetypes.\n'
						if imageLeftSize != imageRightSize:
							warnings = warnings +i[0]+i[1]+'.'+i[5]+' '+str(imageLeftSize)+' and '+i[0]+i[2]+'.'+i[5]+' '+str(imageRightSize)+' can not be used as their dimensions do not match.\n'

			if warnings != '':
				showMessage(self, 'warn', warnings)

			pairlist = []; self.buttonProcess.set_label('Queue')	
			view = '3D';  makeviewlist(self); showImage(self)
			self.buttonProcess.set_label('Queue')
			
	def buttonBack(self, menuitem):
		global firstpress
		findNext('<')		
		firstpress = False
		showImage(self)
				
	def buttonForward(self, menuitem):
		global firstpress
		if not firstpress: #it's already on first image, this is so it shows first image rather than going to second.
			findNext('>')	
		firstpress = False
		showImage(self)		
				
	def buttonDelete(self, button): #menuitem
		global viewind
		#local ok

		if len(viewlist) > 0:
			if os.path.isfile(myfold+viewlist[viewind][0]+'.'+viewlist[viewind][1]):
				if viewlist[viewind][2] == '3D':			
					result = showMessage(self, 'ask', 'Delete ' + viewlist[viewind][0]+'.'+viewlist[viewind][1] + '?')
					if result == 'Yes':
						self.image1.clear() ; self.labelImage1.set_text('')
						self.imageL.clear() ; self.labelImageL.set_text('')
						self.imageR.clear() ; self.labelImageR.set_text('')
						#1.5.3
						ok = True 
						try: 
							os.remove(myfold+viewlist[viewind][0]+'.'+viewlist[viewind][1])
						except:
							ok = False
							showMessage(self,	'warn', 'File already deleted.')
						if ok:
							makeviewlist(self); findNext('<'); showImage(self) 
				else:
					showMessage(self, 'warn', 'Only 3D images can be deleted.')							
			else:
				showMessage(self, 'warn', 'Image does not exist.')							
		else:
			showMessage(self, 'warn', 'No 3D images to delete.')							

	def __init__(self):
		self.glade = datafold+gladefile

		self.builder = Gtk.Builder()
		self.builder.add_from_file(self.glade)		 
		self.builder.connect_signals(self)
		 
		self.window = self.builder.get_object('window')
		self.image1 = self.builder.get_object('image1')
		self.imageL = self.builder.get_object('imageL')
		self.imageR = self.builder.get_object('imageR')

		self.labelImage1 = self.builder.get_object('labelImage1')
		self.labelImageL = self.builder.get_object('labelImageL')
		self.labelImageR = self.builder.get_object('labelImageR')
		
		self.labelViewing = self.builder.get_object('labelViewing')
		self.labelViewingTitle = self.builder.get_object('labelViewingTitle')

		self.buttonProcess = self.builder.get_object('buttonProcess')
				
		self.dialogHelp = self.builder.get_object('dialogHelp')
		self.buttonClose = self.builder.get_object('buttonClose')
		
		self.dialogboxAbout = self.builder.get_object('dialogboxAbout')

		self.messageQuestion = self.builder.get_object('messagedialogQuestion')
		self.messageWarning = self.builder.get_object('messagedialogWarning')
		#153 self.messageInfo = self.builder.get_object('messagedialogInfo')
		self.messageFirst = self.builder.get_object('messagedialogFirst')

		# for reading buttons		
		self.radiobuttontoggledAll = self.builder.get_object('radiobuttontoggledAll')
		self.radiobuttontoggled2D = self.builder.get_object('radiobuttontoggled2D')
		self.radiobuttontoggled3D = self.builder.get_object('radiobuttontoggled3D')
		self.radiobuttontoggledTriptych = self.builder.get_object('radiobuttontoggledTriptych')
		
		self.radiobuttontoggledAnaglyph = self.builder.get_object('radiobuttontoggledAnaglyph')
		self.radiobuttontoggledSidebyside = self.builder.get_object('radiobuttontoggledSidebyside')
		self.radiobuttontoggledCrossover = self.builder.get_object('radiobuttontoggledCrossover')

		self.radiobuttontoggledNormal = self.builder.get_object('radiobuttontoggledNormal')		
		self.radiobuttontoggledPopout = self.builder.get_object('radiobuttontoggledPopout')

		# for setting buttons				
		self.radiobuttonAll = self.builder.get_object('radiobuttonAll')
		self.radiobutton2D = self.builder.get_object('radiobutton2D')
		self.radiobutton3D = self.builder.get_object('radiobutton3D')
		self.radiobuttonTriptych = self.builder.get_object('radiobuttonTriptych')
		
		self.radiobuttonAnaglyph = self.builder.get_object('radiobuttonAnaglyph')
		self.radiobuttonSidebyside = self.builder.get_object('radiobuttonSidebyside')
		self.radiobuttonCrossover = self.builder.get_object('radiobuttonCrossover')
		
		self.radiobuttonNormal = self.builder.get_object('radiobuttonNormal')		
		self.radiobuttonPopout = self.builder.get_object('radiobuttonPopout')
	
		self.window.show(); self.window.maximize()

		#=======================================================================		 
		# set preference variables and set title
		getpreferences()

		#if scope == 'Set': #~~~
		#	self.window.set_title(version + '			Set: ' + myfile + '*.' + myext)
		#else:
		#	self.window.set_title(version + '			Folder: ' + myfold)
			 
		if formatcode == 'S': # Side-by-Side
			self.radiobuttonSidebyside.set_active(True)
		elif formatcode == 'C': # Crossover
			self.radiobuttonCrossover.set_active(True)
		else:
			self.radiobuttonAnaglyph.set_active(True)

		if stylecode == 'P': # Popout
			self.radiobuttonPopout.set_active(True)
		else: # Normal
			self.radiobuttonNormal.set_active(True)

		if view == '2D':
			self.radiobutton2D.set_active(True)
		elif view == '3D':
			self.radiobutton3D.set_active(True)
		elif view == 'Triptych':
			self.radiobuttonTriptych.set_active(True)
		else: # All
			self.radiobuttonAll.set_active(True)			

		if firstrun:
			self.result = self.messageFirst.run() ; self.messageFirst.hide()

		makeviewlist(self); showImage(self)
		
#===============================================================================
if __name__ == '__main__':	
	main = GUI()	
	Gtk.main()
