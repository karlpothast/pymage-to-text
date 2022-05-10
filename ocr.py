import sys
import io
import configparser
import os
from pathlib import Path
from PIL import ImageGrab
import pyperclip
import boto3

def process_text_analysis():
    clipboard_image_data = ImageGrab.grabclipboard()
    if clipboard_image_data is None:
        msg=('Clipboard does not contain image data. ' +
             'Screenshot an area containing a block of text and try again.')
        print (msg)
        sys.exit()

    img_byte_arr = io.BytesIO()
    temp_image = clipboard_image_data
    temp_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    client = boto3.client(
        get_config_value('aws_config','aws_service_name'),
        region_name=get_config_value('aws_config','aws_region_name'),
        aws_access_key_id=get_config_value('aws_config','aws_access_key_id'),
        aws_secret_access_key=get_config_value('aws_config','aws_secret_access_key')
    )

    response = client.detect_document_text(
        Document={'Bytes': img_byte_arr}
    )

    extracted_text = ''
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            extracted_text += item["Text"] + "\n"
    pyperclip.copy(extracted_text)

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
