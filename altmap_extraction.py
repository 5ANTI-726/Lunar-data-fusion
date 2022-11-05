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

def cut(longitude, latitude, sitenumber, source):
    try:
        source = Image.open(source)
        print("Source succesfully opened.")
    except:
        print("Error opening source.")

    #The coordinates of the top left corner of the source image. Positive 'y'
    #indexes are downward and positive 'x' indexes are rightward.
    sourcelong = 0.0
    sourcelat = 30.0

    #Pixel resolution selects pxpdeg pixels per degree of lunar surface.
    #The scale variables allow for selection of more than one degree in either
    #lontidunial or latitudinal directions.
    pixpdeg = 512
    xscale = 1
    yscale = 1

    #The 'x' and 'y' variables correctly index the top left corner of
    #the desired field in the source image, from which one only captures
    #'i' and 'j' numbers of pixels in either direction.
    x = (longitude - sourcelong)*pixpdeg
    y = (sourcelat - latitude - 1)*pixpdeg
    #The register array is for saving intensity values to allow for
    #appropriate scaling of pixel brightness.
    register = []

    #'intermediate' is an image object with the same 32-bit mode as the source
    #image. Now we only access the monster source file once. When copying scaled
    #pixels to the final image object in 8-bit format, we only have to access
    #the reduced 'intermediate' file.
    intermediate = Image.new(source.mode, (xscale*pixpdeg, yscale*pixpdeg))
    for i in range(0,xscale*pixpdeg):
        for k in range(0,yscale*pixpdeg):
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
    destination = '/Users/santi/Documents/Semestre 1-2-3/MR3038- Estancia de investigación/Proyectos/Data fusion in lunar environment/Training-testing/' +
    '512_00N_30N_000_045/' + 'SLDEM2015, site ' + str(sitenumber) + '/'
    os.mkdir(destination)
    #Information about the parameters used to cut the 'sink' image are coded in
    #the file name: the first number is the resolution in pixels per degree of
    #lunar surface, the second/third numbers are first/last latitude (south/north),
    #and the fourth/fifth numbers are first/last longitude (west/east).
    sink.save(destination + 'SLDEM2015_' + str(pixpdeg)
    + '_' + namedigits(latitude) + 'N_' + namedigits(latitude+yscale) + 'N_' +
    namedigits(longitude) + '_' + namedigits(longitude+xscale) + '.png')

    #Confirm the last line, the saving of the 'sink' image, was executed.
    print("Data succesfully saved.")

#By default, Image does not take more than a pretty limited number of pixels
#to protect itself from attacks.
Image.MAX_IMAGE_PIXELS = 353894400

#Specify where the monster source file is.
source = '/Users/santi/Downloads/SLDEM2015_512_00N_30N_000_045.JP2'
#Pass the first longitude (west/east), the first latitude (south/north), append
#the site number.
cut(12.0, 2.0, 5, source)
