UCSBClassChecker
================

Python script for checking if a UCSB class is open. Edit the search.json file to customize your search.

Clone this repo and in your terminal run:

python main.py

You will prompted to login using the password associated with your UMAIL account.

Then this account info will be used for sending the notification email.

No login info is saved, but it is kept in session variables until the program quits.

Hint:  
To have this script send you a text when a class opens up, lookup "carrier text email addresses" and use that for your "notify_email"
