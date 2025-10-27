"""
Aula API Client
Handles login and API requests to Aula.dk
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json


class AulaClient:
    """Client for interacting with Aula API"""

    def __init__(self):
        self.session = requests.Session()
        self.logged_in = False
        self.institutions = []
        self.institution_profiles = []
        self.children = []
        self.profile_data = None

    def login(self, username, password):
        """
        Login to Aula with username and password
        Returns True if successful, False otherwise
        """
        # Start login process
        url = 'https://www.aula.dk/auth/login.php?type=unilogin'
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        post_url = soup.form['action']
        params = {
            'selectedIdp': 'uni_idp'
        }

        # Get login form
        response = self.session.post(post_url, data=params)

        # Login loop
        counter = 0
        success = False

        while success == False and counter < 10:
            try:
                soup = BeautifulSoup(response.text, "lxml")
                url = soup.form['action']

                if url:
                    inputs = soup.find_all('input')

                    if inputs:
                        data = {}
                        for input_field in inputs:
                            try:
                                if input_field['name'] == 'username':
                                    data[input_field['name']] = username
                                elif input_field['name'] == 'password':
                                    data[input_field['name']] = password
                                elif input_field['name'] == 'selected-aktoer':
                                    data[input_field['name']] = "KONTAKT"
                                else:
                                    data[input_field['name']] = input_field['value']
                            except:
                                pass

                    if data:
                        response = self.session.post(url, data=data)
                    else:
                        response = self.session.post(url)

                    if response.url == 'https://www.aula.dk:443/portal/':
                        success = True
            except Exception as e:
                print(f"Login error: {e}")
                pass

            counter += 1

        if success and response.status_code == 200:
            self.logged_in = True
            # Initialize profile
            self._init_profile()
            return True

        return False

    def _init_profile(self):
        """Initialize profile and get necessary data"""
        url = 'https://www.aula.dk/api/v18/'

        # First API request
        params = {
            'method': 'profiles.getProfilesByLogin'
        }
        response_profile = self.session.get(url, params=params).json()
        self.profile_data = response_profile

        # Second API request
        params = {
            'method': 'profiles.getProfileContext',
            'portalrole': 'guardian',
        }
        response_profile_context = self.session.get(url, params=params).json()

        # Collect institutions and children
        for institution in response_profile_context['data']['institutions']:
            self.institutions.append(institution['institutionCode'])
            self.institution_profiles.append(institution['institutionProfileId'])
            for child in institution['children']:
                self.children.append(child['id'])

        # Third request - notifications
        params = {
            'method': 'notifications.getNotificationsForActiveProfile',
            'activeChildrenIds[]': self.children,
            'activeInstitutionCodes[]': self.institutions
        }
        self.session.get(url, params=params).json()

    def get_weekly_notes(self, week_offset=0):
        """
        Get weekly notes (calendar events) for a specific week
        week_offset: 0 = current week, 1 = next week, -1 = previous week
        """
        if not self.logged_in:
            return None

        # Calculate date range for the week
        today = datetime.now()
        # Get start of week (Monday)
        start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
        # Get end of week (Sunday)
        end_of_week = start_of_week + timedelta(days=6)

        url = 'https://www.aula.dk/api/v18/'

        # Get calendar events for all children and institution profiles
        children_and_institution_profiles = self.institution_profiles + self.children

        params = {
            'method': 'calendar.getEventsByProfileIds',
            'profileIds[]': children_and_institution_profiles,
            'startDate': start_of_week.strftime('%Y-%m-%d'),
            'endDate': end_of_week.strftime('%Y-%m-%d')
        }

        try:
            response = self.session.get(url, params=params).json()
            return {
                'week_number': start_of_week.isocalendar()[1],
                'year': start_of_week.year,
                'start_date': start_of_week.strftime('%Y-%m-%d'),
                'end_date': end_of_week.strftime('%Y-%m-%d'),
                'events': response.get('data', {}).get('events', [])
            }
        except Exception as e:
            print(f"Error getting weekly notes: {e}")
            return None

    def get_children_info(self):
        """Get information about children"""
        if not self.profile_data:
            return []

        children_info = []
        try:
            for profile in self.profile_data['data']['profiles']:
                if 'institutionProfiles' in profile:
                    for inst_profile in profile['institutionProfiles']:
                        if 'children' in inst_profile:
                            for child in inst_profile['children']:
                                children_info.append({
                                    'name': child.get('name', 'Unknown'),
                                    'id': child.get('id', ''),
                                    'institution': inst_profile.get('institutionName', '')
                                })
        except Exception as e:
            print(f"Error getting children info: {e}")

        return children_info
