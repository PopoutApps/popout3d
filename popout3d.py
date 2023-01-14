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
import sys, os, shutil, subprocess, shlex, glob #153 remove colorsys, math add glob
#from PIL import Image, ExifTags, ImageOps, __version__ #153 remove ImageEnhance add ImageOps for orientation
from PIL import Image, ImageOps, __version__ #153 remove ImageEnhance add ImageOps for orientation
from PIL.ExifTags import TAGS

import multiprocessing

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
version = 'Popout3D V1.5.4'
firstrun = True
firstimage = True							# whether this is firstimage

view = 'All'									# which sort of images to show
viewlist = []									# list of images to view
viewind = 0										# index of image to view
viewtext = ''

dummyfile = 'dummy.png'       # grey image to display when one is missing.
blankfile = 'blank.png'       # blank image to display for clearing.
gladefile = 'popout3d.glade'
preffile = 'popout3d.dat'			# user preference file
myfile = ''										# current file
myext = ''										# current extension
# myfold mustn't be defined
scope = 'Folder'

formatcode = 'A'							# first letter of format
stylecode = 'N'								# first letter of style
pairlist = []								  # list of pairs to process
warnings = ''									# list of Processed warnings

okchar = ['0','1','2','3','4','5','6','7','8','9','L','R'] #last char in 2D filename
okext	= ['jpg','JPG','jpeg','JPEG','png','PNG','tif','TIF','tiff','TIFF']
okformat = ['A','S','C']			# Anaglyph/Side-by-Side/Crossover
okstyle	= ['N','P'] 					# Normal/Popout

resettable = False						# whether to show only recently processed files 32X 
blockfile = 'BLOCK'						# to show that multiprocessing is running
stopfile  = 'STOP'						# to tell multiprocessing to stop

'''
Added by 'exalm':
	$XDG_DATA_HOME defines the base directory relative to which user specific data files should be stored. 
	If $XDG_DATA_HOME is either not set or empty, a default equal to $HOME/.local/share should be used.
	Done.
	$XDG_CONFIG_HOME defines the base directory relative to which user specific configuration files should be stored. 
	If $XDG_CONFIG_HOME is either not set or empty, a default equal to $HOME/.config should be used.
	Not done.
'''

# home folder
homefold = os.getenv('XDG_HOME')
if homefold == None:
	homefold = os.getenv('HOME')
homefold = homefold + '/'

# work folder for processing files
workfold = homefold + '.popout3d/'
if os.path.isdir(workfold):
	shutil.rmtree(workfold, True)

result = os.system('mkdir '+ workfold)
if result != 0:
	print('Cannot create work directory')
	sys.exit(result)

# config folder for preference file
configfold = os.getenv('XDG_CONFIG_HOME')
if configfold == None:
	configfold = os.getenv('HOME') + '/.config/popout3d'
configfold = configfold + '/'
	
# project folder (read-only) for Glade file, dummy image and blank image
if os.path.exists('/.flatpak-info'): #This is within the sandbox so can't be seen
	datafold = '/app/share/popout3d/'
else: # no package for testing
	datafold = '/home/chris/git/popout3d/'

#print(os.getcwd())
#print('homefold = ', homefold)
#print('workfold = ', workfold)
#print('configfold = ', configfold)
#print('datafold = ', datafold)

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
			infile.close()	
	except:
		okpref = False

	if okpref:
		if not prefdata[0] == version:
			okpref = False
	
	if okpref:			
		if os.path.exists(prefdata[1]):
			myfold = prefdata[1]
		else:
			myfold = homefold #1.5.31
		
		myfile = prefdata[2] ; myext = prefdata[3]; scope = 'Set'
		#153 note this doesn't check the ? character is valid, but it shouldn't be possible
		# to save an invalid one. Should only occur if preference file was edited
		if not glob.glob(myfold+'/'+myfile+'?.'+myext): 
			myfile == ''; myext == ''; scope = 'Folder' #1.5.31
		
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

	if okpref:
 		firstrun = False
	else: # defaults
		#version
		myfold = homefold #1.5.31
		myfile = '' #1.5.31
		myext = '' #1.5.31
		formatcode = 'A'
		stylecode = 'N'
		view = 'All'

	# write pref file anyway in case mydir/myfile have been deleted or any other problem
	with open(configfold + preffile, 'w') as fn:			
		fn.write(version+'\n')
		fn.write(myfold+'\n')
		fn.write(myfile+'\n')
		fn.write(myext+'\n')
		fn.write(formatcode+'\n')
		fn.write(stylecode+'\n')
		fn.write(view+'\n')
		fn.close()

#===============================================================================
def checklist(self): #32XX
	global pairlist
	#local warnings, existsLeft, existsRight, imageLeftFormat, imageRightFormat, imageLeftSize, imageRightSize
	warnings = ''

	for i in pairlist: # open images and get image type and size
		try:
			image = Image.open(myfold+i[0]+i[1]+'.'+i[5])
			imageLeftFormat = image.format ; imageLeftSize = image.size
			existsLeft = True
			image.close
		except:
			warnings = warnings +'Unable to load left image '+myfold+i[0]+i[1]+'.'+i[5]+'.\n'
			existsLeft = False
			pairlist.remove(i)				
		try:
			image = Image.open(myfold+i[0]+i[2]+'.'+i[5])
			imageRightFormat = image.format ; imageRightSize = image.size
			existsRight = True
			image.close
		except:
			warnings = warnings +'Unable to load right image '+myfold+i[0]+i[2]+'.'+i[5]+'.\n'
			existsRight = False
			pairlist.remove(i)
					
		if existsLeft and existsRight:
			if imageLeftFormat != imageRightFormat:
				warnings = warnings +i[0]+i[1]+'.'+i[5]+' and '+i[0]+i[2]+'.'+i[5]+' can not be used as they have different filetypes.\n'
				pairlist.remove(i)
			if imageLeftSize != imageRightSize:
				warnings = warnings +i[0]+i[1]+'.'+i[5]+' '+str(imageLeftSize)+' and '+i[0]+i[2]+'.'+i[5]+' '+str(imageRightSize)+' can not be used as their dimensions do not match.\n'
				pairlist.remove(i)
							
	if warnings != '':		
		showMessage(self, 'warn', warnings)

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
def exif(newfilename, newext):
	'''
	Open file, get tags, if processing turn and save the image.
	Returns orientation, except 'notfound' if file missing and 'tagerror' if exif flags not available.
	'''

	global pixbuf, error
	# local orientationTag
	
	orientationTag = 'None'
	if os.path.isfile(myfold+newfilename+'.'+newext):
		try:
			image = Image.open(myfold+newfilename+'.'+newext)
		except:
			return 'notfound'
	else:		
		return 'notfound'
	
	try:
		image_exif = image.getexif()
	except AssertionError as error:
		print('image.exif() error: ', error)
		image.close
		return 'tagerror'

	for tag_id in image_exif:
		tag=TAGS.get(tag_id,tag_id)
		data=image_exif.get(tag_id)
		if isinstance(data,bytes):
			try:
				data=data.decode()
			except:
				image.close
				return 'tagerror'	
		#print(f"{tag:20}:{data}")
		if tag == 'Orientation':
			orientationTag = str(data)

	image.close
	return orientationTag

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
			
#===============================================================================
def findNext(direction):
	global viewind
	#local found

	newviewind = viewind
	if direction == '>':
		newviewind = newviewind +1
	else:
		newviewind = newviewind -1

	found = False
	while found == False and len(viewlist) > 0 and newviewind > -1 and newviewind < len(viewlist): 
		if (view in ('All', '3D', 'Triptych') and viewlist[newviewind][2] == '3D') or (view in ('All', '2D') and viewlist[newviewind][2] == '2D'):
			found = True	
			viewind = newviewind
			return
		elif direction == '>':
			newviewind = newviewind +1
		else:
			newviewind = newviewind -1

	# a further image wasn't found, leave viewind as it is.
		
#===============================================================================
def showImage(self):

	#local newfilename1, newfilenameL, newfilenameR, newext1, newextL, newextR
	self.labelImage1.set_text(''); self.labelImageL.set_text(''); self.labelImageR.set_text('')
	self.image1.clear(); self.imageL.clear(); self.imageR.clear()
	
	allocation = self.window.get_allocation()
	width = int(allocation.width*7/10); height = int(allocation.height*8/10)

	# valid image 
	if not firstimage and len(viewlist) > 0 and viewind > -1 and (
																																(view in ('All', '3D', 'Triptych') and viewlist[viewind][2] == '3D')
																																or
																																(view in ('All', '2D') and viewlist[viewind][2] == '2D')
																																):
					
		# two 2D images for triptych	
		if view == 'Triptych':
			width = int(width/2) ; height = int(height/2)

			# Left 2D image
			newfilenameL = viewlist[viewind][0][:-4]+viewlist[viewind][0][-4]; newextL = viewlist[viewind][1]
			self.labelImageL.set_text(newfilenameL+'.'+newextL)

			#orientationL = exif(newfilenameL, newextL)
			orientationL = viewlist[viewind][3]
			
			if orientationL == '3': # upside down, so rotate 180 clockwise
				pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilenameL+'.'+newextL, width, height, True), 180)
			elif orientationL == '6': # top at right so rotate 270 clockwise
				pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilenameL+'.'+newextL, height, width, True), 270)
			elif orientationL == '8': #top pointing left so rotate 90 clockwise
				pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilenameL+'.'+newextL, height, width, True), 90)
			elif orientationL == 'notfound':
				pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(datafold+dummyfile, width, height, True)
			else:
				pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilenameL+'.'+newextL, width, height, True)
			self.imageL.set_from_pixbuf(pixbuf)

			# Right 2D image
			newfilenameR = viewlist[viewind][0][:-4]+viewlist[viewind][0][-3]; newextR = viewlist[viewind][1]
			self.labelImageR.set_text(newfilenameR+'.'+newextR)

			#orientationR = exif(newfilenameR, newextR)
			orientationR = viewlist[viewind][3]
			if orientationR == '3': # upside down, so rotate 180 clockwise
				pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilenameR+'.'+newextR, width, height, True), 180)
			elif orientationR == '6': # top at right so rotate 270 clockwise
				pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilenameR+'.'+newextR, height, width, True), 270)
			elif orientationR == '8': #top pointing left so rotate 90 clockwise
				pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilenameR+'.'+newextR, height, width, True), 90)
			elif orientationR == 'notfound':
				pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(datafold+dummyfile, width, height, True)
			else:
				pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilenameR+'.'+newextR, width, height, True)
			self.imageR.set_from_pixbuf(pixbuf)

		# image 1 must be last so it doesn't take all the space in a Triptych
		# select currently indicated image from viewlist			
		newfilename1 = viewlist[viewind][0]; newext1 = viewlist[viewind][1]
		self.labelImage1.set_text(newfilename1+'.'+newext1)
		
		if os.path.isfile(myfold+newfilename1+'.'+newext1): #32XXXX
			#orientation1 = exif(newfilename1, newext1)
			orientation1 = viewlist[viewind][3]
			if orientation1 == '3': # upside down, so rotate 180 clockwise
				pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilename1+'.'+newext1, width, height, True), 180)
			elif orientation1 == '6': # top at right so rotate 270 clockwise
				pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilename1+'.'+newext1, height, width, True), 270)
			elif orientation1 == '8': #top pointing left so rotate 90 clockwise
				pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilename1+'.'+newext1, height, width, True), 90)
			elif orientation1 == 'notfound': # file missing
				pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(datafold+dummyfile, width, height, True)
			else: #already upright or could not be determined
				pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(myfold+newfilename1+'.'+newext1, width, height, True)
		else: # not found
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(datafold+dummyfile, width, height, True)
		self.image1.set_from_pixbuf(pixbuf)

#===============================================================================
def makeviewlist(self):
	global viewlist, viewind, pairlist
	#local variables newfile, newext, viewtext, tag
	tag = 'TAG'

	viewlist = []
	for newfile in os.listdir(myfold):			 
		newfile, newext = os.path.splitext(newfile) ; newext = newext[1:]		
		if len(newfile) > 1:
			if newext in okext and newfile[-1] in okchar:
				# set: only add files in set to viewlist
				if scope == 'Set':
					if len(newfile) == len(myfile) +1:
						if newfile[0:-1] == myfile and newext == myext:
							tag = exif(newfile, newext)
							viewlist.append([newfile, newext, '2D', tag])

				# folder: add all files to viewlist
				elif scope == 'Folder':
					tag = exif(newfile, newext)
					viewlist.append([newfile, newext, '2D', tag])

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
							tag = exif(newfile, newext) #32XX
							viewlist.append([newfile, newext, '3D', tag])

				# folder: add all files to viewlist
				elif scope == 'Folder':
					tag = exif(newfile, newext) #32XX						
					viewlist.append([newfile, newext, '3D', tag])

		viewlist = sorted(viewlist)

	self.image1.clear() ; self.labelImage1.set_text('') #32X

	'''#32X

	#Window title
	if scope == 'Folder':
		self.window.set_title(version + '			Folder: ' + myfold)
	else:
		self.window.set_title(version + '			Set: ' + myfold + myfile + '*.' + myext)
	'''	

def makeviewlabel(self):		

	# Viewing title
	if view == 'All':
		self.labelViewingTitle.set_label('All Images')
	elif view == '2D':
		self.labelViewingTitle.set_label('2D Images')
	elif view in ('3D', 'Triptych'):
		self.labelViewingTitle.set_label('3D Images')

	if resettable: #32XXXX
		if os.path.isfile(workfold+blockfile):
			self.labelViewingTitle.set_label(self.labelViewingTitle.get_label() + ' - being processed') 	
		else:
			self.labelViewingTitle.set_label(self.labelViewingTitle.get_label() + ' - finished')

def makeviewtext(self):		

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
		viewtext = '' #1.5.31

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
					tagL = exif(newfile+str(leftn), newext)
					tagR = exif(newfile+str(rightn), newext)
					pairlist.append([newfile, str(leftn), str(rightn), newformatcode, newstylecode, newext, tagL, tagR])
				rightn = rightn + 1
			leftn = leftn + 1

		# look for images ending in L and R
		if (os.path.isfile(myfold+newfile+'L'+'.'+newext) and os.path.isfile(myfold+newfile+'R'+'.'+newext)
 		 and not os.path.isfile(myfold+newfile+'LR'+newformatcode+newstylecode+'.'+newext)) and [newfile, 'L', 'R', newformatcode, newstylecode, newext] not in pairlist:
			tagL = exif(newfile+str(leftn), newext)
			tagR = exif(newfile+str(rightn), newext)
			pairlist.append([newfile, 'L', 'R', newformatcode, newstylecode, newext, tagL, tagR])

#===============================================================================
def processPairlist(pairlist):
	#global warnings
	#local tagL, tagR, foldL, foldR
	
	with open(workfold + blockfile, 'w') as fn:			
		fn.write('BLOCK'+'\n')
		fn.close()

	for record in pairlist:
		if os.path.isfile(workfold+stopfile):
			break
			
		newfile = record[0]; leftn = record[1]; rightn = record[2]; newformatcode = record[3]; newstylecode = record[4]; newext = record[5]; tagL = record[6]; tagR = record[7]
		
		# make filenames then call align_image_stack
		fileout	= newfile+leftn+rightn+newformatcode+newstylecode+'.'+newext
		fileleft	= newfile+leftn+'.'+newext
		fileright = newfile+rightn+'.'+newext

		# turn image if needed and put into workfold
		foldL = foldR = myfold	
		if tagL in ['3', '6', '8']: #32XXX rotate image	
			if os.path.isfile(myfold+fileleft):
				try:
					image = Image.open(myfold+fileleft)
					image = ImageOps.exif_transpose(image)
					image.save(workfold+fileleft, quality=95, subsampling='4:4:4')
					foldL = workfold
				except:
					pass	

		if tagR in ['3', '6', '8']: #32XXX rotate image	
			if os.path.isfile(myfold+fileright):
				try:
					image = Image.open(myfold+fileright)
					image = ImageOps.exif_transpose(image)
					image.save(workfold+fileright, quality=95, subsampling='4:4:4')
					foldR = workfold	
				except:
					pass	
		
		#replace A and P with styleAIS
		if stylecode == 'N':		
			styleAIS = 'A'
		else:
			styleAIS = 'P'

		#command	 = 'align_image_stack -a "'+workfold+fileout+'" -m -i -P -C "'+workfold+'right.'+newext+'" "'+workfold+'left.'+newext+'"' 
		#command	 = 'align_image_stack -a "'+workfold+fileout+'" -m -i --use-given-order -"'+styleAIS+'" -C "'+foldR+fileright+'" "'+foldL+fileleft+'"' #-v {verbose}
		command	 = 'align_image_stack -a "'+workfold+fileout+'" -"'+styleAIS+'" -C "'+foldR+fileright+'" "'+foldL+fileleft+'"' #-v {verbose} #-i favour centre of images

		args = shlex.split(command) 
		
		print('Aligning ', workfold+fileout) # For checking which files cause the problem
		result = os.system(command)
 		
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
				Lred	 = image_left.getchannel('R')
				Rgreen = image_right.getchannel('G')
				Rblue	 = image_right.getchannel('B')
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
			pass# warnings = warnings + 'It was not possible to align '+fileout+'.\n'
		
	if os.path.isfile(workfold+blockfile):
			os.remove(workfold+blockfile)

#===============================================================================
#===============================================================================
# Load the UI, define UI class and actions
class GUI:

	def on_window1_destroy(self, object): # close window with 0 or X
		with open(workfold+stopfile, 'w') as fn:			
			fn.write('STOP'+'\n'); fn.close()
		Gtk.main_quit()

	def menuitemQuit(self, menuitem): # quit with File > Quit
		with open(workfold+stopfile, 'w') as fn:			
			fn.write('STOP'+'\n'); fn.close()
		Gtk.main_quit()

	def menuitemFolder(self, menuitem):
		global myfold, myfile, myext, scope, pairlist, viewind#, firstimage
		global resettable
		resettable = False #32X
			
		filechooser = Gtk.FileChooserNative.new(title='Select the Folder where the images are', parent = self.window, action=Gtk.FileChooserAction.SELECT_FOLDER)
		filechooser.set_current_folder(myfold)
		response = filechooser.run();
		filechooser.hide()

		if response == Gtk.ResponseType.ACCEPT:	
			newfold = filechooser.get_filename()
			newfold = newfold+'/'	
			myfold = newfold; os.chdir(myfold) 
			myfile = ''; myext = '' #1.5.31 
			pairlist = []; self.buttonProcess.set_label('Queue')	
			scope = 'Folder'
			makeviewlist(self); makeviewlabel(self); makeviewtext(self); viewind = 0; findNext('<') # firstimage = True
			if len(viewlist) > 0: #1.5.31
				if not  (
								(view in('All', '3D', 'Triptych') and viewlist[viewind][2] == '3D')
								or
								(view in ('All', '2D') and viewlist[viewind][2] == '2D')
								):
					findNext('>')
			self.window.set_title(version + '			Folder: ' + myfold)	#32X
			showImage(self)

	def menuitemSet(self, menuitem):
		global myfold, myfile, myext, scope, pairlist, viewind#, firstimage
		#local okfile
		global resettable
		resettable = False #32X

		filechooser = Gtk.FileChooserNative.new(title="Select any file from a set of images", parent = self.window, action = Gtk.FileChooserAction.OPEN)
		
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
			return #~ newfile = '' #1.5.31

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
					showMessage(self, 'warn', 'Filename must follow rules in Help on File Selection.')
					return
			else:
				showMessage(self, 'warn', 'Filename must follow rules in Help on File Selection.')
				return
			self.window.set_title(version + '			Set: ' + myfold + myfile + '*.' + myext) #4

		os.chdir(newfold)
		pairlist = []; self.buttonProcess.set_label('Queue')	
		scope = 'Set'

		makeviewlist(self); makeviewlabel(self); makeviewtext(self); viewind = 0; findNext('<') # firstimage = True
		if len(viewlist) > 0: #1.5.31
			if not  (
							(view in('All', '3D', 'Triptych') and viewlist[viewind][2] == '3D')
							or
							(view in ('All', '2D') and viewlist[viewind][2] == '2D')
							):
				findNext('>')
		showImage(self)
		
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
					fn.close()
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
			makeviewlabel(self); makeviewtext(self); findMatch(); showImage(self)
				
	def radiobuttontoggled2D(self, menuitem):
		global view
		if menuitem.get_active():
			view = '2D'
			makeviewlabel(self); makeviewtext(self); findMatch(); showImage(self)
			
	def radiobuttontoggled3D(self, menuitem):
		global view
		if menuitem.get_active():
			view = '3D'
			makeviewlabel(self); makeviewtext(self); findMatch(); showImage(self)
			
	def radiobuttontoggledTriptych(self, menuitem):
		global view
		if menuitem.get_active():
			view = 'Triptych'
			makeviewlabel(self); makeviewtext(self); findMatch(); showImage(self)
			
	def radiobuttontoggledAnaglyph(self, radiobutton):
		global formatcode, pairlist, viewind#~
		global resettable; resettable = False #32X
		if radiobutton.get_active():
			formatcode = 'A'			
			pairlist = []; self.buttonProcess.set_label('Queue')	
			makeviewlist(self); makeviewlabel(self); makeviewtext(self);	showImage(self)
						
	def radiobuttontoggledSidebyside(self, radiobutton):
		global formatcode, pairlist, viewind#~
		global resettable; resettable = False #32X
		if radiobutton.get_active():
			formatcode = 'S'
			pairlist = []; self.buttonProcess.set_label('Queue')	
			makeviewlist(self); makeviewlabel(self); makeviewtext(self);	showImage(self)
							
	def radiobuttontoggledCrossover(self, radiobutton):
		global formatcode, pairlist, viewind#~
		global resettable; resettable = False #32X
		if radiobutton.get_active():
			formatcode = 'C'
			pairlist = []; self.buttonProcess.set_label('Queue')	
			makeviewlist(self); makeviewlabel(self); makeviewtext(self);	showImage(self)

	def radiobuttontoggledNormal(self, radiobutton):
		global stylecode, pairlist, viewind#~
		global resettable; resettable = False #32X
		if radiobutton.get_active():
			stylecode = 'N'
			pairlist = []; self.buttonProcess.set_label('Queue')	
			makeviewlist(self); makeviewlabel(self); makeviewtext(self);	showImage(self)
		
	def radiobuttontoggledPopout(self, radiobutton):
		global stylecode, pairlist, viewind#~
		global resettable; resettable = False #32X
		if radiobutton.get_active():
			stylecode = 'P'
			pairlist = []; self.buttonProcess.set_label('Queue')	
			makeviewlist(self); makeviewlabel(self); makeviewtext(self);	showImage(self)
		
	def buttonProcess(self, button):
		global warnings, view, pairlist, viewtext, viewind
		global viewlist, resettable #32X
		# local okleft, okright, alive
		# pairlist filename style is name less last digit (no 3D at start)		

		warnings = ''

		# DO  NOTHING
		# Still processing - do nothing
		if os.path.isfile(workfold+blockfile):
			showMessage(self,	'warn', 'Please wait for the current processing to finish.')

		# RESET
		# Button on resettable, empty pairlist, reset processing
		elif pairlist == [] and resettable: 
			self.buttonProcess.set_label('Queue'); resettable = False
			makeviewlist(self); makeviewlabel(self); makeviewtext(self);	findMatch(); showImage(self)

		# QUEUE
		# empty pairlist - make the list
		elif pairlist == [] and not resettable: #32X 
			setlist = [];	warnings = ''
	
			#32XXX
			# viewlist record ['DONEtestL', 'png', '2D', '8']
			# setlist record ['DONEtest', 'A', 'N', 'jpg']
			# pairlist record ['DONEtest', 'L', 'R', 'A', 'N', 'jpg', '8', '8']
						
			# put one filename for each set into setlist
			for record in viewlist:
				if [record[0][:-1], formatcode, stylecode, record[1]] not in setlist:
					setlist.append([record[0][:-1], formatcode, stylecode, record[1]])				
			setlist = sorted(setlist)		

			# setlist record ['DONEtest', 'A', 'N', 'jpg']
			for record in setlist:
				makepairlist(self, record[0], record[1], record[2], record[3])				
			setlist = []	
			
			#32XX
			checklist(self) # remove any which don't match format and size.

			# pairlist record ['DONEtest', 'L', 'R', 'A', 'N', 'jpg', '8', '8']
			# viewlist record ['DONEtestL', 'png', '2D', '8']
		
			# make viewtext and templist of projected images
			if pairlist != []:			
				viewtext = ''; viewlist = [] 					
				for record in pairlist:
					# add projected 3D images to viewtext
					viewtext = viewtext+record[0]+record[1]+record[2]+formatcode+stylecode+'.'+record[5]+'\n'	
					# add all relevant images to viewlist
					viewlist.append([record[0]+record[1], record[5], '2D', record[6]])		
					viewlist.append([record[0]+record[1]+record[2]+record[3]+record[4], record[5], '3D', 'N/A'])		
					viewlist.append([record[0]+record[2], record[5], '2D', record[7]])		
					
				viewlist = sorted(viewlist)
				viewind = -1; showImage(self)
				
				self.labelViewing.set_text(viewtext)		
				self.buttonProcess.set_label('Process')		
				self.radiobutton3D.set_active(True) #~
				
			else: # empty list - warn nothing to process
				makeviewlist(self); makeviewlabel(self); makeviewtext(self); showImage(self) #32XXXX			
				showMessage(self,	'warn', 'Nothing to process.')
				
		# PROCESS
		else: # list not empty so process
			multi = multiprocessing.Process(target = processPairlist, args=(pairlist,))				
			multi.start()
			
			#processPairlist(pairlist)
					
			pairlist = []
			self.buttonProcess.set_label('Reset'); resettable = True	
			self.radiobutton3D.set_active(True)
			view = '3D'; viewind = -1
			
	def buttonBack(self, menuitem):
		global firstimage
		global viewtext #132XXXX
		findNext('<')		
		firstimage = False
		showImage(self)
		makeviewlabel(self)
									
	def buttonForward(self, menuitem):
		global firstimage
		global viewtext #132XXXX
		
		if not firstimage: #it's already on first image, this is so it shows first image rather than going to second.
			findNext('>')	
		firstimage = False
		showImage(self)		
		makeviewlabel(self)
				
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
							if not resettable:
								makeviewlist(self); makeviewlabel(self); makeviewtext(self); findNext('<'); showImage(self) 
				else:
					showMessage(self, 'warn', 'Only 3D images can be deleted.')							
			else:
				showMessage(self, 'warn', 'Image does not exist.')							
		else:
			showMessage(self, 'warn', 'No 3D images to delete.')							

	def __init__(self):
		global viewind#~
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
		if scope == 'Folder':
			self.window.set_title(version + '			Folder: ' + myfold)
		else:
			self.window.set_title(version + '			Set: ' + myfold + myfile + '*.' + myext)

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

		makeviewlist(self); makeviewlabel(self); makeviewtext(self); viewind = 0; findNext('<')
		if len(viewlist) > 0: #1.5.31
			if not  (
							(view in('All', '3D', 'Triptych') and viewlist[viewind][2] == '3D')
							or
							(view in ('All', '2D') and viewlist[viewind][2] == '2D')
							):
				findNext('>')
		showImage(self)

#===============================================================================
if __name__ == '__main__':	
	main = GUI()	
	Gtk.main()
