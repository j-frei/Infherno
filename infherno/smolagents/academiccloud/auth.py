#!/usr/bin/env python3
import sys
import os
from requests import Session
from bs4 import BeautifulSoup

# Windows 10 Chrome User-Agent
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
DEFAULT_ENDPOINT = 'https://chat-ai.academiccloud.de/models'

class AcademicFederatedCredentialsFlow:
    def __init__(self):
        self.steps = {}

    def authenticate(self, supported_logins: dict, session: Session, get_url: str, get_data: dict, login_provider_field: str):
        raise NotImplementedError("This method should be overridden by subclasses.")


class AcademicUniAugsburgCredentialsFlow(AcademicFederatedCredentialsFlow):
    def __init__(self, username: str, password: str):
        super().__init__()
        self.login_provider = "University of Augsburg"
        self.username = username
        self.password = password

    def authenticate(self, supported_logins: dict, session: Session, get_url: str, get_data: dict, login_provider_field: str):
        # Step 0: Proceed to the Uni Augsburg login page and extract the POST form data
        if self.steps.get("uaux_step0") is None:
            uaux_step0 = {}

            # Check if the login provider is supported
            if self.login_provider not in supported_logins:
                raise ValueError(f"Login provider '{self.login_provider}' is not supported. Supported logins: {supported_logins}")

            # Select the login provider for Uni Augsburg
            uaux_get_data = get_data.copy()
            uaux_get_data[login_provider_field] = supported_logins[self.login_provider]

            uaux_resp0 = session.get(get_url, params=uaux_get_data)
            uaux_soup0 = BeautifulSoup(uaux_resp0.text, 'html.parser')

            # Set default login items
            login_data_items = {
                "username": self.username,
                "password": self.password,
            }

            # Parse the Uni Augsburg login form (with added credentials)
            uaux_form0 = uaux_soup0.find('form', {'id':'f'})
            uaux_post_url0 = uaux_form0.get('action')
            uaux_post_data0 = {}
            for input_tag in uaux_form0.find_all('input'):
                if input_tag.get('name'):
                    uaux_post_data0[input_tag.get('name')] = login_data_items.get(
                        input_tag.get('name'),
                        input_tag.get('value', '')
                    )

            uaux_step0["resp"] = uaux_resp0
            uaux_step0["soup"] = uaux_soup0
            uaux_step0["form"] = uaux_form0
            uaux_step0["post_url"] = uaux_post_url0
            uaux_step0["post_data"] = uaux_post_data0
            self.steps["uaux_step0"] = uaux_step0

        # Step 1: Submit the login credentials
        if self.steps.get("uaux_step1") is None:
            uaux_step1 = {}

            # Submit the form
            uaux_resp1 = session.post(self.steps["uaux_step0"]["post_url"], data=self.steps["uaux_step0"]["post_data"])
            uaux_soup1 = BeautifulSoup(uaux_resp1.text, 'html.parser')

            # Confirm that you want to proceed with the login
            uaux_form1 = uaux_soup1.find('form')
            uaux_post_url1 = uaux_form1.get('action')
            uaux_post_data1 = {}
            for input_tag in uaux_form1.find_all('input'):
                if input_tag.get('name'):
                    uaux_post_data1[input_tag.get('name')] = input_tag.get('value', '')

            # Save the data
            uaux_step1["resp"] = uaux_resp1
            uaux_step1["soup"] = uaux_soup1
            uaux_step1["form"] = uaux_form1
            uaux_step1["post_url"] = uaux_post_url1
            uaux_step1["post_data"] = uaux_post_data1
            self.steps["uaux_step1"] = uaux_step1

        # Step 2: Submit the confirmation form
        if self.steps.get("uaux_step2") is None:
            uaux_step2 = {}

            # Submit the confirmation form
            uaux_resp2 = session.post(self.steps["uaux_step1"]["post_url"], data=self.steps["uaux_step1"]["post_data"])
            uaux_soup2 = BeautifulSoup(uaux_resp2.text, 'html.parser')

            # Extract form data to re-confirm on the /sso endpoint
            uaux_form2 = uaux_soup2.find('form')
            uaux_post_url2 = uaux_form2.get('action')
            uaux_post_data2 = {}
            for input_tag in uaux_form2.find_all('input'):
                if input_tag.get('name'):
                    uaux_post_data2[input_tag.get('name')] = input_tag.get('value', '')

            # Save the data
            uaux_step2["resp"] = uaux_resp2
            uaux_step2["soup"] = uaux_soup2
            uaux_step2["form"] = uaux_form2
            uaux_step2["post_url"] = uaux_post_url2
            uaux_step2["post_data"] = uaux_post_data2
            self.steps["uaux_step2"] = uaux_step2

        # Step 3: Final post to the /sso endpoint -> should redirect to the initial endpoint page (now authenticated)
        if self.steps.get("uaux_step3") is None:
            uaux_step3 = {}

            # Submit the confirmation form
            uaux_resp3 = session.post(self.steps["uaux_step2"]["post_url"], data=self.steps["uaux_step2"]["post_data"])

            # Save the data
            uaux_step3["resp"] = uaux_resp3
            self.steps["uaux_step3"] = uaux_step3

class AcademicAuth:
    def __init__(self, endpoint: str = DEFAULT_ENDPOINT, user_agent: str = DEFAULT_USER_AGENT, store_cookie: bool = True):
        self.endpoint = endpoint
        self.session = Session()
        self.session.headers.update({'User-Agent': user_agent})
        self.steps = {}
        # Cookie value for cookie 'mod_auth_openidc_session'
        self.auth_cookie = None
        self.store_cookie = store_cookie

        if self.store_cookie:
            if os.path.exists(os.path.join(os.path.dirname(__file__), ".auth_cookie")):
                with open(os.path.join(os.path.dirname(__file__), ".auth_cookie"), "r") as f:
                    self.auth_cookie = f.read().strip()

    def authenticate(self, credentials: AcademicFederatedCredentialsFlow) -> str:
        # Don't authenticate if the auth cookie is already set and valid
        if self.auth_cookie is not None:
            print("Auth cookie already provided. Checking if it's still valid...", file=sys.stderr)
            # Check if the cookie is still valid
            self.session.cookies.set("mod_auth_openidc_session", self.auth_cookie)
            check_resp = self.session.get(self.endpoint)
            if check_resp.url == self.endpoint:
                print("Auth cookie appears to be valid. No authentication required.", file=sys.stderr)
                return self.auth_cookie
            else:
                # Auth cookie is invalid, proceed with authentication
                print("Auth cookie is invalid. Proceeding with authentication...", file=sys.stderr)
                self.session.cookies.clear()
                self.auth_cookie = None
            return self.auth_cookie

        # Step 0: Initial GET request to the endpoint;
        # -> extract the redirect form to the first authentication page
        if self.steps.get("step0") is None:
            step0 = {}
            # Initial GET request to the endpoint
            resp0 = self.session.get(self.endpoint)

            # Check if the response is a redirect
            if resp0.url == self.endpoint:
                # No auth required,
                raise ValueError("No authentication required. The endpoint is already accessible.")

             # Post to get 1st login
            soup0 = BeautifulSoup(resp0.text, 'html.parser')
            form0 = soup0.find('form', {'name':'saml-post-binding'})
            post_url0 = form0.get('action')
            post_data0 = {}
            for input_tag in form0.find_all('input'):
                if input_tag.get('name'):
                    post_data0[input_tag.get('name')] = input_tag.get('value')

            # Save the data
            step0["resp"] = resp0
            step0["soup"] = soup0
            step0["form"] = form0
            step0["post_url"] = post_url0
            step0["post_data"] = post_data0
            self.steps["step0"] = step0

        # Step 1: Post to the first login page and get the login options
        if self.steps.get("step1") is None:
            step1 = {}
            # We now get the login page of AcademiaCloud
            resp1 = self.session.post(self.steps["step0"]["post_url"], data=self.steps["step0"]["post_data"])
            soup1 = BeautifulSoup(resp1.text, 'html.parser')

            # There are three options:
            # [Unsupported] - Direct login via Academic ID (soup1.get("form", {"class": "fieldset"}))
            # [Supported] - Generic Federated login (soup1.get("form", {"id": "delegate_federated"}))
            # [Unsupported] - Max Plank SSO (soup1.get("form", {"id": "delegate_mpg"}))

            # Only Generic Federated login is supported
            federated_form1 = soup1.find('form', {'id':'delegate_federated'})
            federated_post_url1 = federated_form1.get('action')
            federated_post_data1 = {}
            for input_tag in federated_form1.find_all('input'):
                if input_tag.get('name'):
                    federated_post_data1[input_tag.get('name')] = input_tag.get('value', '')

            # Save the data
            step1["resp"] = resp1
            step1["soup"] = soup1
            step1["federated_form"] = federated_form1
            step1["federated_post_url"] = federated_post_url1
            step1["federated_post_data"] = federated_post_data1
            self.steps["step1"] = step1

        # Step 2: Post to the federated login page and get the login options
        if self.steps.get("step2") is None:
            step2 = {}

            # Add referer to headers
            self.session.headers.update({'Referer': self.steps["step1"]["resp"].url})

            # We now get the login page of the Generic Federated login
            resp2 = self.session.post(self.steps["step1"]["federated_post_url"], data=self.steps["step1"]["federated_post_data"])
            soup2 = BeautifulSoup(resp2.text, 'html.parser')

            # Get the form for the Generic Federated login
            form2 = soup2.find('form', {'class':'form-group'})
            get_url2 = form2.get('action')
            get_data2 = {}
            for input_tag in form2.find_all('input'):
                if input_tag.get('name'):
                    get_data2[input_tag.get('name')] = input_tag.get('value', '')

            # Find the supported federated login options
            supported_logins_options = form2.find("select", {"id": "dropdownlist"}).find_all("option")
            supported_logins = {
                option.text.strip() : option.get("value") for option in supported_logins_options
            }
            login_provider_fieldname = form2.find("select", {"id": "dropdownlist"}).get("name")

            step2["resp"] = resp2
            step2["soup"] = soup2
            step2["form"] = form2
            step2["get_url"] = get_url2
            step2["get_data"] = get_data2
            step2["supported_logins"] = supported_logins
            step2["login_provider_fieldname"] = login_provider_fieldname
            self.steps["step2"] = step2

        if self.steps.get("step3") is None:
            step3 = {}

            # If the login provider is not given, raise an error
            if credentials is None:
                raise ValueError("Login provider is not set. Please provide a valid login provider. Supported logins:\n" + ("\n".join(self.steps["step2"]["supported_logins"])))

            credentials.authenticate(
                supported_logins=self.steps["step2"]["supported_logins"],
                session=self.session,
                get_url=self.steps["step2"]["get_url"],
                get_data=self.steps["step2"]["get_data"],
                login_provider_field=self.steps["step2"]["login_provider_fieldname"]
            )

            step3["credentials"] = credentials
            self.steps["step3"] = step3

        # Check if the authentication was successful
        auth_cookie = self.session.cookies.get("mod_auth_openidc_session")
        if auth_cookie is None:
            raise ValueError("Authentication failed. The auth cookie could not be found.")
        self.auth_cookie = auth_cookie

        if self.store_cookie:
            # Save the auth cookie to a file
            print("Saving auth cookie to file...", file=sys.stderr)
            with open(os.path.join(os.path.dirname(__file__), ".auth_cookie"), "w") as f:
                f.write(self.auth_cookie)
        return self.auth_cookie

if __name__ == "__main__":
    import getpass

    # Example usage for Uni Augsburg-based AcademicCloud login
    auth = AcademicAuth()

    # Ask for username and password (safely)
    username = input("Enter your Uni Augsburg username (RZ): ")
    password = getpass.getpass(prompt="Enter your Uni Augsburg password (RZ): ")

    # Create a credentials flow for Uni Augsburg
    credentials = AcademicUniAugsburgCredentialsFlow(username=username, password=password)

    # Ask whether to proceed with the login
    proceed = input(f"Proceed with login for {credentials.login_provider}? (y/n): ")
    if proceed.lower() != 'y':
        print("Login cancelled.")
        sys.exit()

    # Authenticate
    auth_cookie = auth.authenticate(credentials)
    print("Authenticated successfully. Auth cookie:", auth_cookie)