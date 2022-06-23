from PIL import Image, ImageChops, ImageDraw
import PIL.ExifTags
import numpy

from pathlib import Path

def read_file(file_name):
    """"
    This function reads the database of power stations from the file supplied and returns a 2d list of power stations
    :param file_name: The name of te csv file to read
    :type contents: 2d list
    :returns: 2d list of power stations
    """
    contents = []  #will hold the contents of the file
    in_file = open(file_name, "r",encoding="utf8")  #open the file
    for line in in_file:
        line = line.strip()
        entry = line.split(",")  #split each line at a comma
        contents.append(entry)  #add to list
    in_file.close()
    return contents
def crop_to_circle(im):
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    #print(bigsize)
    mask = Image.new('L', bigsize, 0)
    #ImageDraw.Draw(mask).ellipse((2860, 800,11290,9040) , fill=255)
    ImageDraw.Draw(mask).ellipse((2740, 830,11070,9040) , fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, im.split()[-1])
    im.putalpha(mask)

power_stations = read_file("solarandwind2.csv")
# iss logs: 0: date time, 1:lat, 2: long 3: elevation of iss, 4: compass heading, 5:red, 6: green, 7: blue

ISS_logs = read_file("updatedISS.csv")
data_hits=[]
#loop through each of you logs, find the long and lat
for log in ISS_logs:
    #try:
        long = float(log[2])
        lat = float(log[1])
        #  loop through each of the power stations until you find one greater then long -4
        #    loop through until power station long > log+4
        im = Image.open(str(log[8]))
        im_exif= im.info['exif'] #im.getexif()
        im=im.convert('RGBA')
        im = im.rotate(-(float(log[4])))
        im_exif= im.getexif()
        crop_to_circle(im)
        #image_array = numpy.asarray(im)
        print("File :", str(log[8]))
        for farm in power_stations:
            #print("step")
            if float(farm[6]) > (long - 4) and float(farm[6]) < (long + 4):
                #print("long")
                #      if the lat of power station > lat -4 and < lat+4
                if float(farm[5]) > (lat - 4) and float(farm[5]) < (lat + 4):
                  #print("lat")
                  # solar farm is in image
                  # lat, long give the centre of the image and we know how
              
                  change_in_long=long-float(farm[6])
                  change_in_lat=lat-float(farm[5])
                  # big each pixel is convert the difference between the lat long
                  # (of the picture)
                  # and the lat long of the power station into an offset in pixels
                  long_offset=change_in_long*128
                  lat_offset=change_in_lat*128
                  # from this we can work out the coordinate of the power station in 
                  # the image and check it for colour
                  farm_x= 2028+float(long_offset) #find x coordinate
                  farm_y= 1520-float(lat_offset) #find y coordinate
                  farm_colour=im.getpixel((farm_x,farm_y)) #get the colour
                  data_line=[farm[0], farm[3],farm[5],farm[6],lat,long, farm_x, farm_y, farm_colour]
                  data_hits.append(data_line)
                  print(data_line)
                  draw=ImageDraw.Draw(im)
                  draw.ellipse((farm_x-20,farm_y-20,farm_x+20, farm_y+20),outline="red")
                  try:
                    im.save('croppedr\\'+str(log[8])[7:-3]+"png") #, exif=im.info["exif"])#im_exif)
                  except:
                      print("failed to save")
    #        copy the image for processing
    #except:
    #    print("File not found", str(log[8]))
#show the data
myfile=open("matchinfo.csv","w")
for line in data_hits:
  myfile.write(line[0] +","+line[1]+","+line[2]+","+line[3]+","+line[4]+","+line[5]+","+line[6]+","+line[7]+","+line[8][0]+","+line[8][1]+","+line[8][2])
directory = 'images'
myfile.close()
