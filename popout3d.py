#! /usr/bin/python3


#RPM icon and logo files are OK, but must test for Flatpak, Snap and AppImage
test = True

'''
--------------------------------------------------------------------------------
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
#43 import warnings to suppress GTK deprecation warnings
import sys, os, shutil, shlex, glob, subprocess, threading, warnings 
#44 no longer using: shutil, subprocess, shlex, multiprocessing, numpy, cv 

#----------
warnings.filterwarnings("ignore", category=DeprecationWarning)
#----------
import gettext # No need to try as always present.

try:
	from PIL import Image, ImageOps, __version__ #DIFF, ImageChops #TEST WITH IMAGECHOPS
except ImportError:
	sys.exit('Failed to import PIL')

try:
	from PIL.ExifTags import TAGS
except ImportError:
	sys.exit('Failed to import TAGS')

#try:
#	import numpy as np
#except ImportError:
#	sys.exit('Failed to import np')

#try:
#	import cv2 # Fedora currently 4.10.0
#except ImportError:
#	sys.exit('Failed to import cv2')

try:
	import gi
except ImportError:
	sys.exit('Failed to import gi')

from gi.repository import Gtk, GdkPixbuf, Gio

try:
	gi.require_version('Gtk', '4.0')
except ImportError:
	sys.exit(f'gi wrong version: {gi.__version__}') #44

try:
	import locale
except ImportError:
		print('Cannot import locale')

try:
	import webbrowser
except ImportError:
		print('Cannot import webbrowser')

#-------------------------------------------------------------------------------
# create global variables and set default values
version = '1.6.45'							# formatted for "About"
firstrun = True

viewDim = 'All'									# which sort of images to show
viewType = 'ASCNP'							# which type of 3D images to show
viewlist = []										# list of images to view
viewind = 0											# index of image to view
infolist = ''

blankfile = 'blank.png'					# grey image to display when one is missing.

settingsfile = ''								# settings file [Snap]           >>>>>
settingsfile = 'popout3d.dat'		# settings file [RPM] tested [AppImage]

logofile = 'com.github.PopoutApps.popout3d'	# Musn't have .png OK for RPM 

myfile = ''											# current file
myext = ''											# current extension
# myfold mustn't be defined
scope = 'Folder'								# whether dealing with file set or folder

formatcode = 'A'								# first letter of format
stylecode = 'N'									# first letter of style
pairlist = []										# list of pairs to process
warnings = ''										# list of Processed warnings

okformat = ['A','S','C']				# Anaglyph/Side-by-Side/Crossover
okstyle	= ['N','P'] 						# Normal/Popout
okchar = ['0','1','2','3','4','5','6','7','8','9','L','R'] #last char in 2D filename
okext	= ['jpg','JPG','jpeg','JPEG','png','PNG','tif','TIF','tiff','TIFF']
tifext	= ['tif','TIF','tiff','TIFF']

processlist = False							# whether to show only recently processed files 32X 
#44 runningfile = 'RUNNING'					# to show that multiprocessing is running
#44 stopfile = 'STOP'								# to tell multiprocessing to stop
process = 'queue'								# queue/process/reset
retain = False									# whether to save aligned L and R images #43
balance = 1.5									# left right balance in Anaglyphs #43
urlForum = 'https://popout3d.proboards.com/' 
##44 name changes and 2 new ones
environment = ''								# environment in which the app is running
snap_path = '' 									# Find Snap package data directory 
homefold = ''										# initial location for looking for photographs.
configfold = ''									# the Config file.			
workfold = ''										# temporary images, STOP and RUNNING control files
datafold = ''										# root of tree for locale and programfold
programfold = ''								# additional program parts
localefold = ''									# localisation files
#44
logfile = 'align_errors.log'		# logfile for align_image_stack output so it can be disconnected from terminal
worker = None										# for align_image_stack process
stop_event = threading.Event()	# for align_image_stack process

#44 environment added and all revised ---------------------------------------
if 'SNAP' in os.environ:
	environment = 'snap'
elif os.environ.get("container") == "flatpak":
	environment = 'flatpak'
elif os.environ.get("_") == "/usr/bin/popout3d":
	environment = 'rpm'
else:
	environment = 'terminal'

if test:
	print ('<',environment,'>')

# Most environment variables aren't any good
#	gettext will add {language}/LC_MESSAGES to locale

# (RPM and AppImage set logofile, Snap didn't) out-of-date
if environment == 'terminal':
	homefold		= os.getenv('HOME')
	workfold		= os.getenv('XDG_RUNTIME_DIR')
	configfold	= homefold  + '/git/testdirs/home/.config'
	#programfold = homefold + '/git/testdirs/usr/share/popout3d' NBG
	programfold = homefold  + '/git/testdirs/usr/share/popout3d'
	localefold	= homefold  + '/git/testdirs/usr/share/locale'	
	#logofile = 'popout3d'
	
elif environment == 'rpm':
	homefold 		= os.getenv('HOME')
	workfold		= os.getenv('XDG_RUNTIME_DIR')
	configfold 	= homefold + '/.config/popout3d'  # as XDG_CONFIG_HOME is None
	programfold = '/usr/share/popout3d'						# as XDG_DATA_HOME is None
	localefold  = '/usr/share/locale'							# as XDG_DATA_HOME is None
	
elif environment == 'flatpak':
	homefold 		= os.getenv('HOME')
	workfold		= os.getenv('XDG_RUNTIME_DIR')
	configfold 	= os.getenv('XDG_CONFIG_HOME')
	programfold = '/app/share/popout3d'
	localefold  = '/app/share/locale'
	#logofile = 'popout3d' #AppImage
	
elif environment == 'snap': #FROM SNAPFILE
	homefold 		= os.getenv('SNAP_REAL_HOME')
	workfold		= os.getenv('XDG_RUNTIME_DIR')
	configfold 	= os.getenv('XDG_CONFIG_HOME')
	snap_path 	= os.getenv('SNAP', '/')  # Default to '/' when not running in Snap
	programfold = os.path.join(snap_path, 'usr/share/popout3d') #OK
	localefold 	= os.path.join(snap_path, 'usr/share/locale')		#OK
	x = os.path.expanduser("~/.config/"); print('>>>',x,'<<<')	
	#configfold = os.path.expanduser("~/.config/")

	#logofile 		= 'popout3d'
	#logofile = 'com.github.PopoutApps.popout3d' #FROM AppImage file
 	
	#elif environment == 'snap': #FROM RPM FILE
	#	homefold 		= os.getenv('SNAP_REAL_HOME')
	#	workfold		= os.getenv('XDG_RUNTIME_DIR')
	#	configfold 	= os.getenv('XDG_CONFIG_HOME')
	#	#programfold = '/snap/popout3d/current/usr/share'
	#	programfold = 'SNAP/usr/share/popout3d'
	#	#localefold 	= '/snap/popout3d/current/usr/share/locale'	#localefold 	= 'SNAP/usr/share/popout3d/locale'
	#	locale_folder = os.path.join(os.environ["SNAP"], "usr", "share", "locale")

	#	logofile 		= 'popout3d'

else:
  sys.exit('Cannot work out environment: ', environment)

homefold = homefold + '/'
workfold = workfold + '/'
configfold = configfold +'/'	
programfold = programfold + '/'
localefold = localefold + '/'

if test:
	print('------------------------------------------------------')
	print('Environment:\t', environment)
	print('HOME\t\t', os.getenv('HOME'), os.getenv('SNAP_REAL_HOME'))
	print('CONFIG\t\t', os.getenv('XDG_CONFIG_HOME'))
	print('RUNTIME\t\t', os.getenv('XDG_RUNTIME_DIR'))
	print('DATA\t\t', os.getenv('XDG_DATA_HOME'))
	print('')
	print('homefold:\t', homefold)
	print('configfold:\t', configfold)
	print('workfold:\t', workfold)
	print('programfold:\t', programfold)
	print('localefold:\t', localefold)
	print('------------------------------------------------------')
	#TEST = os.getenv('SNAP_USER_COMMON'); print('<<<<<',TEST,'>>>>>')
	x = os.path.expanduser("~/.config/"); print(x)

'''
CONTROL FILES, WILL THEY BE HERE NEXT RUN? - NOT SURE THEY SHOULD BE HERE?	These arent permanent but need to be kept between sessions (1 does anyway)
Correct places?
	if os.path.isdir(workfold):											#if it exists, remove workdir and its files
		shutil.rmtree(workfold, True)

	result = os.system('mkdir ' + workfold)					#try making work directory
	if result !=0:
		sys.exit('Cannot make work directory')			#cannot make work directory so exit			

'''

#locale-------------------------------------------------------------------------
locale.setlocale(locale.LC_ALL, '')
language = locale.getlocale()[0] 
lang = gettext.translation('popout3d', localedir=localefold, languages=[language], fallback=True)
_ = lang.gettext

# Help pages -------------------------------------------------------------------
#44 Revised help text and one command text.

helpPage = []

# Basics -----------------------------------------------------------------------
helpPage.append(_('''You need two photos of a stationary subject. Take one, then move the camera about 60mm to the right but pointing at the same part of the subject and take another. Copy them to your PC, then rename them so that they have the same name, but with an "L" at the end of the left-hand one and an "R" at the end of the right-hand one. For example photoL.JPG and photoR.JPG.

Open Popout3D and select one of these photos with Open>File. Click Queue to see what 3D images will be created. The button changes to Process. Click Process to start processing. The button changes to Reset. If you use the < and > arrows, you will see a grey rectangle while the image is being created. When the 3D image is ready, it will be displayed if you use the arrows. This can take about half a minute.

You will need 3D glasses to see anaglyph images. You will need 3D Virtual Reality goggles to see side-by-side images. Some people can see side-by-side or crossover images without goggles.

Popout3D Forum https://popout3d.proboards.com/'''))

# Source Files -----------------------------------------------------------------
helpPage.append(_('''Choose a stationary subject. Take one photo, then move the camera about 60mm to the right, point it at the same part of the subject, and take another. Always take them in sequence from left to right, so you don't get them mixed up. It's best to copy your original photos onto your PC to process them. Rename them so that they both have the same name, but with an "L" at the end of the left-hand one and an "R" at the end of the right-hand one. For example photoL.JPG and photoR.JPG. If you find it difficult to get the camera postion right, you can take 3 or more photos at different separations. Name them in order from left to right in numerical order, for example photo1.jpg, photo2.jpg and photo3.jpg. Don't take too many, as this results in creating a large number of 3D images, which will take a long time to process.

Each set of images (all those intended for the same 3D image) must be in the same format with the same file-extension - .jpg, .png or .tiff. They must be exactly the same size in pixels.

Movement
Stationary objects like buildings or scenery give good results. Pictures of people should work, provided they can keep still for a few seconds. Objects like trees and water may work in the right circumstances, for example if there isn't too much wind, and the water is placid. Moving vehicles, people or animals, or fast-flowing water like a waterfall or waves won't work.

Quality of Effect
A picture with objects at varying distances results in a convincing effect. Distant scenery won't work well, as there is little perspective effect anyway.

Notes
Some images are too difficult for the aligning software, the result will just be a blank grey square.

For Anaglyph 3D, avoid images with all red or all cyan objects. They will look odd as they will only appear in one eye.

Cropping images - for Anaglyph 3D it is easiest to edit the 3D image. For Side-By-Side or Crossover ones you cannot do this, so you must crop the original 2D images. This can be difficult, because you must ensure that the edited photos have exactly the same height and width in pixels. You also need to keep most of the same content in both images without losing the difference in view point.

Nearby objects can cause strange effects when the camera's depth of field is high. A shorter exposure will reduce the depth of field.'''))

# File Selection----------------------------------------------------------------
helpPage.append(_('''File
To process a single set of 2D images which will all be used for the same 3D image, first use Open>File to choose any file from the set.

scenery1.jpg
scenery2.jpg
scenery3.jpg

Selecting any of these files will prepare you to process all of them. The program will create a 3D image for each pair of originals, so you are able to choose the best. It is not recommended to use more than 3 originals as the number of output images goes up dramatically:

2 originals produce 1 3D image
3 originals produce 3 3D images
4 originals produce 6 3D images
5 originals produce 10 3D images

All the 3D images in the set will get the same original filename as the originals with the final characters from both, followed by a letter for the 3D format and a letter for the style.

These examples are "Anaglyph" format with "Normal" style:

scenery12AN.jpg was made from scenery1.jpg for the left image and scenery2.jpg for the right.
scenery13AN.jpg was made from scenery1.jpg for the left image and scenery3.jpg for the right.

Images ending in L and R would give sceneryLRAN.jpg.

Folder:
To process all the image sets in a folder, use Open>Folder.'''))

# Options for 3D Images --------------------------------------------------------
helpPage.append(_('''The format of the 3D image may be:

Anaglyph
A red/cyan coloured 3D image viewed with coloured spectacles. These are available very cheaply on the Web.

Side-by-side
A side-by-side 3D image with the left-hand image on the left, the right-hand on the right. Some people can see these without a viewer, some can't.

Crossover
A side-by-side 3D image viewed with eyes crossed. The right-hand image is on the left, the left-hand on the right. Some people can see these without a viewer, some can't.

There are two styles available:

Normal
A normal 3D image with the front of the picture level with the screen.

Popout
A "popout" image. In some cases the effect is startling, as the front of the 3D image will stand out in front of the screen. In most cases there is little or no difference from "Normal".

Aligned 2D images
The processing creates aligned versions of the left and right images, which are then merged into a 3D image. These two images are only temporary. If you want to use them to try your own method of creating and displaying 3D images, you can save them by selecting "Aligned 2D Images>Save". They will remain after the processing has finished. They will have names like PhotoL(LRP).tif, the "LR" refers to the final identifying characters from the two original images. The "P" indicates that any 3D image you make from them will be a popout one.'''))

# Processing -------------------------------------------------------------------
#44 removed suggestion of trying Hugin.
helpPage.append(_('''For the 3D effect to work it is essential that each pair of images is perfectly aligned vertically and in rotation. This is very difficult to achieve when holding a camera and even by editing the 2D images. This program does it for you, it may take about 20 seconds per 3D image.

An existing 3D image will not be overwritten. Therefore if you wish to recreate a 3D image, you will first need to move, rename or delete the existing one.

To start processing the selected images, click on "Queue", this will show a list of the images to be created in the panel to the left and the button will change to "Process". If you don't like the list, choose another File/Folder or Format/Style.
If you are happy with list of images in the queue, press "Process", the button will change to "Reset". You can use the < and > buttons to look for completed 3D images. Only the recently processed images are shown. When you have finished checking them, press "Reset" to go back to the File or Folder selection, now including both old and new images. Using the Open menu or the Delete or process buttons will also reset the list.

Notes
Portrait images from a mobile phone may actually be landscape photos with a rotation tag, the program rotates them to portrait for processing, but it doesn't change the originals.

Mobile phones from one manufacturer are suspected of producing 16:9 photos which do not conform to JPG standards.

The 3D images won't have valid EXIF tags - date and so on.

Settings from previous versions of the program are not loaded.

If you can't remember which image was the left-hand one and which was the right-hand one, create an anaglyph 3D image. If it doesn't look right, try the glasses on upside down, so the lenses swap sides. If the image now works rename the 2D images and create a new 3D image. You can do something similar with Side-by-Side and Crossover images.
'''))

# View -------------------------------------------------------------------------
helpPage.append(_('''Scroll backwards and forwards through the images using < and >.

All
All the images in the chosen set or folder which follow the naming rules will be shown.

2D
Only 2D images in the chosen set or folder which follow the naming rules will be shown.

3D
Only 3D images in the chosen set or folder which follow the naming rules will be shown.

Triptych
3D images will be shown at the top with the 2D images they were made from shown beneath.

3D Image Types
These selections only affect 3D/Triptych views (see Processing for explanations). If you have created more than one type of 3D image, these buttons allow you to show only one type at a time.

Delete
If a 3D image is being displayed you may delete it. To ensure that you don't lose original images, 2D images cannot be deleted from within Popout3D. You could of course delete them using your file manager.

Notes
You may need to view 3D images from further away than you might expect.'''))

#-------------------------------------------------------------------------------
# tooltips
tipDelete			= _('Delete a 3D image')
tipQueue			= _('Make a queue of 3D images from the files selected by Folder or File')
tipProcess		= _('Create the 3D images shown in the queue')
tipReset			= _('Clear the list of processed images and show the list selected by Folder or File')
tipNext				= _('Show next image')
tipPrev				= _('Show previous image')
tipOpen				= _('Select a folder or file')
tipStripey		= _('Menu') 

tip2D					= _('Show only 2D images')
tipTriptych		= _('Show 3D images above the 2D images they came from')
tip3D					= _('Show only 3D images')
tipAll				= _('Show all images')
tipAnaglyph		= _('A 3D image with the left-hand image red and the right-hand image cyan')
tipSidebyside	= _('A 3D image with the left-hand image on the left and the right-hand image on the right')
tipCrossover	= _('A 3D image with the left-hand image on the right and the right-hand image on the left')
tipNormal 		= _('A normal 3D image')
tipPopout			= _('A 3D image which may appear to stand out in front of the screen')
tipRetain			= _('Save the aligned 2D images') #43, 44

#===============================================================================
#def on_close_request(app): # When window is closed with X
#44
def on_close_request(*args):
	global stop_event
	if stop_event:
		stop_event.set()
	return False  # allows GTK to actually close the window

	#with open(workfold + stopfile, 'w') as fn:			
	#	fn.write('STOP'+'\n')
	#	fn.close()

def processPairlist(stop_event, pairlist, myfold, workfold): #44 added everything after pairlist
	#global warnings
	#local tagL, tagR, foldL, foldR foldL and foldR are for when a portrait needs rotating
	#local log
	
	#44
	#with open(workfold + runningfile, 'w') as fn:			
	#	fn.write('RUNNING'+'\n')
	#	fn.close()
	if test:
		print()
	for record in pairlist:
		#44
		#if os.path.isfile(workfold+stopfile): 
		#	break
		if stop_event.is_set():
			print("Processing stopped by user")
			break			
		else:	
			newfile = record[0]; leftn = record[1]; rightn = record[2]; newformatcode = record[3]; newstylecode = record[4]; newext = record[5]; tagL = record[6]; tagR = record[7]
		
			# make filenames then call align_image_stack
			fileout	= newfile+leftn+rightn+newformatcode+newstylecode+'.'+newext
			fileleft	= newfile+leftn+'.'+newext
			fileright = newfile+rightn+'.'+newext

			# turn image if needed and put into workfold
			foldL = foldR = myfold	

			if test:
				print(myfold, workfold, fileout, fileleft, fileright)

			if tagL in ['3', '6', '8']: # rotate image	
				if os.path.isfile(myfold+fileleft):
					try:
						image = Image.open(myfold+fileleft)
						image = ImageOps.exif_transpose(image)
						#image.save(workfold+fileleft, quality=95, subsampling='4:4:4')
						if newext in tifext:
							image.save(workfold+fileleft) 
						else:
							image.save(workfold+fileleft, quality=95, subsampling='4:4:4')
						foldL = workfold
					except:
						pass	

			if tagR in ['3', '6', '8']: # rotate image	
				if os.path.isfile(myfold+fileright):
					try:
						image = Image.open(myfold+fileright)
						image = ImageOps.exif_transpose(image)
						#image.save(workfold+fileright, quality=95, subsampling='4:4:4')
						if newext in tifext:
							image.save(workfold+fileright) 
						else:
							image.save(workfold+fileright, quality=95, subsampling='4:4:4')
						foldR = workfold	
					except:
						pass	
		
			#replace A and P with styleAIS
			if stylecode == 'N':		
				styleAIS = 'A'
			else:
				styleAIS = 'P'

			if test:
				print(foldL+fileleft, foldR+fileright, workfold+fileout)
			command = 'align_image_stack -S -C -i --align-to-first --use-given-order -'+styleAIS+' -a '+workfold+fileout+' '+foldR+fileright+' '+foldL+fileleft #43
				
			args = shlex.split(command) 
		
			print('Aligning'+' ', workfold+fileout) # For checking which files cause the problem #43
			#result = os.system(command) #44			
			log = os.path.join(workfold, logfile)
			result = subprocess.run(
				command,
				shell=True,
				stdout=subprocess.DEVNULL,                # discard normal output
				stderr=open(log, "a"),                # append errors to a log file
				start_new_session=True                     # detach from terminal
				)
 		
			# remove turned images if they exist
			if os.path.isfile(workfold+fileleft):
				os.remove(workfold+fileleft)
			if os.path.isfile(workfold+fileright):
				os.remove(workfold+fileright)

			# align_image_stack has worked
			#if result == 0: #44
			if result.returncode == 0:

				# load left and right images
				image_left = Image.open(workfold+fileout+'0001.tif')
				image_right = Image.open(workfold+fileout+'0000.tif')

				# merge the files, put result in myfold
				if formatcode == 'A': # Anaglyph			
					Lred	 = image_left.getchannel('R')
					Rgreen = image_right.getchannel('G')
					Rblue	 = image_right.getchannel('B')

					#43 easter egg for anaglyph colour balance (not working)
					#if balance != 1:			
					#	Lred = Lred.point	(lambda i: i * balance)
					#	Rgreen = Rgreen.point	(lambda i: i * 1/balance)
					#	Rblue = Rblue.point	(lambda i: i * 1/balance)

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

				# attempt to avoid fringing but subsampling doesn't work for TIF files
				if newext in tifext:
					image_new.save(myfold+fileout) 
				else:
					image_new.save(myfold+fileout, quality=95, subsampling='4:4:4')

				# close delete input and delete intermediate files 
				image_left.close ; image_right.close
 
 				#DIFF IF POPOUT IS REMOVED, +newformatcode should be removed
				if test:
					print('Retain: ', retain)
				if os.path.isfile(workfold+fileout+'0001.tif'):
					if retain: #43
						shutil.copy(workfold+fileout+'0001.tif', myfold+newfile+leftn+'('+leftn+rightn+newformatcode+newstylecode+').tif') 
					os.remove(workfold+fileout+'0001.tif')
				if os.path.isfile(workfold+fileout+'0000.tif'):
					if retain: #43
						shutil.copy(workfold+fileout+'0000.tif', myfold+newfile+rightn+'('+leftn+rightn+newformatcode+newstylecode+').tif') 
					os.remove(workfold+fileout+'0000.tif') 
						
			else:
				print('Could not align error: ' + str(result) + ' ' + fileout + '\n' ) # warnings = warnings + 'It was not possible to align '+fileout+'.\n'  #43
	#44	
	#if os.path.isfile(workfold+runningfile):
	#		os.remove(workfold+runningfile)

	print('Finished') #43

def on_activate(app):
	global viewind, process
	##global image1, imageL, imageR, boxOuter1, boxImageL, boxImageR

	win = Gtk.ApplicationWindow(application=app)
	win.maximize()
	win.header = Gtk.HeaderBar()
	win.set_titlebar(win.header)
	win.present()
	win.connect('close-request', on_close_request)

	#-----------------------------------------------------------------------------
	def greyout(state): #43
		if state:
			GtickViewAnaglyph.set_sensitive(False)
			GtickViewSidebyside.set_sensitive(False)
			GtickViewCrossover.set_sensitive(False)
			GtickViewNormal.set_sensitive(False)
			GtickViewPopout.set_sensitive(False)
			#GbuttonDelete.set_sensitive(False)
		else:
			GtickViewAnaglyph.set_sensitive(True)
			GtickViewSidebyside.set_sensitive(True)
			GtickViewCrossover.set_sensitive(True)
			GtickViewNormal.set_sensitive(True)
			GtickViewPopout.set_sensitive(True)
			#GbuttonDelete.set_sensitive(True)

	def ask(widget, response, param):
		global viewind, process
		if response == Gtk.ResponseType.OK:
			if param == 'settings':
				with open(configfold + settingsfile, 'w') as fn:
					try:
						fn.write(version+'\n')
						fn.write(myfold+'\n')
						fn.write(myfile+'\n')
						fn.write(myext+'\n')
						fn.write(formatcode+'\n')
						fn.write(stylecode+'\n')
						fn.write(viewDim+'\n')
						fn.write(viewType+'\n')
						if retain:
							fn.write('True\n') #43
						else:
							fn.write('False\n') #43
						fn.write(str(balance)+'\n') #43
					except:
						print('Failed to write preference file')
			elif param == 'delete':
				ok = True 
				try: 
					os.remove(myfold + viewlist[viewind][0]+'.'+viewlist[viewind][1])
				except:
					ok = False
					showInfo(_('File not found'))
				if ok:
					if process == 'reset':
						labelInfoTitle.set_markup('<b>' + _(scope) + ' ' + _('Selection') +'</b>')
						GbuttonProcess.set_label(_('Queue')); process = 'queue'
						makeviewlist(False); viewind = 0
					findNext('<'); showImage() 					
		widget.destroy()
		
	#-----------------------------------------------------------------------------
	def showInfo(messtext):
		message = Gtk.MessageDialog(title = _('Information'), text = messtext)
		message.add_buttons(_('OK'), Gtk.ResponseType.OK)
		message.set_transient_for(win); message.set_modal(win)
		message.set_default_response(Gtk.ResponseType.OK)
		message.connect('response', ask, None)
		message.set_visible(True)

	def showDelete():
		message = Gtk.MessageDialog(title = _('Are you sure?'), 
			text = _('This will delete') +' ' + viewlist[viewind][0]+'.'+viewlist[viewind][1])
		message.add_buttons(_('Cancel'), Gtk.ResponseType.CANCEL, _('Delete'), Gtk.ResponseType.OK) #43
		message.set_transient_for(win); message.set_modal(win)		
		message.set_default_response(Gtk.ResponseType.OK)
		message.connect('response', ask, 'delete')
		message.set_visible(True)
	
	def showSettings(action, button):
		message = Gtk.MessageDialog(title = _('Are you sure?'), text = _('This will save your current settings as the defaults'))
		message.set_transient_for(win); message.set_modal(win)
		message.add_buttons(_('Cancel'), Gtk.ResponseType.CANCEL, _('Save'), Gtk.ResponseType.OK) #43
		message.set_default_response(Gtk.ResponseType.OK)
		message.connect('response', ask, 'settings')
		message.set_visible(True)
		
	def showAbout(action, button):
		message = Gtk.AboutDialog(transient_for=win, modal=True)
		# Comes from the standard icon so no need for directory
		message.set_logo_icon_name(logofile) # logofile MUST NOT HAVE .png on the end! from RPM. # MUST NOT HAVE directory name or .png on the end! from Snap
		message.set_program_name('Popout3D')
		message.set_version(version)
		message.set_comments(_('Create a 3D image from ordinary photographs'))
		message.set_website_label('Popout3D ' + _('on') + ' GitHub')
		message.set_website('https://github.com/PopoutApps/popout3d')
		message.set_copyright(_('Copyright') + ' 2022 - 2026 Chris Rogers')
		message.set_license_type(Gtk.License.GPL_3_0)
		message.set_authors(['PopoutApps']) # Shows under 'Created by' probably translated by GTK.
		message.add_credit_section(section_name=_('Image Alignment'), people=['Hugin']) 
		
		message.add_credit_section(section_name='Flatpak', people=['"chrisawi"', 'Alexander Mikhaylenko', 'Hubert Figuière', 'Bartłomiej Piotrowski','Nick Richards'])
		if environment == 'snap': #44
			message.add_credit_section(section_name=_('Snap Package'), people=['ChatGPT'])
		elif environment == 'rpm': #44
			message.add_credit_section(section_name=_('RPM Package'), people=['ChatGPT'])
		message.set_visible(True)

	def	showHelp(action, button):
		message = Gtk.Window()
		message.set_title(_('How to use Popout3D'))
		message.set_default_size(1000, 700)
		message.set_child(notebook)
		message.set_transient_for(win); message.set_modal(win)
		message.set_visible(True)
	
	def	showForum(action, button):
		result = webbrowser.open(urlForum)
		
	#def	showLocale(action, button):
	#	result = webbrowser.open(urlCrowdin)

	def readSettings():
		global version, myfold, myfile, myext, formatcode, stylecode, viewDim, scope, viewType, firstrun, retain, balance #43
		# local okpref, okcol, ver, i
		# Preference file is not present when program is installed, so shows whether this is the first run.

		# create settings array
		prefdata = []
		for i in range(10): #43
			prefdata.append('')

		# load settings file, if file not found or is wrong version skip to end
		# if any fields are bad, replace with default
		okpref = True
		try:
			with open(configfold + settingsfile, 'r') as infile:
				ver = infile.readline()[:-1]
				if ver != version:
					okpref = False				
		except:
			okpref = False
	
		if okpref:
			try:
				with open(configfold + settingsfile, 'r') as infile:
					for i in range(0, 10): #43
						prefdata[i] = infile.readline()
						prefdata[i] = prefdata[i][:-1]
			except:
				okpref = False

		if okpref:					
			if os.path.exists(prefdata[1]):
				myfold = prefdata[1]
			else:
				myfold = homefold #1.5.31
		
			myfile = prefdata[2] ; myext = prefdata[3]; scope = 'File'
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
				viewDim = prefdata[6]
			else:
				viewDim = 'All'
		
			if (prefdata[7][0] in 'A-' and prefdata[7][1] in 'S-' and prefdata[7][2] in 'C-' 
				and	prefdata[7][3] in 'N-' and prefdata[7][4] in 'P-'):
				viewType = prefdata[7]
			else:
				viewType = 'ASCNP'

			if prefdata[8] in ['True', 'False']: #43
				if prefdata[8] == 'True':
					retain = True
				else:
					retain = False
			else:
				retain = False

			try: #44
				balance = real(prefdata[9])
				if not (balance >= 75 and balance <= 125):
					balance = 100.0
			except:
				balance = 100.0

		if okpref:
			firstrun = False
		else: # defaults
			#version already set
			myfold = homefold #1.5.31
			myfile = '' #1.5.31
			myext = '' #1.5.31
			formatcode = 'A'
			stylecode = 'N'
			viewDim = 'All'
			viewType = 'ASCNP'
			retain = False #43
			balance = 100.0 #43
		
			# write pref file anyway in case mydir/myfile have been deleted or any other problem
			with open(configfold + settingsfile, 'w') as fn:			
				fn.write(version+'\n')
				fn.write(myfold+'\n')
				fn.write(myfile+'\n')
				fn.write(myext+'\n')
				fn.write(formatcode+'\n')
				fn.write(stylecode+'\n')
				fn.write(viewDim+'\n')
				fn.write(viewType+'\n')
				if retain:
					fn.write('True\n') #43
				else:
					fn.write('False\n') #43
				fn.write(str(balance)+'\n') #43

			print('<<< balance: ',balance,'>>>') #44

	#-----------------------------------------------------------------------------		 
	def exif(newfilename, newext):
		'''
		Open file, get tags, if processing turn and save the image.
		Returns orientation, except 'notfound' if file missing and 'tagerror' if exif flags not available.
		'''
		global pixbuf, error
		# local orientationTag

		orientationTag = '' #44 was 'None' which was confusable with None
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
			#print(f'{tag:20}:{data}')
			if tag == 'Orientation':
				orientationTag = str(data)

		image.close
		return orientationTag

	#-----------------------------------------------------------------------------
	def findVmatch():
		global viewind # local searchlength, charL, charR, viewindL, viewindR, viewindN

		if len(viewlist) > 0: #and viewDim != 'All': # Can use same image if switching viewDim to All
			searchfilename = viewlist[viewind][0]; searchlength = -1 
			searchext = viewlist[viewind][1]; imageDim = viewlist[viewind][2]
			charL = charR = ''; viewindL = viewindR = viewindN = -1

			if not (viewDim == 'All' or viewDim == imageDim or (viewDim == 'Triptych' and imageDim == '3D')):	
				# switching viewDim to 2D
				# get basic filename, length and 2 characters
				if viewDim == '2D' and imageDim == '3D':
					searchname = searchfilename[:-4];	searchlength = len(searchname)
					charL = searchfilename[-4]; charR = searchfilename[-3]

					# search through list
					viewindL = viewindR = viewindN = -1
					for record in viewlist:
						if record[1] == searchext and record[2] == '2D':					
							if viewindL < 0 and searchname+charL in record[0][:searchlength+1]:
								viewindL = viewlist.index(record) # L of 3D image matches a 2D image
							elif viewindR < 0 and searchname+charR in record[0][:searchlength+1]:
								viewindR = viewlist.index(record) # R of 3D image matches a 2D image
							elif viewindN < 0 and searchname in record[0][:searchlength]:
								viewindN = viewlist.index(record) # match for basic name
	
				# switching viewDim to 3D
				# get basic filename and 1 character
				elif viewDim in ('3D', 'Triptych') and imageDim == '2D':
					searchname = searchfilename[:-1];	searchlength = len(searchname)
					charL = searchfilename[-1]; charR = ''
			
					# search through list
					viewindL = viewindR = viewindN = -1
					for record in viewlist:
						if (record[1] == searchext and record[2] == '3D'
							and record[0][-2] in viewType and record[0][-1] in viewType):
							if viewindL < 0 and searchname+charL in record[0][:searchlength+1]:
								viewindL = viewlist.index(record) # char of 2D image matches 1st char of a 3D image
							elif viewindR < 0 and searchname+charL in record[0][:searchlength]+record[0][-3]:
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
					viewind = 0

	#-----------------------------------------------------------------------------
	def findFSmatch():
		global viewind # local searchlength, charL, charR, viewindL, viewindR, viewindN

		if len(viewlist) > 0:
			# Details of current image
			searchfilename = viewlist[viewind][0]; searchext = viewlist[viewind][1]
			searchname = searchfilename[:-4];	searchlength = len(searchname)
			charL = searchfilename[-4]; charR = searchfilename[-3]
			charF = searchfilename[-2]; charS = searchfilename[-1]

			# might be still valid, if not search viewlist
			if not (charF in viewType and charS in viewType): 
				viewindLR = viewindL = viewindR = viewindName = -1
				for record in viewlist:
					if (record[1] == searchext and record[2] == '3D'
						and record[0][-2] in viewType and record[0][-1] in viewType
						 ):
						if viewindLR < 0 and searchname+charL+charR in record[0][:searchlength+2]:
							viewindLR = viewlist.index(record) # both L and R chars match
						# rest same as 2D to 3D
						elif viewindL < 0 and searchname+charL in record[0][:searchlength+1]: 
							viewindL = viewlist.index(record) # charL matches
						elif viewindR < 0 and searchname+charL in record[0][:searchlength]+record[0][-3]:
							viewindR = viewlist.index(record) # charR matches
						elif viewindName < 0 and searchname in record[0][:searchlength]:
							viewindName = viewlist.index(record) # only basic name matches

				if viewindLR > -1:
					viewind = viewindLR
				elif viewindL > -1:
					viewind = viewindL
				elif viewindR > -1:
					viewind = viewindR
				elif viewindName > -1:
					viewind = viewindName
				else:
					viewind = 0

	#-----------------------------------------------------------------------------
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
			if ((viewDim in ('All', '3D', 'Triptych') and viewlist[newviewind][2] == '3D'
				and viewlist[newviewind][0][-2] in viewType and viewlist[newviewind][0][-1] in viewType)			
			 or (viewDim in ('All', '2D') and viewlist[newviewind][2] == '2D')
					):
				found = True	
				viewind = newviewind
				return
			elif direction == '>':
				newviewind = newviewind +1
			else:
				newviewind = newviewind -1

	# if a further image wasn't found, leave viewind as it is.
		 
	#-----------------------------------------------------------------------------
	def makepairlist(newfile, newformatcode, newstylecode, newext):
		global warnings, pairlist, infolist, viewDim
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

#-------------------------------------------------------------------------------
	def makeviewlist(queuing):
		global viewlist, viewind, pairlist
		#local variables newfile, newext, infolist, tag
		tag = 'TAG'
		viewlist = []

		if queuing:
			# add all relevant images to viewlist
			for record in pairlist:
				# Graceful stop request #44
				if stop_event.is_set():
					print("Stop requested")
					break		
				#viewlist.append([record[0]+record[1], record[5], '2D', record[6]])		
				viewlist.append([record[0]+record[1]+record[2]+record[3]+record[4], record[5], '3D', ''])	
				#viewlist.append([record[0]+record[2], record[5], '2D', record[7]])		
		else:
			# 2D
			for newfile in os.listdir(myfold):			 
				newfile, newext = os.path.splitext(newfile) ; newext = newext[1:]		
				if len(newfile) > 1:
					if newext in okext and newfile[-1] in okchar:
						# set: only add files in set to viewlist

						# file
						if scope == 'File':
							if len(newfile) == len(myfile) +1:
								if newfile[0:-1] == myfile and newext == myext:
									tag = exif(newfile, newext)
									viewlist.append([newfile, newext, '2D', tag])

						# folder
						elif scope == 'Folder':
							tag = exif(newfile, newext)
							viewlist.append([newfile, newext, '2D', tag])

			# 3D
			for newfile in os.listdir(myfold):
				newfile, newext = os.path.splitext(newfile) ; newext = newext[1:]
				if len(newfile) > 4:
					if (newext in okext
					and newfile[-4] in okchar and newfile[-3] in okchar 
					and newfile[-2] in okformat and newfile[-1] in okstyle
					and newfile[-2] in viewType and newfile[-1] in viewType):

						# file
						if scope == 'File':
							if len(newfile) == len(myfile) +4:												 
								if newfile[0:-4] == myfile and newext == myext:
									tag = exif(newfile, newext)
									viewlist.append([newfile, newext, '3D', tag])

						# folder
						elif scope == 'Folder':
							tag = exif(newfile, newext)						
							viewlist.append([newfile, newext, '3D', tag])

			viewlist = sorted(viewlist)

		# make infolist
		infolist = ''
		for i in viewlist:
			if (i[2] == '2D' and not process == 'reset') or i[2] == '3D':
				infolist = infolist+i[0]+'.'+i[1]+'\n'
		labelInfo.set_text(infolist)
		
	#-----------------------------------------------------------------------------	
	def showImage():
		global image1, imageL, imageR, boxOuter1, boxOuterL, boxOuterR
		#local newfilename1, newfilenameL, newfilenameR, newext1, newextL, newextR

		labelImage1.set_text('')
		labelImageL.set_text('')
		labelImageR.set_text('')
		
		for i in boxImage1:
			boxImage1.remove(i)
		for i in boxImageL:
			boxImageL.remove(i)
		for i in boxImageR:
			boxImageR.remove(i)

		if len(viewlist) > 0 and viewind > -1 and (
				(viewDim in ('All', '3D', 'Triptych') and viewlist[viewind][2] == '3D'
				and viewlist[viewind][0][-2] in viewType and viewlist[viewind][0][-1] in viewType
				)
			or
				(viewDim in ('All', '2D') and viewlist[viewind][2] == '2D')
			):

			if viewlist[viewind][2] == '2D': #43 greyout delete button for 2D images
				GbuttonDelete.set_sensitive(False)
			else:
				GbuttonDelete.set_sensitive(True)

			# two 2D images for triptych	
			if viewDim == 'Triptych':
				
				# Left 2D image
				newfilenameL = viewlist[viewind][0][:-4]+viewlist[viewind][0][-4]; newextL = viewlist[viewind][1]
				labelImageL.set_markup('<b>'+newfilenameL+'.'+newextL+'</b>')

				if os.path.isfile(myfold+newfilenameL+'.'+newextL):
					orientationL = viewlist[viewind][3]				
					if orientationL == '3': # upside down, so rotate 180 clockwise
						pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file(myfold+newfilenameL+'.'+newextL), 180)
					elif orientationL == '6': # top at right so rotate 270 clockwise
						pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file(myfold+newfilenameL+'.'+newextL), 270)
					elif orientationL == '8': #top pointing left so rotate 90 clockwise
						pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file(myfold+newfilenameL+'.'+newextL), 90)
					elif orientationL == 'notfound':
						pixbuf = GdkPixbuf.Pixbuf.new_from_file(programfold+blankfile)
					else:
						pixbuf = GdkPixbuf.Pixbuf.new_from_file(myfold+newfilenameL+'.'+newextL)
				else:
					pixbuf = GdkPixbuf.Pixbuf.new_from_file(programfold+blankfile)

				imageL = Gtk.Picture.new_for_pixbuf(pixbuf)
				imageL.props.hexpand = True	
				imageL.props.content_fit = Gtk.ContentFit.CONTAIN
				boxImageL.append(imageL)

				# Right 2D image
				newfilenameR = viewlist[viewind][0][:-4]+viewlist[viewind][0][-3]; newextR = viewlist[viewind][1]
				labelImageR.set_markup('<b>'+newfilenameR+'.'+newextR+'</b>')

				if os.path.isfile(myfold+newfilenameR+'.'+newextR):
					orientationR = viewlist[viewind][3]
					if orientationR == '3': # upside down, so rotate 180 clockwise
						pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from__file_at_scale(myfold+newfilenameR+'.'+newextR), 180)
					elif orientationR == '6': # top at right so rotate 270 clockwise
						pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file(myfold+newfilenameR+'.'+newextR), 270)
					elif orientationR == '8': #top pointing left so rotate 90 clockwise
						pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file(myfold+newfilenameR+'.'+newextR), 90)
					elif orientationR == 'notfound':
						pixbuf = GdkPixbuf.Pixbuf.new_from_file(programfold+blankfile)
					else:
						pixbuf = GdkPixbuf.Pixbuf.new_from_file(myfold+newfilenameR+'.'+newextR)
				else:
					pixbuf = GdkPixbuf.Pixbuf.new_from_file(programfold+blankfile) 

				imageR = Gtk.Picture.new_for_pixbuf(pixbuf)
				imageR.props.hexpand = True	
				imageR.props.content_fit = Gtk.ContentFit.CONTAIN
				boxImageR.append(imageR)
				
			# image 1 must be last so it doesn't take all the space in a Triptych
			newfilename1 = viewlist[viewind][0]; newext1 = viewlist[viewind][1]
			labelImage1.set_markup('<b>'+newfilename1+'.'+newext1+'</b>')

			if os.path.isfile(myfold+newfilename1+'.'+newext1):
				orientation1 = viewlist[viewind][3]
				if orientation1 == '3': # upside down, so rotate 180 clockwise
					pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file(myfold+newfilename1+'.'+newext1), 180)
				elif orientation1 == '6': # top at right so rotate 270 clockwise
					pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file(myfold+newfilename1+'.'+newext1), 270)
				elif orientation1 == '8': #top pointing left so rotate 90 clockwise
					pixbuf = GdkPixbuf.Pixbuf.rotate_simple(GdkPixbuf.Pixbuf.new_from_file(myfold+newfilename1+'.'+newext1), 90)
				elif orientation1 == 'notfound': # file missing #redundant
					pixbuf = GdkPixbuf.Pixbuf.new_from_file(programfold+blankfile)
				else: #already upright or could not be determined
					pixbuf = GdkPixbuf.Pixbuf.new_from_file(myfold+newfilename1+'.'+newext1)
			else: # not found
				pixbuf = GdkPixbuf.Pixbuf.new_from_file(programfold+blankfile)

		else:
			pixbuf = GdkPixbuf.Pixbuf.new_from_file(programfold+blankfile)

		image1 = Gtk.Picture.new_for_pixbuf(pixbuf)
		image1.props.hexpand = True; image1.props.vexpand = True
		image1.props.content_fit = Gtk.ContentFit.CONTAIN
		boxImage1.append(image1)

	#-----------------------------------------------------------------------------
	def checkpairlist():
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
				warnings = warnings + _('Unable to load left image') +' ' +myfold+i[0]+i[1]+'.'+i[5]+'.\n'
				existsLeft = False
				pairlist.remove(i)				
			try:
				image = Image.open(myfold+i[0]+i[2]+'.'+i[5])
				imageRightFormat = image.format ; imageRightSize = image.size
				existsRight = True
				image.close
			except:
				warnings = warnings + _('Unable to load right image') +' ' +myfold+i[0]+i[2]+'.'+i[5]+'.\n'
				existsRight = False
				pairlist.remove(i)
					
			if existsLeft and existsRight:
				if imageLeftFormat != imageRightFormat:
					warnings = warnings +i[0]+i[1]+'.'+i[5]+ ' ' +_('and') +' ' +i[0]+i[2]+'.'+i[5] +' ' + _('cannot be used as they have different filetypes.') +'\n'
					pairlist.remove(i)
				if imageLeftSize != imageRightSize:
					warnings = warnings +i[0]+i[1]+'.'+i[5]+' '+str(imageLeftSize) +' ' +_('and') +' ' +i[0]+i[2]+'.'+i[5]+' '+str(imageRightSize)+ ' ' +_('cannot be used as their dimensions do not match.') +'\n'
					pairlist.remove(i)
							
		if warnings != '':		
			showInfo(warnings)

	#-----------------------------------------------------------------------------
	#def processPairlist(pairlist): WAS HERE
	
	#-----------------------------------------------------------------------------			
	def buttonPrev(button):
		global worker
		findNext('<')		
		showImage()
		if process == 'Reset':
			#if os.path.isfile(workfold+runningfile): #44
			if worker and worker.is_alive():
				labelInfoTitle.set_markup('<b>' +_('Processing 3D Images') +'</b>')
			else:
				labelInfoTitle.set_markup('<b>' +_('Completed 3D Images') +'</b>')

	def buttonNext(button):
		findNext('>')	
		showImage()
		if process == 'reset':
			#if os.path.isfile(workfold+runningfile): #44
			if worker and worker.is_alive():
				labelInfoTitle.set_markup('<b>' +_('Processing 3D Images') +'</b>')
			else:
				labelInfoTitle.set_markup('<b>' +_('Completed 3D Images') +'</b>')

	#-----------------
	def tickViewAll(menuitem): 
		global viewDim
		if menuitem.get_active():	
			viewDim = 'All'
			greyout(False) #43
			if not startup:
				findVmatch(); showImage()
					
	def tickView2D(menuitem):
		global viewDim
		if menuitem.get_active():
			viewDim = '2D'
			greyout(True) #43
			if not startup:
				findVmatch(); showImage()
			
	def tickView3D(menuitem):
		global viewDim
		if menuitem.get_active():
			viewDim = '3D'
			greyout(False) #43
			if not startup:
				findVmatch(); showImage()
	
	def tickViewTriptych(menuitem):
		global viewDim
		if menuitem.get_active():
			viewDim = 'Triptych'
			greyout(False) #43
			if not startup:
				findVmatch(); showImage()
				
	#-----------------
	def tickViewAnaglyph(menuitem):
		global viewType
		if menuitem.get_active():	
			viewType = viewType[:0] + 'A' + viewType[1:]
		else:
			viewType = viewType[:0] + '-' + viewType[1:]
		if not startup:	
			findFSmatch(); showImage()									

	def tickViewSidebyside(menuitem):
		global viewType
		if menuitem.get_active():	
			viewType = viewType[:1] + 'S' + viewType[2:]
		else:
			viewType = viewType[:1] + '-' + viewType[2:]
		if not startup:
			findFSmatch(); showImage()									
										
	def tickViewCrossover(menuitem):
		global viewType
		if menuitem.get_active():	
			viewType = viewType[:2] + 'C' + viewType[3:]
		else:
			viewType = viewType[:2] + '-' + viewType[3:]
		if not startup:
			findFSmatch(); showImage()									

	def tickViewNormal(menuitem):
		global viewType
		if menuitem.get_active():	
			viewType = viewType[:3] + 'N' + viewType[4:]
		else:
			viewType = viewType[:3] + '-' + viewType[4:]
		if not startup:
			findFSmatch(); showImage()									

	def tickViewPopout(menuitem):
		global viewType
		if menuitem.get_active():	
			viewType = viewType[:4] + 'P' + viewType[5:]
		else:
			viewType = viewType[:4] + '-' + viewType[5:]
		if not startup:
			findFSmatch(); showImage()									

	#-----------------			
	def tickAnaglyph(menuitem):
		global formatcode, pairlist, process
		if menuitem.get_active():
			formatcode = 'A'
			GbuttonProcess.set_label(_('Queue')); process = 'queue'; GbuttonProcess.props.tooltip_text = tipQueue
			labelInfoTitle.set_markup('<b>' + _(scope) +' ' +_('Selection') +'</b>')
			pairlist = []						
			makeviewlist(False)#; viewind = 0; findNext('<'); showImage()

	def tickSidebyside(menuitem):
		global formatcode, pairlist, process
		if menuitem.get_active():
			formatcode = 'S'
			GbuttonProcess.set_label(_('Queue')); process = 'queue'; GbuttonProcess.props.tooltip_text = tipQueue
			labelInfoTitle.set_markup('<b>' + _(scope) +' ' +_('Selection') +'</b>')
			pairlist = []						
			makeviewlist(False)#; viewind = 0; findNext('<'); showImage()
							
	def tickCrossover(menuitem):
		global formatcode, pairlist, process
		if menuitem.get_active():
			formatcode = 'C'
			GbuttonProcess.set_label(_('Queue')); process = 'queue'; GbuttonProcess.props.tooltip_text = tipQueue
			labelInfoTitle.set_markup('<b>' + _(scope) +' ' +_('Selection') +'</b>')
			pairlist = []						
			makeviewlist(False)#; viewind = 0; findNext('<'); showImage()

	def tickNormal(menuitem):
		global stylecode, pairlist, process
		if menuitem.get_active():
			stylecode = 'N'
			GbuttonProcess.set_label(_('Queue')); process = 'queue'; GbuttonProcess.props.tooltip_text = tipQueue
			labelInfoTitle.set_markup('<b>' + _(scope) +' ' +_('Selection') +'</b>')
			pairlist = []						
			makeviewlist(False)#; viewind = 0; findNext('<'); showImage()

	def tickPopout(menuitem):
		global stylecode, pairlist, process
		if menuitem.get_active():
			stylecode = 'P'
			GbuttonProcess.set_label(_('Queue')); process = 'queue'; GbuttonProcess.props.tooltip_text = tipQueue
			labelInfoTitle.set_markup('<b>' + _(scope) +' ' +_('Selection') +'</b>')
			pairlist = []						
			makeviewlist(False)#; viewind = 0; findNext('<'); showImage()

	def tickRetain(menuitem): #43
		global retain
		if menuitem.get_active():
			retain = True
		else:
			retain = False

	#-----------------------------------------------------------------------------		
	def buttonProcess(button):
		global warnings, viewDim, pairlist, infolist, viewind, process
		global viewlist
		global worker, stop_event   #44
		# local okleft, okright
		# pairlist filename style is name less last digit		
		#44
		#if os.path.isfile(workfold+runningfile):
		#	showInfo(_('Please wait for the current processing to finish'))

		if worker and worker.is_alive():
			showInfo(_('Please wait for the current processing to finish'))
			return

		if process == 'queue': #not reset and pairlist == []: #was elif CGPT2026
			setlist = [];	warnings = ''

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
				makepairlist(record[0], record[1], record[2], record[3])
			setlist = []	
			
			checkpairlist() # remove any which don't match format and size.

			# pairlist record ['DONEtest', 'L', 'R', 'A', 'N', 'jpg', '8', '8']
			# viewlist record ['DONEtestL', 'png', '2D', '8']
		
			# make infolist and templist of projected images
			if pairlist != []:
				makeviewlist(True); viewind = 0; findNext('<'); showImage()
				labelInfoTitle.set_markup('<b>' +_('Queue') +'</b>')
				GbuttonProcess.set_label(_('Process')); process = 'process'; GbuttonProcess.props.tooltip_text = tipProcess
				GtickView3D.set_active(True)
			else: # empty list - warn nothing to process
				makeviewlist(False); viewind = 0; findNext('<'); showImage()
				showInfo(_('Nothing to process'))
			

		# RESET Button on Reset empty pairlist
		elif process == 'reset': # and pairlist == []
			GbuttonProcess.set_label(_('Queue')); process = 'queue'; GbuttonProcess.props.tooltip_text = tipQueue
			labelInfoTitle.set_markup('<b>' + _(scope) +' ' +_('Selection') +'</b>')
			makeviewlist(False); findVmatch(); showImage()

		# PROCESS
		else: # Process as list is not empty
			#44
			#multi = multiprocessing.Process(target = processPairlist, args=(pairlist,))
			stop_event = threading.Event()
			stop_event.clear()
			worker = threading.Thread(
				target=processPairlist,
				args=(stop_event, pairlist, myfold, workfold),
				daemon=True
					)
			worker.start()

			pairlist = []
			GbuttonProcess.set_label(_('Reset')); process = 'reset'; GbuttonProcess.props.tooltip_text = tipReset
			GtickView3D.set_active(True)
			viewDim = '3D'; viewind = 0; findNext('<'); showImage()		
			labelInfoTitle.set_markup('<b>' +_('Processing 3D Images') +'</b>')

		warnings = ''			
	
	def buttonDelete(button): # was (self, button)
		global viewind
		#local ok
		#if os.path.isfile(workfold+runningfile): #44
		if worker and worker.is_alive():
			showInfo(_('Please wait for the current processing to finish'))
		elif process == 'process':
			showInfo(_('Cannot delete from queue'))
		elif process in ('queue', 'reset'):
			if len(viewlist) > 0:
				if os.path.isfile(myfold+viewlist[viewind][0]+'.'+viewlist[viewind][1]):
					if viewlist[viewind][2] == '3D':
						showDelete()
					else:
						showInfo(_('Only 3D images can be deleted')) #43 redundant as delete button is greyed out for 2D images
				else:
					showInfo(_('Image does not exist'))
			else:
				showInfo(_('No 3D images to delete'))
				
	def show_open_dialog_file(win, anything):
		global process
		GbuttonProcess.set_label(_('Queue')); process = 'queue'; labelInfoTitle.set_markup('<b>' + _(scope) + ' ' +_('Selection') +'</b>')
		open_dialog_file.show()	
		
	def show_open_dialog_folder(win, anything):
		GbuttonProcess.set_label(_('Queue')); process = 'queue'; labelInfoTitle.set_markup('<b>' + _(scope) + ' ' +_('Selection') +'</b>')
		open_dialog_folder.show()	
				
	def open_response_file(dialog, response): #was menuItemSet(self, menuitem)
		global myfold, myfile, myext, scope, pairlist, viewind
		#local okfile
				
		if response == Gtk.ResponseType.ACCEPT:		
			file = dialog.get_file()
			newfile = file.get_path()
		else: # answered No or closed window
			return

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
					showInfo(_('Filename must follow the rules in the Help about File Selection'))
					return
			else:
				showInfo(_('Filename must follow the rules in the Help about File Selection'))
				return
			win.set_title(myfold + myfile + '*.' + myext)
							
		''' #DIFF THIS WAS IN ANOTHER FILE
		okfile = True			
		if len(newfile) > 1:
			if newfile[-1] in okchar: # could be a 2D file
				myfold = newfold +'/' ; myfile = newfile[:-1]; myext = newext[1:]
			elif len(newfile) > 3: #44P could be a new style 3D file	
				if (newfile[-3] in okchar and newfile[-2] in okchar and newfile[-1] in okformat):
					myfold = newfold +'/' ; myfile = newfile[:-3]; myext = newext[1:] 
			elif len(newfile) > 4: # could be an old style 3D file
				if (newfile[-4] in okchar and newfile[-3] in okchar and newfile[-2] in okformat and newfile[-1] in okstyle):
					myfold = newfold +'/' ; myfile = newfile[:-4]; myext = newext[1:] 
				else:
					showInfo(_('Filename must follow the rules in the Help about File Selection'))
					return
			else:
				showInfo(_('Filename must follow the rules in the Help about File Selection'))
				return
		'''

			
		os.chdir(newfold)
		pairlist = []; GbuttonProcess.set_label(_('Queue')); process = 'queue'; GbuttonProcess.props.tooltip_text = tipQueue
		scope = 'File'; labelInfoTitle.set_markup('<b>' + _(scope) + ' ' +_('Selection') +'</b>')
		
		makeviewlist(False); viewind = 0; findNext('<')
		if len(viewlist) > 0: #1.5.31
			if not	(
							(viewDim in('All', '3D', 'Triptych') and viewlist[viewind][2] == '3D')
							or
							(viewDim in ('All', '2D') and viewlist[viewind][2] == '2D')
							):
				findNext('>')

		showImage()
			
	def open_response_folder(dialog, response): #was menuItemFolder(self, menuitem)
		global myfold, myfile, myext, scope, pairlist, viewind, process
		
		if response == Gtk.ResponseType.ACCEPT:
			file = dialog.get_file()
			newfold = file.get_path()

			newfold = newfold+'/'	
			myfold = newfold; os.chdir(myfold) 
			myfile = ''; myext = ''
			pairlist = []; GbuttonProcess.set_label('Queue'); process = 'queue'; GbuttonProcess.props.tooltip_text = tipQueue

			scope = 'Folder'
			makeviewlist(False); viewind = 0; findNext('<')
			if len(viewlist) > 0:
				if not	(
								(viewDim in('All', '3D', 'Triptych') and viewlist[viewind][2] == '3D')
								or
								(viewDim in ('All', '2D') and viewlist[viewind][2] == '2D')
								):
					findNext('>')

			win.set_title(myfold)
			showImage()
		
	#============================================================================= 
	# notebook

	notebook = Gtk.Notebook()
	notebook.set_tab_pos(Gtk.PositionType.LEFT)

	label0 = Gtk.Label.new(helpPage[0])
	label0.props.justify = Gtk.Justification.LEFT; label0.props.yalign = 0; label0.props.xalign = 0 #43 xalign was commented out
	label0.set_wrap(True)
	page0 = Gtk.ScrolledWindow()
	page0.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS) # scrollbars
	page0.set_child(label0)
	notebook.append_page(page0)
	notebook.set_tab_label_text(page0, _('Basics'))

	#43
	label0.set_margin_start(5)
	label0.set_margin_end(5)
	label0.set_margin_top(5)
	#

	label1 = Gtk.Label.new(helpPage[1])
	label1.props.justify = Gtk.Justification.LEFT; label1.props.yalign = 0; label1.props.xalign = 0
	label1.set_wrap(True)
	page1 = Gtk.ScrolledWindow()
	page1.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
	page1.set_child(label1)
	notebook.append_page(page1)
	notebook.set_tab_label_text(page1, _('Source Photographs'))

	label1.set_margin_start(5)
	label1.set_margin_end(5)
	label1.set_margin_top(5)
			
	label2 = Gtk.Label.new(helpPage[2])
	label2.props.justify = Gtk.Justification.LEFT; label2.props.yalign = 0; label2.props.xalign = 0
	label2.set_wrap(True)
	page2 = Gtk.ScrolledWindow()
	page2.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
	page2.set_child(label2)
	notebook.append_page(page2)
	notebook.set_tab_label_text(page2, _('File Selection'))

	label2.set_margin_start(5)
	label2.set_margin_end(5)
	label2.set_margin_top(5)
	
	label3 = Gtk.Label.new(_(helpPage[3]))
	label3.props.justify = Gtk.Justification.LEFT; label3.props.yalign = 0; label3.props.xalign = 0
	label3.set_wrap(True)
	page3 = Gtk.ScrolledWindow()
	page3.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
	page3.set_child(label3)
	notebook.append_page(page3)
	notebook.set_tab_label_text(page3, _('3D Image Options'))

	label3.set_margin_start(5)
	label3.set_margin_end(5)
	label3.set_margin_top(5)
	
	label4 = Gtk.Label.new(helpPage[4])
	label4.props.justify = Gtk.Justification.LEFT; label4.props.yalign = 0; label4.props.xalign = 0
	label4.set_wrap(True)
	page4 = Gtk.ScrolledWindow()
	page4.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
	page4.set_child(label4)
	notebook.append_page(page4)
	notebook.set_tab_label_text(page4, _('Process'))

	label4.set_margin_start(5)
	label4.set_margin_end(5)
	label4.set_margin_top(5)
	
	label5 = Gtk.Label.new(helpPage[5])
	label5.props.justify = Gtk.Justification.LEFT; label5.props.yalign = 0; label5.props.xalign = 0
	label5.set_wrap(True)
	page5 = Gtk.ScrolledWindow()
	page5.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
	page5.set_child(label5)
	notebook.append_page(page5)
	notebook.set_tab_label_text(page5, _('Images to View'))

	label5.set_margin_start(5)
	label5.set_margin_end(5)
	label5.set_margin_top(5)

	# BOXES-----------------------------------------------------------------------
	separatorView = Gtk.Separator(); separatorProcess = Gtk.Separator(); separatorInfo = Gtk.Separator()
	separatorDisplay = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)

	for i in (separatorView, separatorProcess, separatorInfo, separatorDisplay):
		i.set_margin_top(5); i.set_margin_bottom(10)
	separatorDisplay.set_margin_end(10)

	# create boxes and images
	boxWindow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
	boxOptions = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
	boxDisplay = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

	boxView = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
	boxViewT = Gtk.CenterBox()
	boxViewT3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
	boxViewButton = Gtk.CenterBox()

	boxProcess = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
	boxProcessT = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
	boxProcessL = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
	boxProcessR = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
	boxProcessButton = Gtk.CenterBox()

	# put boxes within boxes
	win.set_child(boxWindow) # Horizontal box to window
	boxWindow.append(boxOptions) # Put vert box in that box
	boxWindow.append(boxDisplay)
	boxOptions.append(boxView)
	
	labelView = Gtk.Label.new(); labelView.set_markup('<b>' +_('View') +'</b>')
	boxView.append(labelView)

	labelDimensions = Gtk.Label.new(); labelDimensions.set_markup('<b>' +_('Dimensions') +'</b>') #43
	boxView.append(labelDimensions) #43

	boxView.append(boxViewT)
	labelViewtype = Gtk.Label.new(); labelViewtype.set_markup('<b>' +_('3D Image Types') +'</b>')
	boxView.append(labelViewtype)

	boxOptions.append(boxProcess)
	boxProcess.append(separatorProcess)
	labelProcess = Gtk.Label.new(); labelProcess.set_markup('<b>' +_('Process') +'</b>')
	boxProcess.append(labelProcess)
	boxProcess.append(boxProcessT)
	boxProcessT.append(boxProcessL)

	labelRetain = Gtk.Label.new(); labelRetain.set_markup('<b>' +_('Aligned 2D Images') +'</b>') #43
	boxProcess.append(labelRetain) #43
	GtickRetain = Gtk.CheckButton(label=_('Save')); GtickRetain.props.tooltip_text = tipRetain #43

	boxProcess.append(GtickRetain) #43
	boxProcess.append(boxProcessButton)
	
	labelFormat = Gtk.Label.new(); labelFormat.set_markup('<b>' +_('Format') +'</b>')
	labelFormat.props.xalign = 0
	boxProcessL.append(labelFormat)
	boxProcessT.append(boxProcessR)

	labelStyle = Gtk.Label.new(); labelStyle.set_markup('<b>' +_('Style') +'</b>')
	labelStyle.props.xalign = 0
	boxProcessR.append(labelStyle)
	
	boxInfo = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
	boxOptions.append(boxInfo)
	boxInfo.append(separatorInfo)

	# These need renaming to Info so fixed ones above can be changed to something more relevant.
	labelInfoTitle = Gtk.Label.new(); boxInfo.append(labelInfoTitle)

	# This is the list of files
	labelInfoScroll = Gtk.ScrolledWindow()
	labelInfoScroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
	boxInfo.append(labelInfoScroll)

	labelInfoScroll.props.vexpand = True
	labelInfoScroll.props.valign = Gtk.Align.FILL

	labelInfo = Gtk.Label.new('{None}')
	labelInfoScroll.set_child(labelInfo)

	labelInfo.props.valign = Gtk.Align.START
	labelInfo.props.halign = Gtk.Align.START

	# display---------------------------------------------------------------------	
	boxPrev = Gtk.CenterBox(orientation=Gtk.Orientation.VERTICAL)
	boxImages = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
	boxOuter1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
	boxImagesLR = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
	boxOuterL = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
	boxOuterR = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
	boxNext = Gtk.CenterBox(orientation=Gtk.Orientation.VERTICAL)
	boxLabelImage1 = Gtk.Box(); boxLabelImageL = Gtk.Box(); boxLabelImageR = Gtk.Box()
	boxImage1 = Gtk.Box(); boxImageL = Gtk.Box(); boxImageR = Gtk.Box()

	labelImage1 = Gtk.Label.new(); labelImageL = Gtk.Label.new(); labelImageR = Gtk.Label.new()
	boxLabelImage1.props.halign = Gtk.Align.CENTER; boxLabelImageL.props.halign = Gtk.Align.CENTER; boxLabelImageR.props.halign = Gtk.Align.CENTER
	image1 = Gtk.Picture(); imageL = Gtk.Picture(); imageR = Gtk.Picture()

	boxDisplay.append(separatorDisplay)
	boxDisplay.append(boxPrev)
	boxDisplay.append(boxImages)
	boxImages.append(boxOuter1)
	boxImages.append(boxImagesLR)
	boxImagesLR.append(boxOuterL); boxImagesLR.append(boxOuterR)
	boxOuter1.append(boxLabelImage1); boxOuterL.append(boxLabelImageL); boxOuterR.append(boxLabelImageR)
	boxOuter1.append(boxImage1); boxOuterL.append(boxImageL); boxOuterR.append(boxImageR)
	boxLabelImage1.append(labelImage1); boxLabelImageL.append(labelImageL); boxLabelImageR.append(labelImageR)	
	boxImage1.append(image1); boxImageL.append(imageL); boxImageR.append(imageR)	
	boxDisplay.append(boxNext)
	
	# margins---------------------------------------------------------------------
	for i in (boxView,	boxProcess,	boxInfo, boxImages):
		i.set_margin_start(10); i.set_margin_end(10); i.set_margin_top(10)
	boxImages.set_margin_bottom(10)
	boxImagesLR.set_margin_top(5)
	
	# buttons---------------------------------------------------------------------
	# create
	GtickView2D = Gtk.CheckButton(label=_('2D')); GtickView2D.props.tooltip_text = tip2D
	GtickViewTriptych = Gtk.CheckButton(label=_('Triptych')); GtickViewTriptych.props.tooltip_text = tipTriptych
	GtickView3D = Gtk.CheckButton(label=_('3D')); GtickView3D.props.tooltip_text = tip3D
	GtickViewAll = Gtk.CheckButton(label=_('All')); GtickViewAll.props.tooltip_text = tipAll
	
	GtickViewAnaglyph = Gtk.CheckButton(label=_('Anaglyph')); GtickViewAnaglyph.props.tooltip_text = tipAnaglyph
	GtickViewSidebyside = Gtk.CheckButton(label=_('Side-By-Side')); GtickViewSidebyside.props.tooltip_text = tipSidebyside
	GtickViewCrossover = Gtk.CheckButton(label=_('Crossover')); GtickViewCrossover.props.tooltip_text = tipCrossover
	GtickViewNormal = Gtk.CheckButton(label=_('Normal')); GtickViewNormal.props.tooltip_text = tipNormal
	GtickViewPopout = Gtk.CheckButton(label=_('Popout')); GtickViewPopout.props.tooltip_text = tipPopout
	
	GtickAnaglyph = Gtk.CheckButton(label=_('Anaglyph')); GtickAnaglyph.props.tooltip_text = tipAnaglyph
	GtickSidebyside = Gtk.CheckButton(label=_('Side-By-Side')); GtickSidebyside.props.tooltip_text = tipSidebyside
	GtickCrossover = Gtk.CheckButton(label=_('Crossover')); GtickCrossover.props.tooltip_text = tipCrossover
	GtickNormal = Gtk.CheckButton(label=_('Normal')); GtickNormal.props.tooltip_text = tipNormal
	GtickPopout = Gtk.CheckButton(label=_('Popout')); GtickPopout.props.tooltip_text = tipPopout

	GbuttonDelete = Gtk.Button(label=_('Delete')); GbuttonDelete.props.width_request = 100
	GbuttonDelete.props.tooltip_text = tipDelete	
	
	GbuttonProcess = Gtk.Button(label=_('Queue')); process = 'queue';
	GbuttonProcess.props.width_request = 100
	GbuttonProcess.props.tooltip_text = tipQueue

	GbuttonPrev = Gtk.Button(); GbuttonPrev.set_icon_name('go-previous-symbolic-symbolic'); GbuttonPrev.props.tooltip_text = tipPrev
	GbuttonNext = Gtk.Button(); GbuttonNext.set_icon_name('go-next-symbolic-symbolic'); GbuttonNext.props.tooltip_text = tipNext; GbuttonNext.props.valign = Gtk.Align.CENTER

	boxViewButton.set_center_widget(GbuttonDelete)
	boxProcessButton.set_center_widget(GbuttonProcess)
		
	boxViewT3.append(GtickViewTriptych)
	boxViewT3.append(GtickView3D)

	boxViewT.set_start_widget(GtickView2D)
	boxViewT.set_center_widget(boxViewT3)
	boxViewT.set_end_widget(GtickViewAll)
	
	boxViewType= Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
	boxViewTypeL = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
	boxViewTypeR = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

	boxView.append(boxViewType)
	boxViewType.append(boxViewTypeL)
	boxViewType.append(boxViewTypeR)
	
	boxViewTypeL.append(GtickViewAnaglyph)	
	boxViewTypeL.append(GtickViewSidebyside)		
	boxViewTypeL.append(GtickViewCrossover)
	boxViewTypeR.append(GtickViewNormal)
	boxViewTypeR.append(GtickViewPopout)
	boxView.append(boxViewButton)

	boxProcessL.append(GtickAnaglyph)	
	boxProcessL.append(GtickSidebyside)		
	boxProcessL.append(GtickCrossover)
	boxProcessR.append(GtickNormal)
	boxProcessR.append(GtickPopout)

	boxPrev.set_center_widget(GbuttonPrev)
	boxNext.set_center_widget(GbuttonNext)

	# connect
	GtickViewAll.connect('toggled', tickViewAll)
	GtickView2D.connect('toggled', tickView2D)
	GtickView3D.connect('toggled', tickView3D)
	GtickViewTriptych.connect('toggled', tickViewTriptych)

	GtickViewAnaglyph.connect('toggled', tickViewAnaglyph)
	GtickViewSidebyside.connect('toggled', tickViewSidebyside)
	GtickViewCrossover.connect('toggled', tickViewCrossover)
	GtickViewNormal.connect('toggled', tickViewNormal)	
	GtickViewPopout.connect('toggled', tickViewPopout)

	GtickAnaglyph.connect('toggled', tickAnaglyph)
	GtickSidebyside.connect('toggled', tickSidebyside)
	GtickCrossover.connect('toggled', tickCrossover)
	GtickNormal.connect('toggled', tickNormal)	
	GtickPopout.connect('toggled', tickPopout)

	GbuttonPrev.connect('clicked', buttonPrev)
	GbuttonNext.connect('clicked', buttonNext)
	GbuttonDelete.connect('clicked', buttonDelete)
	GbuttonProcess.connect('clicked', buttonProcess)	
	GtickRetain.connect('toggled', tickRetain)

	# group
	GtickView2D.set_group(GtickViewAll)
	GtickView3D.set_group(GtickViewAll)
	GtickViewTriptych.set_group(GtickViewAll)
	GtickSidebyside.set_group(GtickAnaglyph)
	GtickCrossover.set_group(GtickAnaglyph)
	GtickPopout.set_group(GtickNormal)

	#-----------------
	# open menu
	menu1 = Gio.Menu.new()
	menu1.append(_('Folder'), 'win.menuitemFolder')
	menu1.append(_('File'), 'win.menuitemFile')
	popover1 = Gtk.PopoverMenu() # Create a new popover menu
	popover1.set_menu_model(menu1)

	# Create open menu button
	menuOpen = Gtk.MenuButton(label=_('Open')); menuOpen.props.tooltip_text = tipOpen
	menuOpen.props.width_request = 85
	menuOpen.set_popover(popover1)
	win.header.pack_start(menuOpen)

	# add options to open menu
	action = Gio.SimpleAction.new('menuitemFolder') #, None)
	action.connect('activate', show_open_dialog_folder)
	win.add_action(action)	

	action = Gio.SimpleAction.new('menuitemFile') #, None)
	action.connect('activate', show_open_dialog_file)
	win.add_action(action)

	# file
	open_dialog_file = Gtk.FileChooserNative.new(title=_('Select any file from a set of images'), parent=win, action=Gtk.FileChooserAction.OPEN)
	
	open_dialog_file.connect('response', open_response_file)
	f = Gtk.FileFilter()
	f.set_name(_('Image files'))
	f.add_mime_type('image/jpeg')
	f.add_mime_type('image/tiff')
	f.add_mime_type('image/png')
	open_dialog_file.add_filter(f)

	# folder
	open_dialog_folder = Gtk.FileChooserNative.new(title=_('Select the Folder where the images are'), parent = win, action=Gtk.FileChooserAction.SELECT_FOLDER)
	open_dialog_folder.connect('response', open_response_folder)
	
	#-----------------------------------------------------------------------------	
	# main stripey menu
	menu2 = Gio.Menu.new()
	menu2.append(_('Save Settings'), 'win.menuitemSettings')
	menu2.append(_('Internet Forum'), 'win.menuitemForum')
	#menu2.append(_('Improve a Translation on Crowdin'), 'win.menuitelocalefold')
	menu2.append(_('Help'), 'win.menuitemHelp')
	menu2.append(_('About Popout3D'), 'win.menuitemAbout')

	# create Main menu menuStripey style
	# Create a popover
	popover2 = Gtk.PopoverMenu()
	popover2.set_menu_model(menu2)

	# Create a menu button
	menuStripey = Gtk.MenuButton(); menuStripey.props.tooltip_text = tipStripey
	menuStripey.set_popover(popover2)
	menuStripey.set_icon_name('open-menu-symbolic')
	win.header.pack_end(menuStripey)
	
	# add actions to main stripey menu options
	# settings
	action = Gio.SimpleAction.new('menuitemSettings')
	action.connect('activate', showSettings)
	win.add_action(action)
	
	# help
	action = Gio.SimpleAction.new('menuitemHelp')
	action.connect('activate', showHelp)
	win.add_action(action)
	
	# about
	action = Gio.SimpleAction.new('menuitemAbout')
	action.connect('activate', showAbout)
	win.add_action(action)	

	# Forum
	action = Gio.SimpleAction.new('menuitemForum')
	action.connect('activate', showForum)
	win.add_action(action)

	# locale
	#action = Gio.SimpleAction.new('menuitelocalefold')
	#action.connect('activate', showLocale)
	#win.add_action(action)

	#-----------------------------------------------------------------------------
	readSettings()

	if scope == 'Folder':
		#win.set_title(version + '			Folder: ' + myfold)
		win.set_title(myfold)
	else:
		#win.set_title(version + '			Set: ' + myfold + myfile + '*.' + myext)
		win.set_title(myfold + myfile + '*.' + myext)

	startup = True
	if viewDim == '2D':
		GtickView2D.set_active(True)
	elif viewDim == '3D':
		GtickView3D.set_active(True)
	elif viewDim == 'Triptych':
		GtickViewTriptych.set_active(True)
	else: # All
		GtickViewAll.set_active(True)		

	if 'A' in viewType:
		GtickViewAnaglyph.set_active(True)
		
	if 'S' in viewType:
		GtickViewSidebyside.set_active(True)
		
	if 'C' in viewType:
		GtickViewCrossover.set_active(True)
		
	if 'N' in viewType:
		GtickViewNormal.set_active(True)
		
	if 'P' in viewType:
		GtickViewPopout.set_active(True)

	if formatcode == 'S': # Side-by-Side
		GtickSidebyside.set_active(True)
	elif formatcode == 'C': # Crossover
		GtickCrossover.set_active(True)
	else:
		GtickAnaglyph.set_active(True)
		
	if stylecode == 'P': # Popout
		GtickPopout.set_active(True)
	else: # Normal
		GtickNormal.set_active(True)

	if retain: # 43
		GtickRetain.set_active(True)
	else:
		GtickRetain.set_active(False)

	startup = False

	if firstrun:
		message = Gtk.MessageDialog(title = _('How to use Popout3D'), text = helpPage[0]) #43
		message.set_modal(win); message.set_transient_for(win)
		message.add_buttons(_('OK'), Gtk.ResponseType.OK)		
		response = message.connect('response', ask, None)
		message.set_visible(True)
	
	makeviewlist(False); viewind = 0
	if len(viewlist) > 0:
		if not	(
						(viewlist[viewind][0][-2] in viewType and viewlist[viewind][0][-1] in viewType
						and viewDim in('All', '3D', 'Triptych') and viewlist[viewind][2] == '3D'
						)
						or
						(viewDim in ('All', '2D') and viewlist[viewind][2] == '2D')
						):
			findVmatch()
	showImage()
	#Not needed now using signals
	#if os.path.isfile(workfold+runningfile):
	#	os.remove(workfold+runningfile)
	#if os.path.isfile(workfold+stopfile):
	#	os.remove(workfold+stopfile)

#44 later
def main():
    app = Gtk.Application(application_id='com.github.PopoutApps.popout3d')
    app.connect('activate', on_activate)
    app.run(sys.argv)

if __name__ == "__main__":
    main()

'''TESTED AND WORKING ON RPM
#44
def main():
    app = Gtk.Application(application_id='com.github.PopoutApps.popout3d')
    app.connect('activate', on_activate)
    app.run(None)

if __name__ == "__main__":
    main()
'''
#app = Gtk.Application(application_id='com.github.PopoutApps.popout3d')
#app.connect('activate', on_activate)
#app.run(None)
'''#DIFF
	def makeviewlist(queuing):
		global viewlist, viewind, pairlist
		#local variables newfile, newext, infolist, tag, ok
		tag = 'TAG'
		viewlist = []

		if queuing:
			# add all relevant images to viewlist
			for record in pairlist:
				#viewlist.append([record[0]+record[1], record[5], '2D', record[6]])		
				viewlist.append([record[0]+record[1]+record[2]+record[3]+record[4], record[5], '3D', ''])	
				#viewlist.append([record[0]+record[2], record[5], '2D', record[7]])		
		else:
			# 2D
			for newfile in os.listdir(myfold):			 
				newfile, newext = os.path.splitext(newfile) ; newext = newext[1:]		
				if len(newfile) > 1:
					if newext in okext and newfile[-1] in okchar:
						# set: only add files in set to viewlist

						# file
						if scope == 'File':
							if len(newfile) == len(myfile) +1:
								if newfile[0:-1] == myfile and newext == myext:
									tag = exif(newfile, newext)
									viewlist.append([newfile, newext, '2D', tag])

						# folder
						elif scope == 'Folder':
							tag = exif(newfile, newext)
							viewlist.append([newfile, newext, '2D', tag])

			# 3D
			for newfile in os.listdir(myfold):
				newfile, newext = os.path.splitext(newfile) ; newext = newext[1:]
				ok = False
				if len(newfile) > 4: # old style LRAP
					if (newext in okext
					and newfile[-4] in okchar and newfile[-3] in okchar 
					and newfile[-2] in okformat and newfile[-1] in okstyle
					and newfile[-2] in viewType and newfile[-1] in viewType):

						# file
						if scope == 'File':
							if len(newfile) == len(myfile) +4:												 
								if newfile[0:-4] == myfile and newext == myext:
									tag = exif(newfile, newext)
									viewlist.append([newfile, newext, '3D', tag])
									ok = True

						# folder
						elif scope == 'Folder':
							tag = exif(newfile, newext)						
							viewlist.append([newfile, newext, '3D', tag])
							ok = True

				if not ok and len(newfile) > 3: #44 new style LRA
					if (newext in okext
					and newfile[-3] in okchar and newfile[-2] in okchar
					and newfile[-1] in okformat and 'N' in okstyle
					and newfile[-1] in viewType):	
						print(3)
						# file
						if scope == 'File':
							if len(newfile) == len(myfile) +3:
								if newfile[0:-3] == myfile and newext == myext:
									tag = exif(newfile, newext)
									viewlist.append([newfile, newext, '3D', tag])

						# folder
						elif scope == 'Folder':
							tag = exif(newfile, newext)						
							viewlist.append([newfile, newext, '3D', tag])						

			viewlist = sorted(viewlist)

		# make infolist
		infolist = ''
		for i in viewlist:
			if (i[2] == '2D' and not process == 'reset') or i[2] == '3D':
				infolist = infolist+i[0]+'.'+i[1]+'\n'
		labelInfo.set_text(infolist)
'''		
