UCSBClassChecker
================

Python script for checking if a UCSB class is open. Edit the search.json file to customize your search.

**NOTE:  This script requires bs4 and mechanize**

**Clone this repo, edit the search.json file, and in your terminal run:**

`python main.py`

You will prompted to login using the password associated with your UCSBNetID.

Your account info will be used for logging into GOLD and later for sending a notification email.

No login info is saved, but it is kept in session variables until the program quits.

**Hint:**
To have this script send you a text when a class opens up, lookup "carrier text email addresses" and use that for your "notify_email"
