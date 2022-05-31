import sys
import configparser
import os
from pathlib import Path
import pyclip
import boto3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

def process_text_analysis():

    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    clipboard_image_data = clipboard.wait_for_image()

    if clipboard_image_data is None:
        msg=('Clipboard does not contain image data. ' +
             'Screenshot an image containing some text and try again.')
        print (msg)
        sys.exit()

    tmp_file_path = '/tmp/testimage.png'
    temp_image = clipboard_image_data
    temp_image.savev(tmp_file_path, 'png', [], [])

    png_file = open(tmp_file_path, 'rb')
    img_byte_arr = bytearray(png_file.read())

    client = boto3.client(
        get_config_value('aws_config','aws_service_name'),
        region_name=get_config_value('aws_config','aws_region_name'),
        aws_access_key_id=get_config_value('aws_config','aws_access_key_id'),
        aws_secret_access_key=get_config_value('aws_config','aws_secret_access_key')
    )

    try: 
        response = client.detect_document_text(
            Document={'Bytes': img_byte_arr}
        )

        extracted_text = ''
        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                extracted_text += item["Text"] + "\n"
        pyclip.copy(extracted_text)
    except Exception as e: 
        print(e)

def get_config_value(config_section, config_item_name):
  path = Path(__file__)
  runtime_path = path.parent.absolute()
  config_path = os.path.join(runtime_path, "config.ini")
  config = configparser.ConfigParser()
  config.read(config_path)
  return config.get(config_section, config_item_name)

def main():
  process_text_analysis()

if __name__ == "__main__":
    main()
