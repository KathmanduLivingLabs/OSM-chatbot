# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from bs4 import BeautifulSoup
import lxml
import requests

class ResetSlot(Action):
    def name(self):
        return "action_reset_username_slot"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        return [SlotSet("username", None)]

class ActionUserStats(Action):
    
    def name(self):
        return "action_user_info"
    
    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        username = tracker.get_slot("username")
        print(username)
        user_name = username.replace(' ', '%20')
        url = "https://www.openstreetmap.org/user/{user_name}".format(user_name=user_name)
        user_page = requests.get(url)
        print(user_page.status_code)
        if user_page.status_code !=200:
            dispatcher.utter_message(text="Sorry, there is no user with the username {user_name}. Please check your spelling and capitallization.". format(user_name=username))
        else:
            user_page = user_page.text    
            user_soup = BeautifulSoup(user_page, 'lxml')
            try:
                user_description = user_soup.find("div", class_="user-description")
                user_description = user_description.find("p").textuser_name
            except:
                user_description = ''
            user_image= user_soup.find("img", class_= "user_image")
            user_image = user_image.get("src")
            user_actions = user_soup.find("ul", class_="secondary-actions")
            edits = user_actions.find_all("li")[0]
            edits = edits.find("span").text
            mapping_since=user_soup.find("p", class_="text-muted").find('small').text
            mapping_since=mapping_since.split(":")[1]
            mapping_since=mapping_since.replace(" ", "")
            mapping_since=mapping_since.replace("\n", "")
            dispatcher.utter_message(text="{name} \n {user_description} \n Mapping_since: {mapping_since} \n Edits: {edits}".format(name=username, 
                                        user_description=user_description, mapping_since=mapping_since, 
                                        edits=edits), image=user_image)
        return []