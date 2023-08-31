import requests
import numpy as np
import cv2
from skimage import measure
import pyproj
import math
from datetime import datetime


##sub routine
def manual_input_location():
  """
  This function prompts the user to input lat1, lon1, and alt1.

  Returns:
    lat1, lon1, alt1: The user-inputted latitude, longitude, and altitude.
  """
  lat1 = input("Enter the latitude (default is 24.0): ")
  if lat1 == "":
    lat1 = 24.0
  else:
    try:
      lat1 = float(lat1)
    except ValueError:
      print("Invalid latitude value. Please enter a number.")
      lat1 = None
  lon1 = input("Enter the longitude (default is 120.5): ")
  if lon1 == "":
    lon1 = 120.5
  else:
    try:
      lon1 = float(lon1)
    except ValueError:
      print("Invalid longitude value. Please enter a number.")
      lon1 = None
  alt1 = input("Enter the altitude (default is 10.0): ")
  if alt1 == "":
    alt1 = 10.0
  else:
    try:
      alt1 = float(alt1)
    except ValueError:
      print("Invalid altitude value. Please enter a number.")
      alt1 = None
  return lat1, lon1, alt1
  
##
# Taichun Coordinates of two locations (latitude, longitude)
#lat1 = 24.0  # Example latitude of Location 1 (New York City)
#lon1 = 120  # Example longitude of Location 1
#alt1 = 10.000    # Altitude in meters for Location 1
#copy from google map
#lat1,lon1=22.63281984160608, 120.26223748602828
# Manual input of latitude and longitude for Location 1

# datetime object containing current date and time
now = datetime.now()
print("now =", now)
# YY-mm-dd-H-M
dt_string = now.strftime("%Y-%m-%d")
min_s = int(now.strftime("%M"))
hour_s=int(now.strftime("%H"))

min_s30 = int((min_s-10) / 30)
#print(hour_s, min_s, min_s30)
if min_s30>1:
   min_s300="30"
   if hour_s < 24:
      hour_s=hour_s-1
   else:
      hour_s=0
else:
   min_s300="00"
   if hour_s < 24:
      hour_s=hour_s
     # print(hour_s)
   else:
      hour_s=0
            
print("date and time =", dt_string, hour_s, min_s30)

filename="twRS_"+ dt_string +"-"+str(hour_s)+"-"+min_s300 +".csv"
fileObj = open(filename, "w")

lat1,lon1,alt1=manual_input_location() 

 

lat0=28.0
lon0=116.0
alt0=60000.0
lon0_px=16  #pixel origin x
lat0_py=18  #pixel origin y
distance_per_pixelx=1276.416 #m
distance_per_pixely=1273.857  #m
distance_per_degx=1017303.56/(126-116)
distance_per_degy=886075.49/(28-20)
##set WGS84
geod = pyproj.Geod(ellps="WGS84")


# Read the image using OpenCV
image_url = "https://www.cwb.gov.tw/Data/satellite/TWI_IR1_Gray_800/TWI_IR1_Gray_800-"+dt_string+"-"+str(hour_s)+"-"+min_s300+".jpg"
fileObj.write(image_url)
print(image_url)
# Download the image using requests
response = requests.get(image_url)
image_data = response.content

# Load the image using OpenCV
nparr = np.frombuffer(image_data, np.uint8)
image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

# Define the lower and upper bounds for highlighting
lower_bound = 228
upper_bound = 245

# Create a mask for values between the specified bounds
highlight_mask = cv2.inRange(image, lower_bound, upper_bound)






# Apply the mask to the original image to highlight the regions
highlighted_image = cv2.bitwise_and(image, image, mask=highlight_mask)
##save highlight images
cv2.imwrite("image_with_filtered_colors_highlight.jpg", highlighted_image)
##draw the circles
# Find circles using Hough Circle Transform
circles = cv2.HoughCircles(
    image=highlighted_image,
    method=cv2.HOUGH_GRADIENT,
    dp=1.4,
    minDist=3.8,
    param1=10,
    param2=20,
    minRadius=4,
    maxRadius=25
 
)

##print ircle
if circles is not None:
    circles = np.uint16(np.around(circles))
    print("red sprite cloud candidates, Longitude (deg), Latitude(deg), Cloud Radius(Km), Distance (Km), RS altitude ange (deg), Azimuth Ange(deg)\n")
    fileObj.write("red sprite cloud candidates, Longitude (deg), Latitude(deg), Cloud Radius(Km), Distance (Km), RS altitude ange (deg), Azimuth Ange(deg)\n")
    for circle in circles[0, :]:
     
        x, y, radius = circle
        if y>36:
          cv2.circle(highlighted_image, (x, y), radius, (128, 255, 100), 2)  # Draw circle
          lat=(-(y-lat0_py)*distance_per_pixely/distance_per_degy+lat0)
          lon=((x-lon0_px)*distance_per_pixelx/distance_per_degx+lon0)
          rCloud=(radius*distance_per_pixelx/1000.0) #Km
          
          azimuth1, azimuth2, distance = geod.inv(lon1, lat1, lon, lat)
          
          # Calculate the altitude angle
          altitude_angle_rad = math.atan2(alt0 - alt1, distance)

          # Convert the altitude angle from radians to degrees
          altitude_angle_deg = math.degrees(altitude_angle_rad)
          if azimuth1 <0:
             azimuth1=360+azimuth1
          print (f'Cloud, {lon :.2f}, {lat :.2f}, {rCloud :.3f}, {distance/1000.0:.2f}, {altitude_angle_deg:.2f}, {azimuth1:.2f} ')
          fileObj.write(f'Cloud, {lon :.2f}, {lat :.2f}, {rCloud :.3f}, {distance/1000.0:.2f}, {altitude_angle_deg:.2f}, {azimuth1:.2f} \n')

#close file
fileObj.close()


cv2.imwrite("image_with_filtered_colors_highlight_cirles.jpg", highlighted_image)


# Display or save the highlighted image
#cv2.imshow("Highlighted Image", highlighted_image) #highlighted_image)
#cv2.waitKey(0)
#cv2.destroyAllWindows()



##middile line
lower_bound = 122
upper_bound = 184

# Create a mask for values between the specified bounds
highlight_mask = cv2.inRange(image, lower_bound, upper_bound)

# Apply the mask to the original image to highlight the regions
highlighted_image = cv2.bitwise_and(image, image, mask=highlight_mask)
cv2.imwrite("image_with_filtered_colors_middlelight.jpg", highlighted_image)


# Display or save the highlighted image
#cv2.imshow("Highlighted Image", highlighted_image)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
