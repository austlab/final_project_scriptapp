""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py image_dir_path [apod_date]

Parameters:
  image_dir_path = Full path of directory in which APOD image is stored
  apod_date = APOD image date (format: YYYY-MM-DD)

History:
  Date        Author             Description
  2022-04-28  Austin Labrecque   Final project for Scripting Applications. Completed using template authored by Prof. Jeremy Dalby
"""
from sys import argv, exit
from datetime import datetime, date
from hashlib import sha256
import os
from os import path
import requests
import sqlite3
import ctypes

def main():

    # Determine the paths where files are stored
    image_dir_path = get_image_dir_path()
    db_path = path.join(image_dir_path, 'test_apod_images.db')

    # Get the APOD date, if specified as a parameter
    apod_date = get_apod_date()

    # Create the images database if it does not already exist
    create_image_db(db_path)

    # Get info for the APOD
    apod_info_dict = get_apod_info(apod_date)
    
    # Download today's APOD
    image_url = apod_info_dict['url']
    image_msg = download_apod_image(image_url)
    image_path = get_image_path(image_url, image_dir_path)

   
    image_sha256 = calc_hash(image_path)
    image_size = calc_size(image_msg)

    

    print_apod_info(image_url, image_path, image_size, image_sha256)

    # Add image to cache if not already present
    if not image_already_in_db(db_path, image_sha256):
        save_image_file(image_msg, image_path)
        add_image_to_db(db_path, image_path, image_size, image_sha256)

    # Set the desktop background image to the selected APOD
    set_desktop_background_image(image_path)

def get_image_dir_path():
    """
    Validates the command line parameter that specifies the path
    in which all downloaded images are saved locally.

    :returns: Path of directory in which images are saved locally
    """
    if len(argv) >= 2:
        dir_path = argv[1]
        if path.isdir(dir_path):
            print("Images directory:", dir_path+"\n")
            return dir_path
        else:
            print('Error: Non-existent directory', dir_path)
            exit('Script execution aborted')
    else:
        print('Error: Missing path parameter.')
        exit('Script execution aborted')

def get_apod_date():
    """
    Validates the command line parameter that specifies the APOD date.
    Aborts script execution if date format is invalid.

    :returns: APOD date as a string in 'YYYY-MM-DD' format
    """    
    if len(argv) >= 3:
        # Date parameter has been provided, so get it
        apod_date = argv[2]

        # Validate the date parameter format
        try:
            datetime.strptime(apod_date, '%Y-%m-%d')
        except ValueError:
            print('Error: Incorrect date format; Should be YYYY-MM-DD')
            exit('Script execution aborted')
    else:
        # No date parameter has been provided, so use today's date
        apod_date = date.today().isoformat()
    
    print("APOD date:", apod_date)
    return apod_date

def get_image_path(image_url, dir_path):
    """
    Determines the path at which an image downloaded from
    a specified URL is saved locally.

    :param image_url: URL of image
    :param dir_path: Path of directory in which image is saved locally
    :returns: Path at which image is saved locally
    """
    split_url = image_url.split('/')[-1]
    img_path = os.path.join(dir_path, split_url)
    
    return img_path

def get_apod_info(date):
    """
    Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    :param date: APOD date formatted as YYYY-MM-DD
    :returns: Dictionary of APOD info
    """    
    url_apod = "https://api.nasa.gov/planetary/apod"
    params = {
        'api_key': 'StB7u7BFs0gOn1jUthmPqodlxAGGTPUXEh8Pc9Ab',
        'date': date
    }
    
    response_apod = requests.get(url_apod, params=params).json()
    
    
    return response_apod

def print_apod_info(image_url, image_path, image_size, image_sha256):
    """
    Prints information about the APOD

    :param image_url: URL of image
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """ 
    print("\nRetrieving image from", image_url,"\n")
    print("Saving to location:", image_path,"\n")
    print("Image size:", str(image_size), "Bytes\n")
    print("Calculated SHA256 value:", image_sha256)   
    return None

def download_apod_image(image_url):
    """
    Downloads an image from a specified URL.

    :param image_url: URL of image
    :returns: Response message that contains image data
    """
    response = requests.get(image_url)
    if response.status_code == 200:
        img_data = response
        
    return img_data
    
    

def save_image_file(image_msg, image_path):
    """
    Extracts an image file from an HTTP response message
    and saves the image file to disk.

    :param image_msg: HTTP response message
    :param image_path: Path to save image file
    :returns: None
    """
    with open(image_path, 'wb') as fp:
        fp.write(image_msg.content)
        
    
    return None

def calc_hash(image_path):
   
    encoded_path = image_path.encode(encoding = 'utf-8', errors = 'strict')
    readable_hash = sha256(encoded_path).hexdigest()
    return readable_hash
        
def calc_size(image_msg):
    size = len(image_msg.content)
    return size


def create_image_db(db_path):
    """
    Creates an image database if it doesn't already exist.

    :param db_path: Path of .db file
    :returns: None
    """
    
    myConnection = sqlite3.connect(db_path)
    myCursor = myConnection.cursor()
    createImageTable = """CREATE TABLE IF NOT EXISTS Images (
                        image_path TEXT NOT NULL,
                        image_size TEXT NOT NULL,
                        image_hash TEXT NOT NULL
        );"""
    
    myCursor.execute(createImageTable)
    myConnection.commit()
    myConnection.close()
    return None

def add_image_to_db(db_path, image_path, image_size, image_sha256):
  """
    Adds a specified APOD image to the DB.

    :param db_path: Path of .db file
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """
    
  myConnection = sqlite3.connect(db_path)
  myCursor = myConnection.cursor()

  addImage = """INSERT INTO Images   (image_path,
                                      image_size, 
                                      image_hash)
                                      VALUES (?, ?, ?);"""



  imageInfo = (image_path,
              image_size, 
              image_sha256)

  myCursor.execute(addImage, imageInfo)

  myConnection.commit()
  myConnection.close()
  return None

def image_already_in_db(db_path, image_sha256):
  """
    Determines whether the image in a response message is already present
    in the DB by comparing its SHA-256 to those in the DB.

    :param db_path: Path of .db file
    :param image_sha256: SHA-256 of image
    :returns: True if image is already in DB; False otherwise
    """ 
  myConnection = sqlite3.connect(db_path)
  myCursor = myConnection.cursor()
  
  myCursor.execute("""SELECT image_hash FROM Images WHERE image_hash=?""", (image_sha256,))
   
  result = myCursor.fetchall()
  
  if result:
    print("\nThis image has already been downloaded. Remove entry from the database to redownload.")
    return True
  else:
    print("\nSaving image")
    return False
        

def set_desktop_background_image(image_path):
    """
    Changes the desktop wallpaper to a specific image.

    :param image_path: Path of image file
    :returns: None
    """
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0)
    
    return None

main()