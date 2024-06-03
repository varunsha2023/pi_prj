import subprocess
import time
from datetime import datetime
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from flask import Flask, render_template, request

# Define scope
SCOPES = ['https://www.googleapis.com/auth/drive']

# Path to the credentials file downloaded from Google Cloud Console
CREDS_FILE = '/home/pi/Desktop/cred.json'

app = Flask(__name__)

def authenticate():
    creds = None
    # Load credentials from file if it exists
    if os.path.exists('/home/pi/Desktop/token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        print("Error: token.json file not found.")
    return creds

def upload_image(image_path, image_name, folder_id):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {
        'name': image_name,
        'parents': [folder_id]  # Specify the folder ID
    }
    media = MediaFileUpload(image_path, mimetype='image/jpeg')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print('File ID: %s' % file.get('id'))

def capture_image(image_number):
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"image_{image_number:04d}_{current_time}.jpg"
    filepath = f"/home/pi/Pictures/{filename}"
    command = ["gphoto2", "--capture-image-and-download", "--filename", filepath]
    subprocess.run(command)
    print(f"Captured {filename}")
    return filepath

def capture_continuous(folder_id):
    image_number = 1
    while True:
        image_path = capture_image(image_number)
        upload_image(image_path, os.path.basename(image_path), folder_id)
        image_number += 1
        time.sleep(1)  # Wait for 1 second between captures

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        folder_id = '1QA-AEi7rzyICXGvU6ZJyC5MeHymX1wyr'
        capture_continuous(folder_id)
        return 'Capturing images...'
    else:
        return render_template('index.html')

@app.route('/capture')
def capture():
    folder_id = '1QA-AEi7rzyICXGvU6ZJyC5MeHymX1wyr'  # You can pass this as a parameter in the request if needed
    capture_continuous(folder_id)
    return 'Capturing images...'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
