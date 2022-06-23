
from pathlib import Path
from PIL import Image
import numpy

#define constants
LATITUDE = 5
LONGITUDE = 6
FUEL_TYPE = 7
THRESHOLD_SCALE = 2.5  #how much bigger than the average do we count as clouds

def read_file(file_name):
    """"
    This function reads the database of power stations from the file supplied and returns a 2d list of power stations
    :param file_name: The name of te csv file to read
    :type contents: 2d list
    :returns: 2d list of power stations
    """
    contents = []  #will hold the contents of the file
    in_file = open(file_name, "r", encoding="utf8")  #open the file
    for line in in_file:
        line = line.strip()
        entry = line.split(",")  #split each line at a comma
        contents.append(entry)  #add to list
    in_file.close()
    return contents

def is_it_night(image_array):
    """"
    This function takes an image array and works out whether it's night time
    """
    # work out the dimensions of the image
    window=500
    width = image_array.shape[1]
    height = image_array.shape[0]
    pixel_count =  width * height
    start_w= (width //2)-window
    stop_w = (width //2)+window
    start_h= (height//2)-window
    stop_h= (height //2) + window
    im_trim = image_array[start_w:stop_w, start_h:stop_h]
    pixel_count = (stop_w - start_w) * (stop_h -start_h)
    x_range = (stop_w - start_w) 
    y_range= (stop_h -start_h)
    black = 0
    
    array_sum = im_trim.sum(axis=(0, 1))
    red_threshold = array_sum[0] / (pixel_count )
    green_threshold = array_sum[1] / (pixel_count ) 
    blue_threshold = array_sum[2] / (pixel_count )
    if  red_threshold < 10 and  green_threshold < 10 and blue_threshold < 10:
      return True
    else:

      return False
def convert_time_stamp(time):
  #print(time)
  fname=time[0:4]+time[5:7]+ time[8:10]+"_"+time[11:13]+time[14:16]+time[17:19]
  #print(fname)
  return fname

#############################################################
power_stations = read_file("solarandwind2.csv")
ISS_logs = read_file("logfile.csv")
#remove the first line
#files=[]
ISS_logs = ISS_logs[1:]
for log in ISS_logs:
  for i in range(1,8):
    log[i]=float(log[i])
  #files.append(str("images/" + convert_time_stamp(log[0]) + "-output.jpg"))
  

#print(ISS_logs[0])
# assign directory
directory = 'images'
 
# iterate over files in
# that directory
files = Path(directory).glob('*')
for file in files:
  f_hour=int(str(file)[16:18])
  f_minutes=int(str(file)[18:20])
  f_sec=int(str(file)[20:22])
  #print (f_hour,f_minutes,f_sec)
  

  #print(file)
  for log in ISS_logs:
    hour=int(log[0][11:13])
    minutes=int(log[0][14:16])
    secs= int(log[0][17:19])
    if secs > 55:
        wrap="Down"
    elif secs <=6:
        wrap="Up"
    else:
        wrap="No"
    if wrap == "No":
      if(f_hour == hour and f_minutes == minutes and (f_sec > secs -6) and (f_sec < secs +6)) : #and wrap == "No" :# or (f_hour == hour and f_minutes == minutes-1 and (f_sec > 0)and (f_sec < secs +6)) and wrap=="Down"or (f_hour == hour and f_minutes == minutes+1 and (f_sec > secs-6)and (f_sec < 60)) and wrap=="Up" :
        #print("Matched:", log)
        log.append(str(file))
        current_image = Image.open(file)
        current_image = current_image.convert(mode="RGB")
        image_array = numpy.asarray(current_image)
        if is_it_night(image_array) :
            log.append("Night")
        else:
            log.append("Day")
    elif wrap == "Down":
        # near the minute
      if(f_hour == hour and f_minutes == minutes and (f_sec > secs -6)) or  (f_hour == hour and f_minutes == minutes+1 and(f_sec < 6)) : #and wrap == "No" :# or (f_hour == hour and f_minutes == minutes-1 and (f_sec > 0)and (f_sec < secs +6)) and wrap=="Down"or (f_hour == hour and f_minutes == minutes+1 and (f_sec > secs-6)and (f_sec < 60)) and wrap=="Up" :
        #print("Matched:", log)
        log.append(str(file))
        current_image = Image.open(file)
        current_image = current_image.convert(mode="RGB")
        image_array = numpy.asarray(current_image)
        if is_it_night(image_array) :
              log.append("Night")
        else:
              log.append("Day")
    elif wrap == "Up":
        # near the minute
      if(f_hour == hour and f_minutes == minutes-1 and (f_sec > 55)) or  (f_hour == hour and f_minutes == minutes and(f_sec < secs+ 6)) : #and wrap == "No" :# or (f_hour == hour and f_minutes == minutes-1 and (f_sec > 0)and (f_sec < secs +6)) and wrap=="Down"or (f_hour == hour and f_minutes == minutes+1 and (f_sec > secs-6)and (f_sec < 60)) and wrap=="Up" :
        #print("Matched:", log)
        log.append(str(file))
        current_image = Image.open(file)
        current_image = current_image.convert(mode="RGB")
        image_array = numpy.asarray(current_image)
        if is_it_night(image_array) :
              log.append("Night")
        else:
              log.append("Day")
    #    if f_hour == hour and f_minutes == minutes and (secs -6)< 0:
    #        print("file not matched: ",file, f_sec, secs)
     
myFile=open("updatedISS.csv","w")
for log in ISS_logs:
    line=""
    for item in log:
        line = line + str(item) +","
    line = line[:-1]
    myFile.write(line+"\n")
myFile.close()

