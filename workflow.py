from PIL import Image, ImageFilter
from playsound import playsound
import os.path as path
from time import sleep
import numpy, os, shutil

#Probable parent file: '/Users/santi/Desktop/Near infrared imaging, site 1'

def alarm(value):
    if value:
        playsound('siren.mp3')

def getfolders():
    #Input: None.
    #Output: Array of formatted folder paths.

    #This method is a UI with text processing capabilities. It will request,
    #clean, and return folder paths.
    folders = []

    #Get the number of elements in the folder array.
    numberfolders = int(input('How many parent folders do you want processed?'))
    for i in range(0,numberfolders):
        if i == 0:
            folders.append(input('Drop folder to process'))
        else:
            folders.append(input('Drop next folder to process'))

    #Remove the any backslashes added by the terminal to blank spaces, since
    #these are not required/don't work as file paths when using Pillow.
    c_folders = []
    for folder in folders:
        corrected = ''
        for i in range(0,len(folder)):
            if folder[i] != '\\':
                if i == (len(folders) - 1):
                    if folder[i] != ' ':
                        corrected = corrected + folder[i]
                else:
                    corrected = corrected + folder[i]
        c_folders.append(corrected)

    #Return the final array of folders, split as different elements, without backslashes.
    return c_folders

def interpolation_criteria(im,x,y):
    #Input: Image object and integer coordinates.
    #Output: Boolean value and classification of pixel in string.

    #Variable criteria for qualificatying for interpolation:
    width, height = im.size

    #Nonedge cases
    if x > 0 and x < width-1 and y > 0 and y < height-1:
        up = im.getpixel((x,y+1))
        down = im.getpixel((x,y-1))
        left = im.getpixel((x-1,y))
        right = im.getpixel((x+1,y))
        dead_neighbors = sum([int(up == 0), int(down == 0), int(left == 0), int(right == 0)])
        type = 'no edge'

    #Edge cases

    #Edge cases
    elif x == 0 and y > 0 and y < height-1:
        up = im.getpixel((x,y+1))
        down = im.getpixel((x,y-1))
        right = im.getpixel((x+1,y))
        dead_neighbors = sum([int(up == 0), int(down == 0), int(right == 0)])
        type = 'left edge'
    elif y == 0 and x > 0 and x < width-1:
        up = im.getpixel((x,y+1))
        left = im.getpixel((x-1,y))
        right = im.getpixel((x+1,y))
        dead_neighbors = sum([int(up == 0), int(left == 0), int(right == 0)])
        type = 'bottom edge'
    elif x == width-1 and y > 0 and y < height-1:
        up = im.getpixel((x,y+1))
        down = im.getpixel((x,y-1))
        left = im.getpixel((x-1,y))
        dead_neighbors = sum([int(up == 0), int(down == 0), int(left == 0)])
        type = 'right edge'
    elif y == height-1 and x > 0 and x < width-1:
        down = im.getpixel((x,y-1))
        left = im.getpixel((x-1,y))
        right = im.getpixel((x+1,y))
        dead_neighbors = sum([int(down == 0), int(left == 0), int(right == 0)])
        type = 'top edge'

    #Corner cases
    elif x == 0 and y == 0:
        up = im.getpixel((x,y+1))
        right = im.getpixel((x+1,y))
        dead_neighbors = sum([int(up == 0), int(right == 0)])
        type = 'corner 3'
    elif x == width-1 and y == 0:
        up = im.getpixel((x,y+1))
        left = im.getpixel((x-1,y))
        dead_neighbors = sum([int(up == 0), int(left == 0)])
        type = 'corner 4'
    elif x == 0 and y == height-1:
        down = im.getpixel((x,y-1))
        right = im.getpixel((x+1,y))
        dead_neighbors = sum([int(down == 0), int(right == 0)])
        type = 'corner 2'
    elif x == width-1 and y == height-1:
        down = im.getpixel((x,y-1))
        left = im.getpixel((x-1,y))
        dead_neighbors = sum([int(down == 0), int(left == 0)])
        type = 'corner 1'

    #Return whether it meets criteria (one allowable dead neighbor)
    if dead_neighbors <= 2:
        return (True,type)
    else:
        return (False,type)

def mosaic_create(origin, replace_mosaics):
    #Input: Folder path and save path destination.
    #Output: None.

    def quality_estimation(parent_folder_path):
        #Input: Parent folder path string.
        #Output: Array with decimal estimations of image quality.

        quality_matrix = []
        for file in os.listdir(parent_folder_path):
            if file.endswith(".tif") or file.endswith(".png"):
                im = Image.open(parent_folder_path + '/' + file)

                width, height = im.size
                dead_pixel_count = 0
                for x in range(0,width):
                    for y in range(0,height):
                        pixel = im.getpixel((x,y))
                        if pixel <= 1 or pixel == 256:
                            dead_pixel_count += 1
                top = width*height - dead_pixel_count
                bottom = width*height

                quality_matrix.append(top/bottom)
        return quality_matrix

    def contrast(source):
        #Input: Image object.
        #Output: Image object with contrast maximized.


        def mb(floor, ceiling):
            low = 2
            high = 256
            #print("Lowest: " + str(floor))
            #print("Highest: " + str(ceiling))
            b = (high*floor - low*ceiling)/(floor - ceiling)
            m = (low - b)/floor
            return m, b

        def acd(floor, ceiling, register):
            averages = []
            a = 0
            c = 0
            d = 0
            q = ceiling - floor
            for p in range(116, 190):
                a = (p*q - ceiling + 256*floor - 128*255)/(q*(128^2+ceiling*floor) - 128*(ceiling^2 + floor^2))
                c = 255/q - a*(ceiling + floor)
                d = 1 - a*ceiling**2 - c*floor
                temp = []
                for i in range(0,len(register)):
                    x = register[i]
                    temp.append(quadratic_map(a, c, d, x))
                average = sum(temp)/len(temp)
                averages.append(abs(average - 90))

            p = averages.index(min(averages)) + 116
            #print("P: " + str(p))
            a = (p*q - ceiling + 256*floor - 128*255)/(q*(128^2+ceiling*floor) - 128*(ceiling^2 + floor^2))
            c = 255/q - a*(ceiling + floor)
            d = 1 - a*ceiling**2 - c*floor

            return a, c, d

        def linear_map(m, b, x):
            y = m*x + b
            return int(y)

        def quadratic_map(a, c, d, x):
            y = a*x**2 + c*x + d
            return int(y)

        #Get limits for calculating the new pixel values.
        register = []
        x_limit, y_limit = source.size
        for i in range(0, x_limit):
            for j in range(0, y_limit):
                pixel = source.getpixel((i, j))
                if pixel > 3:
                    register.append(pixel)

        #Create the brightness/contrast options if the image is not all black
        if len(register) != 0:
            floor = min(register)
            ceiling = max(register)
            average = sum(register)/len(register)
            #Image transformation diagnostic tools
            #print("Average: " + str(average))
            #print("Ceiling: " + str(ceiling))
            #print("Floor: " + str(floor))
            #source.show()

            #Quasi-linear mapping option
            m, b = mb(floor, ceiling)
            sink_1 = Image.new(source.mode, (x_limit, y_limit))
            for i in range(0, x_limit):
                for j in range(0, y_limit):
                    pixel = source.getpixel((i, j))
                    if pixel * (128/average) <= 256:
                        pixel = int(source.getpixel((i, j)) * (128/average))
                        sink_1.putpixel( (i, j), pixel )
                    else:
                        sink_1.putpixel( (i, j), linear_map(m, b, pixel) )

            #Linear mapping option
            sink_2 = Image.new(source.mode, (x_limit, y_limit))
            for i in range(0, x_limit):
                for j in range(0, y_limit):
                    pixel = source.getpixel((i, j))
                    sink_2.putpixel( (i, j), linear_map(m, b, pixel) )

            #Quadratic mapping option
            a, c, d = acd(floor, ceiling, register)
            sink_3 = Image.new(source.mode, (x_limit, y_limit))
            for i in range(0, x_limit):
                for j in range(0, y_limit):
                    pixel = source.getpixel((i, j))
                    sink_3.putpixel( (i, j), quadratic_map(a, c, d, pixel) )

            return sink_1, sink_2, sink_3
        #If the register is empty, return the original image
        return source, source, source

    threshold = 1
    for item in os.listdir(origin):
        if item == "Original data":
            #print(origin + item)
            item += "/"
            for area in  os.listdir(origin + item):
                area += "/"
                if area[0] != ".":
                    for site_data in os.listdir(origin + item + area):
                        site_data += "/"
                        prefix = ''
                        if site_data[0:4] == "Near":
                            prefix = "NIR"
                        elif site_data[0:5] == "Ultra":
                            prefix = "UVV"

                        if site_data[-11:] == "_processed/" and not path.exists(origin + item + area + site_data + prefix + "mosaic_1.png"):
                            parent_directory = origin + item + area + site_data
                            destination_directory = parent_directory

                            print("Constructing mosaic for " + site_data)

                            #Mosaic creation variables# DO NOT TOUCH
                            #Estimating the quality of every image file in the folder
                            quality_matrix = quality_estimation(parent_directory)
                            quality_order = list(numpy.argsort(quality_matrix))
                            tiff_list = []
                            #Mosaic creation variables# DO NOT TOUCH

                            for file in os.listdir(parent_directory):
                                if file.endswith(".tif") or file.endswith(".png"):
                                    tiff_list.append(file)

                            basis_1 = Image.new('L', (training_image_size,training_image_size), color = 0)
                            basis_2 = Image.new('L', (training_image_size,training_image_size), color = 0)
                            basis_3 = Image.new('L', (training_image_size,training_image_size), color = 0)

                            for index in quality_order:
                                #Add to canvas in order of quality.
                                current_mosaic_item = Image.open( parent_directory + tiff_list[quality_order[index]] )
                                #current_mask = Image.open( parent_directory + tiff_list[quality_order[index]] + '.msk')
                                next_image_1, next_image_2, next_image_3 = contrast(current_mosaic_item)

                                for x in range(0,training_image_size):
                                    for y in range(0,training_image_size):
                                        new_pixel_1 = next_image_1.getpixel((x,y))
                                        new_pixel_2 = next_image_2.getpixel((x,y))
                                        new_pixel_3 = next_image_3.getpixel((x,y))
                                        if new_pixel_1 > threshold:
                                            basis_1.putpixel((x,y), new_pixel_1)
                                        if new_pixel_2 > threshold:
                                            basis_2.putpixel((x,y), new_pixel_2)
                                        if new_pixel_3 > threshold:
                                            basis_3.putpixel((x,y), new_pixel_3)

                            if replace_mosaics:
                                os.remove(destination_directory + prefix + 'mosaic_1.png')
                                os.remove(destination_directory + prefix + 'mosaic_2.png')
                                os.remove(destination_directory + prefix + 'mosaic_3.png')

                            #Save first mosaic option
                            basis_1.save(destination_directory + prefix + 'mosaic_1.png')
                            #Save second mosaic option
                            basis_2.save(destination_directory + prefix + 'mosaic_2.png')
                            #Save third mosaic option
                            basis_3.save(destination_directory + prefix + 'mosaic_3.png')

def over80_filter(origin):
    #Input: The project's file; the "Original data" file has to be
    #an immediate child.
    #Output: None.

    ###FROM DIFFERENT METHOD. EVENTUALLY UPDATE###Navigate through all folders within the "Original data and scripts" folder
    #, looking for folders that start with "Near" or "Ultra". For each of these,
    #an equivalent sibling folder is created with the additional termination
    #"_processed".

    for item in os.listdir(origin):
        if item == "Original data":
            #print(origin + item)
            item += "/"
            for area in  os.listdir(origin + item):
                area += "/"
                if area[0] != ".":
                    for site_data in os.listdir(origin + item + area):
                        site_data += "/"
                        if site_data[-11:] == "_processed/":
                            parent_directory = origin + item + area + site_data
                            destination_directory = parent_directory[0:-1] + "_over80/"

                            #Detect if folder already exists. If true, skip.
                            if not path.isdir(destination_directory):
                                os.mkdir(destination_directory)

                                print("Filtering incomplete images in " + site_data)
                                for file in os.listdir(parent_directory):
                                    if file.endswith(".tif") or file.endswith(".png"):

                                        im = Image.open(parent_directory + '/' + file)
                                        width, height = im.size

                                        dead_pixel_count = 0
                                        for x in range(0,width):
                                            for y in range(0,height):
                                                if im.getpixel((x,y)) == 0:
                                                    dead_pixel_count += 1

                                        completeness = (width*height - dead_pixel_count) / (width*height)
                                        if completeness >= 0.75:
                                            im.save(destination_directory + file[:-4] + '_over80.png')

def preprocessing(origin):
    #Input: The project's file; the "Original data" file has to be
    #an immediate child.
    #Output: None.

    #Navigate through all folders within the "Original data and scripts" folder
    #, looking for folders that start with "Near" or "Ultra". For each of these,
    #an equivalent sibling folder is created with the additional termination
    #"_processed".

    def interpolation(image,x,y,type):
        #Input: Image object, integer coordinates, and classification of pixel in string.
        #Output: None.

        #The interpolation transformation is applied based on the pixel type.
        #image variable is an Image object
        #Max number of neighboring pixels that can be dead for the pixel to be interpolated.
        threshold = 2
        if type == 'no edge':
            neighbors = [image.getpixel((x,y+1)), image.getpixel((x,y-1)), image.getpixel((x+1,y)), image.getpixel((x-1,y))]
            pixel = 0
            count = 0
            for neighbor in neighbors:
                if neighbor != 0:
                    pixel += neighbor
                    count += 1
            if count > (len(neighbors) - threshold):
                image.putpixel((x,y), int(pixel/count))
        elif type == 'top edge':
            neighbors = [image.getpixel((x,y-1)), image.getpixel((x+1,y)), image.getpixel((x-1,y))]
            pixel = 0
            count = 0
            for neighbor in neighbors:
                if neighbor != 0:
                    pixel += neighbor
                    count += 1
            if count > (len(neighbors) - threshold):
                image.putpixel((x,y), int(pixel/count))
        elif type == 'bottom edge':
            neighbors = [image.getpixel((x,y+1)), image.getpixel((x+1,y)), image.getpixel((x-1,y))]
            pixel = 0
            count = 0
            for neighbor in neighbors:
                if neighbor != 0:
                    pixel += neighbor
                    count += 1
            if count > (len(neighbors) - threshold):
                image.putpixel((x,y), int(pixel/count))
        elif type == 'right edge':
            neighbors = [image.getpixel((x,y+1)), image.getpixel((x,y-1)), image.getpixel((x-1,y))]
            pixel = 0
            count = 0
            for neighbor in neighbors:
                if neighbor != 0:
                    pixel += neighbor
                    count += 1
            if count > threshold:
                image.putpixel((x,y), int(pixel/count))
        elif type == 'left edge':
            neighbors = [image.getpixel((x,y+1)), image.getpixel((x,y-1)), image.getpixel((x+1,y))]
            pixel = 0
            count = 0
            for neighbor in neighbors:
                if neighbor != 0:
                    pixel += neighbor
                    count += 1
            if count > (len(neighbors) - threshold):
                image.putpixel((x,y), int(pixel/count))
        elif type == 'corner 1':
            neighbors = [image.getpixel((x,y-1)), image.getpixel((x-1,y))]
            pixel = 0
            count = 0
            for neighbor in neighbors:
                if neighbor != 0:
                    pixel += neighbor
                    count += 1
            if count > (len(neighbors) - threshold):
                image.putpixel((x,y), int(pixel/count))
        elif type == 'corner 2':
            neighbors = [image.getpixel((x,y-1)), image.getpixel((x+1,y))]
            pixel = 0
            count = 0
            for neighbor in neighbors:
                if neighbor != 0:
                    pixel += neighbor
                    count += 1
            if count > (len(neighbors) - threshold):
                image.putpixel((x,y), int(pixel/count))
        elif type == 'corner 3':
            neighbors = [image.getpixel((x,y+1)), image.getpixel((x+1,y))]
            pixel = 0
            count = 0
            for neighbor in neighbors:
                if neighbor != 0:
                    pixel += neighbor
                    count += 1
            if count > (len(neighbors) - threshold):
                image.putpixel((x,y), int(pixel/count))
        elif type == 'corner 4':
            neighbors = [image.getpixel((x,y+1)), image.getpixel((x-1,y))]
            pixel = 0
            count = 0
            for neighbor in neighbors:
                if neighbor != 0:
                    pixel += neighbor
                    count += 1
            if count > (len(neighbors) - threshold):
                image.putpixel((x,y), int(pixel/count))

    def dead_pixel_fix(im, mask):
        #Input: Image object.
        #Output: Image object with dead pixels fixed.

        #Identify dead pixels and interpolate value from neighbors according to the
        #criteria in last lines of interpolation_criteria() method and interpolation method
        #of interpolation() method.
        width, height = im.size
        #Create original image object so you don't interpolate values for swaths
        #of black areas.
        original = im
        dead_pixel_count = 0
        fix_count = 0
        for x in range(0,width):
            for y in range(0,height):
                pixel = im.getpixel((x,y))
                if pixel == 0 or pixel == 256:
                    dead_pixel_count += 1
                    interpolate, pixeltype = interpolation_criteria(original,x,y)
                    if interpolate:
                        fix_count += 1
                        interpolation(im,x,y,pixeltype)
        #You can suppress satistics on dead pixels for each run.
        #print('This run of dead_pixel_fix() found ', dead_pixel_count, ' dead pixels and fixed ', fix_count, ' pixels.')
        return im

    for item in os.listdir(origin):
        if item == "Original data":
            item += "/"
            for area in  os.listdir(origin + item):
                if area[0] != ".":
                    area += "/"
                    for site_data in os.listdir(origin + item + area):
                        if (site_data[0:4] == "Near" or site_data[0:5] == "Ultra") and site_data.find("_") == -1:
                            site_data += "/"
                            parent_directory = origin + item + area + site_data
                            destination_directory = parent_directory[0:-1] + "_processed/"
                            prefix = ''
                            if site_data[0:4] == "Near":
                                prefix = "NIR"
                            elif site_data[0:5] == "Ultra":
                                prefix = "UVV"

                            #Detect if folder already exists. If true, skip.
                            if not path.isdir(destination_directory):
                                os.mkdir(destination_directory)
                                print("Preprocessing " + site_data)
                                for file in os.listdir(parent_directory):
                                    if file.endswith(".tif") or file.endswith(".png"):
                                        im = Image.open(parent_directory + file)
                                        mask = Image.open(parent_directory + file)
                                        processed = dead_pixel_fix(dead_pixel_fix(dead_pixel_fix(dead_pixel_fix(im, mask), mask), mask), mask)
                                        processed.resize((training_image_size,training_image_size)).save(destination_directory + '/' + prefix + file[:-4] + '_processed.png')

def all_alts(origin):
    #Input: The project's file; the "Original data" file has to be
    #an immediate child.
    #Output: None.

    def coordinates(parent, file):
        #Input:
        #Output:

        def id_site(string):
            return string[string.find('site') + 5: -1]

        def expand(number, div, dig):
            string1 = str(int(abs(div*(number//div))))
            string2 = str(int(abs(div*(number//div + 1))))
            while len(string1) < dig:
                string1 = '0' + string1
            while len(string2) < dig:
                string2 = '0' + string2

            return string1, string2


        target_long = ''
        target_lat = ''
        with open(parent + file, 'r') as content:
            content = content.readlines()
            line6 = content[6].strip() + " "
            target_lat = float(line6[line6.find("=") + 2:-1])
            line8 = content[8].strip() + " "
            target_long = float(line8[line8.find("=") + 2:-1])
        if target_long < 0:
            target_long += 360

        f_lat, s_lat = expand(target_lat, 30, 2)
        f_long, s_long = expand(target_long, 45, 3)

        northsouth = ''
        if target_lat < 0:
            NS = 'S'
        else:
            NS = 'N'

        name = '512_' + f_lat + NS + '_' + s_lat + NS + '_'  + f_long + '_' + s_long
        return target_long, target_lat, id_site(parent), name

    def altmap(target_long, target_lat, site_number, name, origin, destination_directory):
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

        def cut(longitude, latitude, sitenumber, source_image, origin, name, destination_directory):
            #Input: Coordiantes of minimum longitude and latitude of the site area,
            #the site number, the monster file filepath, and the parent folder
            #("Original data and scripts").
            #Output: None.

            #
            source = Image.open(source_image)
            #print("This image is: " + str(source.size[0]) + " x " + str(source.size[1]))


            #The coordinates of the top left corner of the source image. Positive 'y'
            #indexes are downward and positive 'x' indexes are rightward.
            sourcelong = float(source_image[-11:-8])
            #print("Source corner longitude: " + str(sourcelong))
            sourcelat = float(source_image[-15:-13])
            #print("Source corner latitude: " + str(sourcelat))

            if longitude < 0:
                longitude = 360 + longitude

            #print("Target corner longitude: " + str(longitude))
            #print("Target corner latitude: " + str(latitude))

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

            sink.save(destination_directory + 'SLDEM2015_512_' + str(abs(latitude))
            + name[8] + '_' + str(abs(latitude + 1)) + name[8] + '_' +
            str(longitude) + '_' + str(longitude + 1) + '.png')
            #Confirm the last line, the saving of the 'sink' image, was executed.
            print("Data succesfully saved for site " + str(sitenumber))

        #By default, Image does not take more than a pretty limited number of pixels
        #to protect itself from attacks. This command will alter that limit.
        Image.MAX_IMAGE_PIXELS = 353894400

        #Specify where the monster source file is.
        source = origin + "Original data/Global maps/SLDEM2015_" + name + ".JP2"
        #Pass the first longitude (west/east), the first latitude (south/north), append
        #the site number.

        cut(target_long, target_lat, site_number, source, origin, name, destination_directory)

    for item in os.listdir(origin):
        if item == "Original data":
            item += "/"
            for area in  os.listdir(origin + item):
                if area[0] != ".":
                    area += "/"
                    for site_data in os.listdir(origin + item + area):
                        if (site_data[0:4] == "Near" or site_data[0:5] == "Ultra") and site_data.find("_") == -1:
                            site_data += "/"
                            parent_directory = origin + item + area + site_data
                            for file in os.listdir(parent_directory):
                                if file[-4:] == ".map":
                                    target_long, target_lat, site_number, name = coordinates(parent_directory, file)

                                    destination_directory = origin + item + name + '/' + 'SLDEM2015, site ' + str(site_number)
                                    if not path.isdir(destination_directory):
                                        os.mkdir(destination_directory)
                                        destination_directory += '/'
                                        altmap(target_long, target_lat, site_number, name, origin, destination_directory)

def sort(origin):
    #Input: The project's file; the "Original data" file has to be
    #an immediate child.
    #Output: None.

    def coordinates(parent, file):
        #Input:
        #Output:

        def id_site(string):
            return string[string.find('site') + 5: -1]

        def expand(number, div, dig):
            string1 = str(int(abs(div*(number//div))))
            string2 = str(int(abs(div*(number//div + 1))))
            while len(string1) < dig:
                string1 = '0' + string1
            while len(string2) < dig:
                string2 = '0' + string2

            return string1, string2


        target_long = ''
        target_lat = ''
        with open(parent + file, 'r') as content:
            content = content.readlines()
            line6 = content[6].strip() + " "
            target_lat = float(line6[line6.find("=") + 2:-1])
            line8 = content[8].strip() + " "
            target_long = float(line8[line8.find("=") + 2:-1])
        if target_long < 0:
            target_long += 360

        f_lat, s_lat = expand(target_lat, 30, 2)
        f_long, s_long = expand(target_long, 45, 3)

        northsouth = ''
        if target_lat < 0:
            NS = 'S'
        else:
            NS = 'N'

        name = '512_' + f_lat + NS + '_' + s_lat + NS + '_'  + f_long + '_' + s_long
        return target_long, target_lat, id_site(parent), name

    for item in os.listdir(origin):
        if item == "Original data":
            item += "/"
            for area in  os.listdir(origin + item):
                if area == "Sort":
                    area += "/"
                    for site_data in os.listdir(origin + item + area):
                        if site_data[0:4] == "Near" or site_data[0:5] == "Ultra":
                            site_data += "/"
                            parent_directory = origin + item + area + site_data
                            for file in os.listdir(parent_directory):
                                if file[-4:] == ".map":
                                    target_long, target_lat, site_number, name = coordinates(parent_directory, file)

                                    shutil.move(parent_directory[:-1], origin + item + name + '/' + site_data[:-1])

origin = "/Users/santi/Documents/Semestre 1-2-3/MR3038- Estancia de investigación/Proyectos/Data fusion in lunar environment/Data workspace/"
training_image_size = 420
alarmV = True
replace_mosaics = False

print("Organizing your new data...")
sort(origin)
alarm(alarmV)

print("Extracting missing altitude maps...")
all_alts(origin)
alarm(alarmV)

print("Begin preprocessing images by removing dead pixels and maximizing contrast...")
preprocessing(origin)
alarm(alarmV)

print("")
print("Begin creating mosaics of site data...")
mosaic_create(origin, replace_mosaics)
alarm(alarmV)

print("")
print("Begin filtering out images with less than 80% content...")
over80_filter(origin)
alarm(alarmV)
