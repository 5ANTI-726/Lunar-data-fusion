from PIL import Image, ImageFilter
from time import sleep
import os

def map(floor,ceiling,value):
    #Map unsigned 32-bit values to unsigned 8-bit
    mapped = int(round(256*(value - floor)/(ceiling - floor)))
    return mapped

def namedigits(number):
    #Maintain the three digit format for noting latitude/longitude. We do not
    #do different numbers of digits for the sake of universality of the method.
    if number < 10:
        name = '00' + str(number)
    elif number < 100:
        name = '0' + str(number)
    else:
        name = str(number)

    return name

def cut(longitude, latitude, sitenumber, source_image, origin):
    #Input: Coordiantes of minimum longitude and latitude of the site area,
    #the site number, the monster file filepath, and the parent folder
    #("Original data and scripts").
    #Output: None.

    #

    source = Image.open(source_image)
    print("This image is: " + str(source.size[0]) + " x " + str(source.size[1]))


    #The coordinates of the top left corner of the source image. Positive 'y'
    #indexes are downward and positive 'x' indexes are rightward.
    sourcelong = float(source_image[-11:-8])
    print("Source corner longitude: " + str(sourcelong))
    sourcelat = float(source_image[-15:-13])
    print("Source corner latitude: " + str(sourcelat))

    if longitude < 0:
        longitude = 360 + longitude

    print("Target corner longitude: " + str(longitude))
    print("Target corner latitude: " + str(latitude))

    #Pixel resolution selects pxpdeg pixels per degree of lunar surface.
    #The scale variables allow for selection of more than one degree in either
    #lontidunial or latitudinal directions.
    pixpdeg = 512
    xscale = 1
    yscale = 1

    #The 'x' and 'y' variables correctly index the top left corner of
    #the desired field in the source image, from which one only captures
    #'i' and 'j' numbers of pixels in either direction.
    x = int(abs(longitude - sourcelong)*pixpdeg) + 1
    y = int(abs(sourcelat - latitude - 1)*pixpdeg)
    #The register array is for saving intensity values to allow for
    #appropriate scaling of pixel brightness.
    register = []

    #'intermediate' is an image object with the same 32-bit mode as the source
    #image. Now we only access the monster source file once. When copying scaled
    #pixels to the final image object in 8-bit format, we only have to access
    #the reduced 'intermediate' file.
    intermediate = Image.new(source.mode, (xscale*pixpdeg, yscale*pixpdeg))
    #print("i will range from " + str(x) + " to " + str(x+xscale*pixpdeg))
    #print("k will range from " + str(y) + " to " + str(y+ yscale*pixpdeg))
    for i in range(0,xscale*pixpdeg):
        for k in range(0,yscale*pixpdeg):
            #print("X: " + str(x))
            #print("Y: " + str(y))
            #print("X + i: " + str(x + i))
            #print("Y + k: " + str(y + k))
            newpixel = source.getpixel((x+i,y+k))
            intermediate.putpixel((i,k), newpixel)
            register.append(newpixel)

    #Determine maximum and minimum 32-bit values of the receptive field and scale
    #pixel brightness to make their respective values 256 and 1.
    floor = min(register)
    ceiling = max(register)

    #Create final image data 'sink' with grayscale image mode and copy scaled
    #data from the 'intermediate'' image.
    sink = Image.new('L', (xscale*pixpdeg, yscale*pixpdeg))
    for i in range(0,xscale*pixpdeg):
        for k in range(0,yscale*pixpdeg):
            newpixel = map(floor, ceiling, intermediate.getpixel((i,k)))
            sink.putpixel((i,k), newpixel)

    #Save the 'sink' image to the appropriate directory. The first important parent
    #is what region of the moon it belongs to (e.g., 512_00N_30N_000_045).
    #The second part is the site number, which is given when calling the cut method.
    reference_name = source_image[-23:-4] + "/"
    destination = origin + reference_name + "SLDEM2015, site " + str(sitenumber) + "/"
    try:
        os.mkdir(destination)
    except:
        pass

    #Information about the parameters used to cut the 'sink' image are coded in
    #the file name: the first number is the resolution in pixels per degree of
    #lunar surface, the second/third numbers are first/last latitude (south/north),
    #and the fourth/fifth numbers are first/last longitude (west/east).
    northsouth = source_image[-13]
    sink.save(destination + 'SLDEM2015_' + str(pixpdeg)
    + '_' + namedigits(latitude) + northsouth + '_' + namedigits(latitude+yscale) + northsouth + '_' +
    namedigits(longitude) + '_' + namedigits(longitude+xscale) + '.png')

    #Confirm the last line, the saving of the 'sink' image, was executed.
    print("Data succesfully saved.")

#By default, Image does not take more than a pretty limited number of pixels
#to protect itself from attacks. This command will alter that limit.
Image.MAX_IMAGE_PIXELS = 353894400
origin = "/Users/santi/Documents/Semestre 1-2-3/MR3038- Estancia de investigación/Proyectos/Data fusion in lunar environment/Original data and scripts/"

#Specify where the monster source file is.
source = origin + "Global maps/SLDEM2015_512_30S_00S_000_045.JP2"
#Pass the first longitude (west/east), the first latitude (south/north), append
#the site number.
cut(22, -11, 4, source, origin)
