from typing import Union
import base64
import requests
import os
import pathlib

def upload_to_imgur(image_full_path:Union[str, pathlib.Path]) -> str:
    """Upload a saved image to IMGUR.com and return the url in BB-code tags"""    

    # Convert image to base64
    image = base64.b64encode(open(image_full_path, 'rb').read())
    
    j1 = requests.post(
        os.getenv('IMGUR_API_URL'), 
        headers = {'Authorization': 'Client-ID '+os.getenv('IMGUR_API_ID')},
        data = {
            'key': os.getenv('IMGUR_API_KEY'), 
            'image': image, 
            'type': 'base64', 
            'name': os.getenv('IMGUR_IMG_NAME'), 
            'title': os.getenv('IMGUR_IMG_TITLE')
            }
        )
       
    message = f"[img]{j1.json()['data']['link']}[/img]\n"
    
    return message
    