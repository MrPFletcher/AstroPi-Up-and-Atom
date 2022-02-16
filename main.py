#####Astro Pi competition code
# Members:
# Theale green school 2022
REPL = True  #some bits will only run on the pi so as we are building the code we can still try it here
#import libraries
#import orbit
from orbit import ISS
from time import sleep
#from astro_pi import AstroPi
if not REPL:
    from picamera import PiCamera
    from sense_hat import SenseHat
from pathlib import Path
import csv

#use pil for images
from PIL import Image
import numpy
#import datetime
from datetime import datetime, timedelta, timezone
from time import sleep

base_folder = base_folder = Path(__file__).parent.resolve()  #Path.cwd()

#define constants
LATITUDE = 5
LONGITUDE = 6
FUEL_TYPE = 7
THRESHOLD_SCALE = 2.5  #how much bigger than the average do we count as clouds
DURATION=1 # How long do we want the experiment to run for

#define functions
def read_file(file_name):
    """"
    This function reads the database of power stations from the file supplied and returns a 2d list of power stations
    :param file_name: The name of te csv file to read
    :type contents: 2d list
    :returns: 2d list of power stations
    """
    contents = []  #will hold the contents of the file
    in_file = open(file_name, "r")  #open the file
    for line in in_file:
        line = line.strip()
        entry = line.split(",")  #split each line at a comma
        contents.append(entry)  #add to list
    in_file.close()
    return contents

def take_photo():
  """
  This function accesses the camera and takes a phot, it return the photo. for test purposes it will return a fixed image
  :returns: an image taken with the camera, for debug it uses a fixed image
  """
  if not REPL:
    #add code to take the photo
    current_image=""
  else:
    current_image = Image.open("images/photo_07003_51845702676_o.jpg")
  return current_image

def get_time_stamp():
    """"
    This function return a string timestamp suitable for use in filenames
    :returns: a string with the date and time suitable for use in a file name
    """
    now = datetime.now(timezone.utc)
    return now.strftime("%Y%m%d_%H%M%S")


def create_csv(data_file):
    """
    This function creates a logfile, and adds te first row with column eaders, pass in te name of the file
    
    """
    with open(data_file, 'w') as f:
        writer = csv.writer(f)
        header = ("Date/time", "Latitude", "Longitide", "Elevation", "Compass", "Red Treshhold", "Green Treshhold", "Blue Treshhold")
        writer.writerow(header)


def add_csv_data(data_file, data):
    """
    This function is used to add data to te logfile, pass in te name of te file and te data to be written.
    Uses the csv library
    
    """
    with open(data_file, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)


def get_image_thresholds(image_array):
    """"
    This function takes an image array and finds the average value for each (non black) pixel, ith then returns scaled values for the thresholds for deciding whether a pixel is cloud or not. It uses the constant THRESHOLD_SCALE
    :returns: The RGB values above which we will consider the pixel to be a cloud
    """
    # work out the dimensions of the image
    width = image_array.shape[1]
    height = image_array.shape[0]
    pixel_count = width * height
    # Work out how many pixels are pure black (mostly the edge)
    # work out the average pixel intensity
    # calculate how many pixels are greater than the THRESHOLD_SCALE * average - this is not needed in the final code
    black = 0

    array_sum = image_array.sum(axis=(0, 1))
    red_threshold = array_sum[0] / (pixel_count - black) * THRESHOLD_SCALE
    if red_threshold > 250:
        red_threshold = 250
    green_threshold = array_sum[1] / (pixel_count - black) * THRESHOLD_SCALE
    if green_threshold > 250:
        green_threshold = 250
    blue_threshold = array_sum[2] / (pixel_count - black) * THRESHOLD_SCALE
    if blue_threshold > 250:
        blue_threshold = 250
    return red_threshold, green_threshold, blue_threshold


############################################
#
#   Main
#
############################################
if __name__ == '__main__':
    #power_stations list
    #[country,	country_long,	name,	gppd_idnr,	capacity_mw,	latitude,	longitude,	primary_fuel ]
    #sorted by longitutde then latitude

    power_stations = read_file("solarandwind2.csv")
    data_file = str(base_folder) +  "logfile.csv"
    create_csv(data_file)
    #run for three hours

    # Create a `datetime` variable to store the start time
    start_time = datetime.now()
    # Create a `datetime` variable to store the current time
    # (these will be almost the same at the start)
    now_time = datetime.now()
    # Run a loop for 2 minutes
    while (now_time < start_time + timedelta(minutes = DURATION)):
        #Get current coordinates of the ISS
        point = ISS.coordinates()
        
        #images taken are at whatever orientation the camera is in the ISS window and will need rotating
        if not REPL:
            ap = SenseHat()
            north = 360 - ap.get_compass()
        else:
            north = 120

        current_image = take_photo()
        #save the unmodified photo
        file_name = str(
            base_folder) + "/images/" + get_time_stamp() + "-output.jpg"
        current_image.save(file_name, format="jpeg")

        #current_image = current_image.rotate(360 - north)  
        #not needed at this point
        #the rotation angle will depend on the orientation of the pi
        current_image = current_image.convert(mode="RGB")
        
        image_array = numpy.asarray(current_image)
        

        red_threshold, green_threshold, blue_threshold = get_image_thresholds(
            image_array)
                
        # saving to log file
        row = (datetime.now(), point.latitude.degrees, point.longitude.degrees, point.elevation.km, north, red_threshold, green_threshold, blue_threshold)
        add_csv_data(data_file, row)
        # Update the current time
        now_time = datetime.now()
        sleep(17)
      except Exception as e:
        logger.error(f'{e.__class__.__name__}: {e}')


