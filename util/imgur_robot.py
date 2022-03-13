import base64
import requests
import os

def upload_to_imgur(files_dir, image_name, plot_title):
    """Upload a saved image to IMGUR.com and return the url in BB-code tags"""    

    # Convert image to base64
    image = base64.b64encode(open(files_dir + image_name, 'rb').read())
    
    j1 = requests.post(
        os.getenv('IMGUR_API_URL'), 
        headers = {'Authorization': 'Client-ID '+os.getenv('IMGUR_API_ID')},
        data = {'key': os.getenv('IMGUR_API_KEY'), 
                'image': image, 
                'type': 'base64', 
                'name': os.getenv('IMGUR_IMG_NAME'), 
                'title': os.getenv('IMGUR_IMG_TITLE')
                }
        )
       
    message = f"[b]{plot_title}[/b]\n[img]{j1.json()['data']['link']}[/img]"
    
    return message
    