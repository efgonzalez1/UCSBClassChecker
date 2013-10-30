UCSBClassChecker
================

Python script for checking if a UCSB class is open. Edit the search.json file to customize your search.

**Clone this repo, edit the search.json file, and run in your terminal.**

**NOTE:  This script requires beautifulsoup4 and mechanize**

Requirements can be installed with:  `pip install -r requirements.txt`

To start searching run: `python gold.py`


You will be prompted to login using the password associated with your UCSBNetID.

Your account info will be used for logging into GOLD and later for sending a notification email.

No login info is saved, but it is kept in session variables until the program quits.

**Hint:**
To have this script send you a text when a class opens up, use one of these for your "notify_email":


* Tmobile: `10digitphonenumber@tmomail.net`
* AT&T:  `10digitphonenumber@txt.att.net`
* Verizon: `10digitphonenumber@vtext.com`
* Sprint: `10digitphonenumber@messaging.sprintpcs.com`

