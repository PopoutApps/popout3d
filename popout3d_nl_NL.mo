��    Q      �  m   ,      �     �     �     �     �  @     V   H  V   �  F   �     =     P     _     c     l     z     �     �  P   �     �  	   	  M   	  L   _	  (   �	  	   �	     �	     �	     �	  �  �	     �     �  @   �       6       O     �     �     �     �     �          !  D   -     r     �     �     �     �     �  1   �     �                    .     4  �  :  $   4  &   Y  	   �  2   �     �     �     �     �     	          +     >  d  D    �      �#  5   �#     $     $     3$     N$  �
  S$     �.  0   /  0   4/     e/  �  h/     �0     �0     �0     1  9   1  B   V1  D   �1  @   �1     2     52     C2     H2     Q2     c2  	   i2  "   s2  U   �2     �2     3  O   3  S   `3  5   �3     �3     �3     �3     4  '  4     E9     V9  I   m9     �9  :   �9  ]  �9     TB     \B     aB     tB     �B     �B  
   �B  \   �B  "   C     +C     3C     GC  +   LC     xC  ,   C     �C  
   �C  	   �C     �C     �C     �C  F  �C  +   7H  .   cH     �H  :   �H     �H     �H      I     I     2I     FI     RI     ^I  �  dI  R  M     pP  P   �P     �P  $   �P  %   Q     )Q  �  2Q     ,]  C   /]  H   s]     �]     M   >   :       G          !           )                     -         (      &      /   2           6         .   '   J       ?             3           F           4       #      @   ;   D      %          
   1   	   0   P   =      5      <   "       C              I   7                 *      E   $   ,   H   L   O               +                       N   K   B   9   A   Q          8                 2D 3D 3D Image Options 3D Image Types A 3D image which may appear to stand out in front of the screen. A 3D image with the left-hand image on the left and the right-hand image on the right. A 3D image with the left-hand image on the right and the right-hand image on the left. A 3D image with the left-hand image red and the right-hand image cyan. A normal 3D image. About Popout3D All Anaglyph Are you sure? Basics Cancel Cannot delete from queue. Clear the list of processed images and show the list selected by Folder or File. Completed 3D Images Copyright Create a 3D image from ordinary photographs.

Bugs can be reported on GitHub. Create a 3D image from photographs taken with a phone or an ordinary camera. Create the 3D images shown in the queue. Crossover Delete Delete a 3D image. File File
To process a single set of images which are all for the same subject, first use Open>File to choose any file from the set.

scenery1.jpg
scenery2.jpg
scenery3.jpg

Selecting any of these files will prepare you to process all of them. The program will create a 3D image for each pair of originals, so you are able to choose the best combination of images for left and right. It is not recommended to use more than 3 originals as the number of output images goes up dramatically:

2 originals produce 1 3D image
3 originals produce 3 3D images
4 originals produce 6 3D images
5 originals produce 10 3D images

All the 3D images get the same filename (except the final character) and extension as the originals, plus two digits and a letter each for the format and style. These examples are 'Anaglyph' format with 'Normal' style:

scenery12AN.jpg was made with scenery1.jpg for the left image and scenery2.jpg for the right.
scenery13AN.jpg was made with scenery1.jpg for the left image and scenery3.jpg for the right.
With images ending in L and R you would get sceneryLRAN.jpg.

Folder:
To process all the image sets in a folder, first use Open>folder to choose the folder with the sets of images.
 File Selection File not found. Filename must follow the rules in the Help about File Selection. Folder Folder: Select a folder. File: Select a 2D image file. For the 3D effect to work it is essential that each pair of images is prefectly aligned vertically and rotationally. This is a vital step and it is very difficult to achieve when holding the camera and even when using image editing software. The program does this for you, it may take about 20 seconds per 3D image.

An existing 3D image file will not be overwritten. Therefore if you wish to recreate a 3D image, you will first need to move, rename or delete the existing 3D image.

To start processing the selected images, click on "Queue", this will show a list of the images to be created in the panel to the left and the button will change to "Process". If you don't like the list, choose another File/Folder or Format/Style.
If you are happy with this list, press "Process", the button will change to "Reset". You can use the < and > buttons to look for completed 3D images. Only the recently processed images are shown. When you have finished checking them, press "Reset" to go back to the File or Folder selection, now including the new images. Using the Open menu or the Delete or process buttons will also reset the list.

Notes
Portrait images from a phone may be landscape photos with a rotation tag, the program rotates them to portrait for processing, but it doesn't change the originals.

Mobile phones from one manufacturer are suspected of producing 16:9 photos which do not conform to JPG standards.

The 3D images won't have valid EXIF tags.

Preferences from previous versions of the program are not loaded.

If you can't remember which of a pair of images was left and which was right, create a 3D image as usual. If it doesn't look right with your anaglyph glasses on normally, try with them on upside down, so the lenses swap sides. If the image now works rename the 2D images and create a new 3D image.

You can run Hugin yourself to experiment with other settings, it is available as a Flatpak. Format Help How to use Popout3D Image Alignment Image does not exist. Image files Information Make a queue of 3D images from the files selected by Folder or File. No 3D images to delete. Normal Nothing to process. OK Only 3D images can be deleted. Open Please wait for the current processing to finish. Popout Preferences Process Processing 3D Images Queue Reset Scroll backwards and forwards through the images using < and >.

All
All the images in the chosen folder or set which follow the naming rules will be shown.

2D
Only 2D images in the chosen folder or set which follow the naming rules will be shown.

3D
Only 3D images in the chosen folder or set which follow the naming rules will be shown.

Triptych
3D images will be shown at the top with the 2D images they were made from shown beneath.

3D Image Types
These selections only affect 3D/Triptych views (see Processing for explanations). If you have created more than one type of 3D image, you won't need to change viewing devices as you browse the images, as these buttons allow you to restrict which image types are shown.

Delete
If a 3D image is being displayed you may delete it. To ensure that you don't lose original images, 2D images cannot be deleted from within Popout3D. You could of course delete them using your file manager.

Notes
You may need to view 3D images from further away than you might expect. Select any file from a set of images Select the Folder where the images are Selection Show 3D images above the 2D images they came from. Show all images. Show next image. Show only 2D images. Show only 3D images. Show previous image. Side-By-Side Source Photographs Style Take two photos of a stationary subject, preferably in landscape format. Take the first, then move the camera about 60mm to the right, but point it at the same thing. Copy them to your PC, then rename them so that they have exactly the same name except that the left one has 'L' at the end and the right one has 'R'. For example photoL.JPG and photoR.JPG.

Open Popout3D then use Open>File to select either photo. Click Queue to see what 3D images will be created, the button will change to Process. Click it to begin processing. The button will change to Reset. If you use the < and > arrows you see a grey rectangle until the 3D image is complete when it will appear. It will take several seconds.

You will need 3D glasses to see anaglyph images or 3D Virtual Reality goggles to see side-by-side images. Some people can see side-by-side or crossover images without. The format of the 3D image can may be:

Anaglyph
A red/cyan colour 3D image viewed with coloured spectacles. These are available very cheaply on the Web.

Side-by-side
A side-by-side 3D image viewed straight ahead. left-hand image on the left, right-hand on the right. Some people can see these without a viewer, some can't.

Crossover
A side-by-side 3D image viewed with eyes crossed. right-hand image on the left, left-hand on the right. Some people can see these without a viewer, some can't.

There are two styles available:

Normal
A normal 3D image with the front of the picture level with the screen.

Popout
A 'popout' image. In some cases the effect is startling, as the front of the 3D image will popout in front of the screen. In most cases there is little or no difference from "Normal". This will delete This will save your current settings as the defaults. Triptych Unable to load left image Unable to load right image View You don't need a special camera, you can use an ordinary one or even a mobile phone. Choose a subject that won't move between photos.

Take two photographs of the same subject, one for the left-hand image, and after moving the camera about 60mm to the right, take another for the right-hand image. Try to get exactly the same thing in the centre of both photos. If you find it difficult to get the separation right you can take 3 or more photos at different separations. Don't take too many as this would result in a large number of 3D images which would take a long time to process. Always take them in sequence from left to right so you don't get them mixed up.

Each set of images (all those for the same subject) must be in the same format - .jpg, .tiff or .png, and the extensions must have the same case - all lowercase or all uppercase. They must be exactly the same size in pixels.

You may not be able to read/write image files on your camera or phone and the 3D images you create will need extra space, so it's best to copy your originals onto your PC.

When you have loaded them onto your PC, make sure that for all images intended for the same 3D image have the same filename followed by a digit that increases as the images were taken from left to right, for example:
DSCN0362.JPG - leftmost image
DSCN0363.JPG - middle image
DSCN0365.JPG - rightmost image
If you only took 2 you could end them with L and R.
Note that the Popout3D only lists and displays files with such names.

Movement
Stationary objects like buildings or scenery give good results.

Pictures of people should work, provided they can keep still for a few seconds. Objects like trees and water may be work in the right circumstances, for example if there isn't too much wind, and the water is placid.

Moving vehicles or people, or fast-flowing water like a waterfall or waves won't work.

Quality of Effect
A picture with objects at varying distances results in a convincing effect. Distant scenery won't work well, as there is little perspective effect anyway.

Some images are too difficult for the aligning software, and the resulting image is unusable.

Notes
Images must have exactly the same width and height in pixels. This makes editing the original L and R images difficult, but it can be done with a photo editor like rawTherapee which shows you the size that the edited image will have so you can match them. It is easier to edit the 3D image, although you can't crop Side-By-Side or Crossover ones.

Avoid images with all red or all cyan objects as they only appear in one eye so look odd.

Strange effects from nearby objects might be caused by the camera's depth of field being high. A shorter exposure will reduce the depth of field. and cannot be used as their dimensions do not match. cannot be used as they have different filetypes. on Project-Id-Version: 
PO-Revision-Date: 2023-04-06 18:51+0100
Last-Translator: PopoutApps, 2023
Language-Team: Dutch (https://app.transifex.com/PopoutApps/teams/166304/nl/)
Language: nl
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=2; plural=(n != 1);
X-Generator: Poedit 3.1.1
X-Poedit-Basepath: .
X-Poedit-SearchPath-0: popout3d.py
 2D 3D 3D-beeldopties 3D-beeldtypen Een 3D-beeld dat mogelijk voor het scherm lijkt te staan. Een 3D-beeld met links het linkerbeeld en rechts het rechterbeeld. Een 3D-beeld met links het rechterbeeld en rechts het linkerbeeld.
. Een 3D-beeld met het linkerbeeld rood en het rechterbeeld cyaan. Een normaal 3D-beeld. Over Popout3D Alle Anaglyph Weet u het zeker? Basis Annuleren Kan niet verwijderen uit wachtrij. Wis de lijst met verwerkte beelden en toon de lijst geselecteerd door map of bestand. Voltooide 3D-beelden Auteursrechten Maak een 3D-afbeelding van gewone foto's.

Bugs kunnen worden gemeld op GitHub. Maak een 3D-beeld van foto's gemaakt met een mobiele telefoon of een gewone camera. Maak de 3D-beelden die in de wachtrij worden getoont. Gekruist Verwijderen 3D-beeld verwijderen. Bestand Bestand
Om een enkele set beelden te verwerken die allemaal voor hetzelfde onderwerp zijn, gebruikt u eerst Open>Bestand om een bestand uit de set te kiezen.

landschap1.jpg
landschap2.jpg
landschap3.jpg

Als u een van deze bestanden selecteert, bereidt u zich voor om ze allemaal te verwerken. Het programma maakt een 3D-beeld voor elk paar originelen, zodat u de beste combinatie van beelden voor links en rechts kunt kiezen. Het wordt niet aanbevolen om meer dan 3 originelen te gebruiken, aangezien het aantal uitgevoerde beelden enorm toeneemt:

2 originelen produceren 1 3D-beeld
3 originelen produceren 3 3D-beelden
4 originelen produceren 6 3D-beelden
5 originelen produceren 10 3D-beelden

Alle 3D-beelden krijgen dezelfde bestandsnaam (behalve het laatste teken) en dezelfde extensie als de originelen, plus twee cijfers en een letter voor het formaat en de stijl. Deze voorbeelden zijn 'Anaglyph' formaat met 'Normal' stijl:

scenery12AN.jpg is gemaakt met scenery1.jpg voor de linkerbeeld en scenery2.jpg voor de rechterbeeld.
scenery13AN.jpg is gemaakt met scenery1.jpg voor de linkerbeeld en scenery3.jpg voor de rechterbeeld.
Met beelden die eindigen op L en R krijgt u sceneryLRAN.jpg.

Map:
Om alle beeldensets in een map te verwerken, gebruikt u eerst Open>map om de map met de beeldensets te kiezen.
 Bestand selectie Bestand niet gevonden. Bestandsnaam moet voldoen aan de regels in de Help over Bestandsselectie. Map Map: Map selecteren . Bestand: 2D-beeldbestand selecteren. Om het 3D-effect te laten werken, is het essentieel dat elk paar beelden perfect verticaal en roterend is uitgelijnd. Dit is een essentiële stap en het is erg moeilijk om dit te bereiken wanneer u de camera vasthoudt en zelfs wanneer u beeldbewerkingssoftware gebruikt. Het programma doet dit voor u, het kan ongeveer 20 seconden duren per 3D-beeld.

Een bestaand 3D-beeldbestand wordt niet overschreven. Als u dus een 3D-beeld opnieuw wilt maken, moet u eerst de bestaande 3D-beeld verplaatsen, hernoemen of verwijderen.

Om te beginnen met het verwerken van de geselecteerde beelden, klikt u op "Wachtrij", dit toont een lijst met de beelden die moeten worden gemaakt in het paneel aan de linkerkant en de knop verandert in "Verwerken". Als de lijst u niet aanstaat, kies dan een andere Bestand/Map of Formaat/Stijl.
Als u tevreden bent met deze lijst, drukt u op "Verwerken", de knop verandert in "Resetten". Jij kunt de knoppen < en > gebruiken om voltooide 3D-beelden te zoeken. Alleen de recent verwerkte beelden worden getoont. Wanneer u klaar bent met het controleren, drukt u op "Resetten" om terug te gaan naar de selectie van bestanden of mappen, nu inclusief de nieuwe beelden. Het gebruik van het menu Openen of de knoppen Verwijderen of Verwerken zal ook de lijst resetten.

Notities
Portretfoto's van een telefoon kunnen landschapsfoto's zijn met een rotatietag, het programma draait ze naar portret voor verwerking, maar het verandert niets aan de originelen.

Mobiele telefoons van één fabrikant worden verdacht van het maken van 16:9-foto's die niet voldoen aan de JPG-normen.

De 3D-beelden hebben geen geldige EXIF-tags.

Voorkeuren uit eerdere versies van het programma worden niet geladen.

Als u niet meer weet welke van een tweetal beelden links en welke rechts was, maakt u zoals gewoonlijk een 3D-beeld. Als het er niet goed uitziet met u anaglief-bril normaal op, probeer hem dan ondersteboven, zodat de lenzen van kant wisselen. Als de beeld nu werkt, hernoem de 2D-beelden en maak een nieuwe 3D-beeld.

Jij kunt Hugin zelf draaien om met andere instellingen te experimenteren, het is verkrijgbaar als Flatpak. Formaat Hulp Popout3D gebruiken Beelduitligning Beeld bestaat niet. Beelden Informatie Maak een wachtrij van 3D-beelden van de bestanden die zijn geselecteerd door Map of Bestand. Geen 3D-beelden om te verwijderen. Normaal Niets te verwerken. Oké Alleen 3D-beelden kunnen worden verwijdert. Openen Wacht tot de huidige verwerking is voltooid. Pop-out Voorkeuren Verwerken 3D-beelden verwerken Wachtrij Resetten Blader met < en > heen en weer door de beelden.

Alle
Alle beelden in de gekozen map of set die de naamgevingsregels volgen, worden getoond.

2D
Alleen 2D-beelden in de gekozen map of set die de naamgevingsregels volgen, worden getoont.

3D
Alleen 3D-beelden in de gekozen map of set die de naamgevingsregels volgen, worden getoont.

Triptiek
3D-beelden worden bovenaan getoont en de 2D-beelden waarvan ze zijn gemaakt, worden hieronder getoont.

3D-beeldtypen
Deze selecties zijn alleen van invloed op 3D-/Triptiek (zie Verwerken voor uitleg). Als u meer dan één type 3D-beeld hebt gemaakt, hoeft u het weergaveapparaat niet te wijzigen terwijl u door de beelden bladert, omdat u met deze knoppen kunt beperken welke beeldstypen worden getoont.

Verwijderen
Als er een 3D-beeld wordt getoont, kunt u deze verwijderen. Om ervoor te zorgen dat u geen originele beelden kwijtraakt, kunnen 2D-beelden niet vanuit Popout3D worden verwijderd. Jij kunt ze natuurlijk verwijderen met behulp van uw bestandsbeheerder.

Notities
Mogelijk moet u 3D-beelden van verder weg bekijken dan u zou verwachten. Selecteer een bestand uit een reeks beelden Selecteer de map waar de beelden zich bevinden Selectie Toon 3D-beelden boven de 2D-beelden waar ze vandaan komen. Alle beelden tonen. Volgende beeld tonen. Alleen 2D-beelden tonen. Alleen 3D-beelden tonen. Vorige beeld tonen. Zij-aan-Zij Bron foto's Stijl Maak twee foto's van een stilstaand onderwerp, bij voorkeur in liggend formaat. Neem de eerste, verplaats de camera vervolgens ongeveer 60 mm naar rechts, maar richt hem op hetzelfde. Kopieer ze naar uw pc en hernoem ze zodat ze exact dezelfde naam hebben, behalve dat de linker een 'L' aan het einde heeft en de rechter een 'R'. Bijvoorbeeld fotoL.JPG en fotoR.JPG.

Open Popout3D en gebruik vervolgens Open>Bestand om een van beide foto's te selecteren. Klik op Wachtrij om te zien welke 3D-beelden er worden gemaakt, de knop verandert in Verwerken. Klik erop om de verwerking te starten. De knop verandert in Resetten. Als u de pijlen < en > gebruikt, ziet u een grijze rechthoek totdat het 3D-beeld compleet is wanneer het verschijnt. Het duurt enkele seconden.

U hebt een 3D-bril nodig om anaglief-beelden te zien of een 3D Virtual Reality-bril om beelden naast elkaar te zien. Sommige mensen kunnen naast elkaar of gekruiste beelden zien zonder. Het type van het gemaakte 3D-beeld kan zijn:

Anaglief
Een 3D-beeld in rood/cyaankleur bekeken met een gekleurde bril. Deze zijn zeer goedkoop beschikbaar op het web.

Zij aan zij
Een naast elkaar geplaatst 3D-beeld dat normaal wordt bekeken. Links beeld links, rechts rechts. Sommige mensen kunnen deze zien zonder een 3D-viewer, andere niet.

Oversteek
Een 3D-beeld naast elkaar bekeken met gekruiste ogen. Rechter beeld links, linker beeld rechts. Sommige mensen kunnen deze zien zonder een 3D-viewer, andere niet.

Er zijn twee stijlen beschikbaar:

Normaal
Een normaal 3D-beeld met de voorkant van het beeld ter hoogte van het scherm.

Pop-out
Een 'pop-out'-beeld. In sommige gevallen is het effect verrassend, omdat de voorkant van het 3D-beeld voor het scherm lijkt te liggen. In de meeste gevallen is er weinig of geen verschil met 'Normaal'. Dit zal verwijderen Hierdoor worden uw huidige instellingen als de standaardinstellingen opgeslagen. Triptiek Linker beeld kan niet worden geladen Rechter beeld kan niet worden geladen Weergave Jij hebt geen speciale camera nodig, u kunt een gewone of zelfs een mobiele telefoon gebruiken. Kies een onderwerp dat niet beweegt tussen foto's.

Maak twee foto's van hetzelfde onderwerp, één voor het linkerbeeld, en nadat u de camera ongeveer 60 mm naar rechts hebt bewogen, maakt u nog een voor het rechterbeeld. Probeer exact hetzelfde in het midden van beide foto's te krijgen. Als u het moeilijk vindt om de scheiding goed te krijgen, kunt u 3 of meer foto's maken met verschillende scheidingen. Neem er niet te veel foto's, want dit zou resulteren in een groot aantal 3D-beelden die lang zouden duren om te verwerken. Neem ze altijd in volgorde van links naar rechts, zodat u ze niet door elkaar haalt.

Elke set beelden (alle beelden voor hetzelfde onderwerp) moet hetzelfde formaat hebben - .jpg, .tiff of .png, en de extensies moeten dezelfde hoofdletters hebben - allemaal kleine letters of allemaal hoofdletters. Ze moeten precies even groot zijn in pixels.

Mogelijk kunt u beeldsbestanden op uw camera of telefoon niet lezen/schrijven en hebben de 3D-beelden die u maakt extra ruimte nodig, dus u kunt uw originelen het beste naar uw pc kopiëren.

Als u ze op uw pc hebt geladen, zorg er dan voor dat alle beelden die bedoeld zijn voor dezelfde 3D-beeld dezelfde bestandsnaam hebben, gevolgd door een cijfer dat oploopt naarmate de beelden van links naar rechts zijn genomen, bijvoorbeeld:
DSCN0362.JPG - meest linkse beeld
DSCN0363.JPG - middelste beeld
DSCN0365.JPG - meest rechtse beeld
Als u er maar 2 nam, kon u ze beëindigen met L en R.
Merk op dat de Popout3D alleen bestanden met dergelijke namen weergeeft en weergeeft.

Beweging
Stilstaande objecten zoals gebouwen of landschappen geven goede resultaten.

Foto's van mensen zouden moeten werken, mits ze een paar seconden stil kunnen blijven staan. Voorwerpen als bomen en water kunnen onder de juiste omstandigheden werken, bijvoorbeeld als er niet te veel wind staat en het water rustig is.

Bewegende voertuigen of mensen, of snelstromend water zoals een waterval of golven zullen niet werken.

Kwaliteit van effect
Een foto met obucten op verschillende afstanden levert een overtuigend effect op. Landschappen in de verte zullen niet goed werken, omdat er sowieso weinig perspectiefeffect is.

Sommige beelden zijn te moeilijk voor de uitlijnsoftware en de resulterende beeld is onbruikbaar.

Notities
Beelden moeten exact dezelfde breedte en hoogte in pixels hebben. Dit maakt het bewerken van de originele L- en R-beelden moeilijk, maar het kan worden gedaan met een foto-editor zoals rawTherapee, die u de grootte van de bewerkte beeld laat zien, zodat u ze kunt matchen. Het is gemakkelijker om de 3D-beeld te bewerken, hoewel u Side-By-Side of Crossover-beelden niet kunt bijsnijden.

Vermijd beelden met allemaal rode of allemaal cyaan obucten, aangezien ze maar in één oog verschijnen, dus kijk vreemd.

Vreemde effecten van obucten in de buurt kunnen worden veroorzaakt doordat de scherptediepte van de camera groot is. Een kortere belichting vermindert de scherptediepte. en kunnen niet worden gebruikt omdat hun afmetingen niet overeenkomen. kunnen niet worden gebruikt omdat ze verschillende bestandstypen hebben. op 