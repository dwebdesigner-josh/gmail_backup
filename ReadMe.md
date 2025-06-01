WHAT IT IS/WHAT IT DOES:
Google Cloud Console & Gmail API based Python app which downloads all targeted emails from your gmail inbox
  
  TARGET EMAILS:
  Downloads all emails from a specified sender
  
  OUTPUT:
  Saves email text (email subjects and bodies) into separate .txt files for each email 
  Downloads all email attachments of any file type, keeping their original file names and skipping duplicates (works for images, videos, audio, etc as long as it's   attached to the email - have not tested for imbedded images, only those added as attachments)

How to set up app with Gmail API/Google Cloud Console:
https://console.cloud.google.com/
- Log in
- -  it may ask you to add payment info (for google cloud console subscription) - you can just close this page/go to home page and bypass it
- Click the project dropdown (top bar) → “New Project”
- Name it something like GmailDownloader, then click Create
- Set up OAuth Consent Screen (hamburger menu>API's & Services>Oauth Consent Screen)
  - Branding tab - fill out required info
  - Audience tab - make sure Publishing status is Testing
  -   scroll down to Test users - add whichever gmail account you would like to backup
- Enable Gmail API
  - In your project dashboard, go to the Navigation menu (≡) → APIs & Services → Library
  - Search for Gmail API
  - Click Gmail API, then click Enable
- Configure OAuth 2.0 credentials
  - Go to APIs & Services → Credentials
  - Click + Create Credentials → OAuth client ID
  - If prompted to configure a consent screen:
    - Choose External
    - App name: e.g., Gmail Attachment Downloader
    - Add your email, and save (you don’t need to add scopes or test users for local use)
  - Then:
    - Application type: Desktop App
    - Name: e.g., DesktopClient
    - Click Create
    - Click Download JSON on the credentials page — save this file as credentials.json and once you have the applocation directory created below, move this credentials.json file into that same folder as your .py script
      
On your local environment:
- install Python https://www.python.org/downloads/
- open Linux/Unix shell/PowerShell/etc. based on your OS
- mkdir C:/applocation
    - (or other external drive - make sure whichever drive you use has enough space for the backup downloads)
- cd /applocation
    - python --version
        - check to make sure python is installed properly (should return version number)
    - pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
    - copy gmail_downloader.py into the application directory
    - don't worry about making /applocation/attachments or /applocation/email_texts subdirectories as these will be automatically created by the program if not already there
    - copy credentials.json from earlier into the application directory
 
Run the program:
- make sure you have configured the .py script to download emails from the specified sender of your choice:
      SENDER_EMAIL = 'example@example.com'  # Replace with actual sender email

- python gmail_downloader.py
  - should open a browser window for you to select the account you want to backup the inbox from, and approve access to it
  - make sure the account you select is listed in your test users (see earlier steps) in your app's google cloud console settings
  - Once you approve, a token.json file will be created. You will not have to approve access again
      - to backup emails for a different gmail account after this, just delete the token file, and when asked to reauthenticate, choose the desired account
- the program will then run, and you will see files that are saved or skipped (skipped if duplicate attachment file names exist - duplicate emails should be fine however, as each will be saved with their unique message ID as part of the title of the file)
- email subject and body (if any) will be saved in the .txt files, each being named based on their source email's date and message ID
    -  these will be saved in the email_texts subdirectory of your applocation directory
- attachments from emails will be downloaded into the attachements subdirectory of your applocation directory

Cleanup

- for privacy/safety, once you are finished with the app, you can remove its access to your accounts with the following steps:
- delete token file
- open  https://myaccount.google.com/permissions
    - Third-party apps & services
    - look for the name of your App
    - click on it and click Delete all connections you have with (name of app)
    - repeat this process on all gmail accounts you backed up
- optional:
    - Delete your google cloud console app
      - Go to https://console.cloud.google.com
        - Click your project
        - 3 dots button in top right corner next to profile icon
        - Project Settings
        - At the top, click "Shut down"
        - Confirm deletion
    - This will revoke:
      - The app’s client ID and secret
      - Any OAuth tokens tied to it
      - Gmail API access through that app
- if you want to use this in the future:
    - don't delete the app
        - keep your credentials.json file in a secure location
    - delete the app
        - remake the app in the future when you need to use it again
