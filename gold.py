from getpass import getpass
from bs4 import BeautifulSoup
import mechanize
import smtplib
import time
import json


class Gold(object):

    def __init__(self):
        self.notify_email = None
        self.quarter = None
        self.user = None
        self.pw = None
        self.br = mechanize.Browser()
        self.welcome_msg = "UCSB Class Checker (Exit at any time with Ctrl-C)"
        self.exit_msg = "\n\nThanks for using the UCSB Class Checker!\n"
        # Read search file to get username on login screen
        self.search_params = self.read_search_file("search.json")
        self.start()

    def start(self):
        print("\n%s" % self.welcome_msg)
        # Trick to underline my welcome message with the correct # of =
        print("%s" % ''.join(["=" for i in range(len(self.welcome_msg))]))
        while True:
            try:
                self.login()
                self.search(self.search_params)
                self.wait()
            except KeyboardInterrupt:
                print(self.exit_msg)
                exit()

    def login(self):
        LOGIN_URL = 'https://my.sa.ucsb.edu/gold/Login.aspx'
        USER_FIELD = 'ctl00$pageContent$userNameText'
        PW_FIELD = 'ctl00$pageContent$passwordText'
        CHECKBOX_FIELD = 'ctl00$pageContent$CredentialCheckBox'
        # Sometimes I get random mechanize errors
        # So try to login til successful
        while True:
            try:
                if not self.pw:
                    print("Logging in as: %s" % self.user)
                    self.pw = getpass("UCSB NetID Password: ")
                ### EDITS FOR HEROKU COMPATIBILITY ###
                # Comment out the above 3 lines relating to the "if" statement
                # Uncomment the following line (NOTE IDK HOW SECURE THIS IS)
                # self.pw = "ENTER_YOUR_GOLD_PW_HERE"
                # Open login page, select login form, modify fields, submit
                self.br.open(LOGIN_URL)
                self.br.select_form(nr=0)
                form = self.br.form
                form[USER_FIELD] = self.user
                form[PW_FIELD] = self.pw
                # Checkbox has weird way of being set
                form[CHECKBOX_FIELD] = ['on']
                # Should not get the login page again after login attempt
                response = self.br.submit()
                soup = BeautifulSoup(response.read())
                if soup.title.string == 'Login':
                    print("> Login unsuccessful. Check credentials.\n")
                    self.pw = None
                else:
                    print("> Login successful.")
                    break
            except (EOFError, KeyboardInterrupt):
                print(self.exit_msg)
                exit()
            except:
                print("Unexpected error logging in. Trying again...")

    def read_search_file(self, path):
        search_params = None
        with open(path) as f:
            search_file = json.load(f)
            self.user = search_file["ucsb_net_id"]
            self.notify_email = search_file["notify_email"]
            self.mins_to_wait = float(search_file["mins_to_wait"])
            self.quarter = search_file["quarter"]
            search_params = search_file["search_params"]

        blank = {"enroll_code": "", "department": "", "course_num": ""}
        # Remove duplicate searches and fix department string if necessary
        dupe_free_search_params = []
        for item in search_params:
            # Fix department string by appending a space until it is 5 chars
            while (len(item['department']) < 5) and (item['department'] != ''):
                item['department'] += ' '
            if item not in dupe_free_search_params:
                dupe_free_search_params.append(item)
        # Remove blanks searches
        # (Couldn't figure out how to remove in one pass with dupes)
        while True:
            try:
                dupe_free_search_params.remove(blank)
            except ValueError:
                break
        return dupe_free_search_params

    def search(self, search_params):
        SEARCH_URL = 'https://my.sa.ucsb.edu/gold/CriteriaFindCourses.aspx'
        QUARTER_FIELD = 'ctl00$pageContent$quarterDropDown'
        ENROLL_CODE_FIELD = 'ctl00$pageContent$enrollcodeTextBox'
        DEPARTMENT_FIELD = 'ctl00$pageContent$departmentDropDown'
        COURSE_NUM_FIELD = 'ctl00$pageContent$courseNumberTextBox'
        print("> Starting search...")
        # Hack to work around lack of javascript in mechanize #
        self.br.open(SEARCH_URL)
        # Select search form
        self.br.select_form(nr=0)
        form = self.br.form
        # Set search params
        form[QUARTER_FIELD] = [self.quarter]
        self.br.submit().read()
        # #
        for s in search_params:
            try:
                self.br.open(SEARCH_URL)
                # Select search form
                self.br.select_form(nr=0)
                form = self.br.form
                # Set search params
                form[QUARTER_FIELD] = [self.quarter]
                form[ENROLL_CODE_FIELD] = s['enroll_code']
                form[DEPARTMENT_FIELD] = [s['department']]
                form[COURSE_NUM_FIELD] = s['course_num']
                # print(form)
                # Execute search and save result page for parsing
                soup = BeautifulSoup(self.br.submit().read())
                # Parse results
                error_page_attrs = {"id": "pageContent_messageLabel"}
                error_page = soup.findAll("span", attrs=error_page_attrs)
                if error_page:
                    print("Class not found. Will try again next time.")
                    continue
                class_title_attrs = {"class": "tableheader"}
                class_title = soup.findAll("span", attrs=class_title_attrs)
                info_header_attrs = {"class": "tableheader"}
                info_header = soup.findAll("td", attrs=info_header_attrs)[0:7]
                info_table_attrs = {"class": "clcellprimary"}
                info_table = soup.findAll("td", attrs=info_table_attrs)[0:7]

                info_dict = {}
                for title, detail in zip(info_header, info_table):
                    info_dict[title.string] = detail.string

                # Print class title
                title = class_title[0].string.replace(u'\xa0', u' ')
                title = ' '.join(title.split())
                print("\n%s" % title)
                # Trick to underline a string with the correct # of =
                print("%s" % ''.join(["=" for i in range(len(title))]))

                # Check if full
                if info_dict["Space"] == u"Full\xa0":
                    print("Class is full.")
                    continue
                elif info_dict["Space"] == u"Closed\xa0":
                    print("Class is closed.")
                    continue
                elif (info_dict['Day(s)'] == u'T.B.A.\xa0'):
                    if (info_dict['Instructor(s)'] == u'T.B.A.\xa0'):
                        if (info_dict['Time(s)'] == u'T.B.A.\xa0'):
                            print("This class is not available yet.")
                            continue
                elif (float(info_dict["Space"]) / float(info_dict["Max"])) > 0:
                    if self.notify_email:
                        print("Class is OPEN! Sending notification...")
                        self.notify(title)
                    else:
                        print("Class is OPEN!")
                    continue
                else:
                    print("Unknown reason why class is full.")
            except (mechanize._form.ControlNotFoundError,
                    mechanize._form.ItemNotFoundError):
                print("Unknown error. Skipping for now...\n")

    def notify(self, class_title):
        # Send email from your UCSB Umail to some other email that you specify
        fromaddr = self.user + "@umail.ucsb.edu"
        toaddrs = self.notify_email
        msg = "\n[CLASS OPEN!]\n%s" % class_title
        # Use credentials that were previously entered
        username = fromaddr
        password = self.pw
        # UCSB Umail's SMTP server and port
        server = smtplib.SMTP('pod51019.outlook.com:587')
        server.starttls()
        server.login(username, password)
        server.sendmail(fromaddr, toaddrs, msg)
        server.quit()
        return self

    def wait(self):
        raw_time_delta = time.localtime(time.time() + self.mins_to_wait*60)
        check_time = time.asctime(raw_time_delta)
        print("\n> Checking again at:\n> %s\n" % check_time)
        time.sleep(self.mins_to_wait*60.0)


def main():
    Gold()


if __name__ == "__main__":
    main()
