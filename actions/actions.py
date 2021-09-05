# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from bs4 import BeautifulSoup
import lxml
import requests
#
#
# class ActionHelloWorld(Action):

#     def name(self) -> Text:
#         return "action_hello_world"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         dispatcher.utter_message(text="Hello World!")

#         return []

class ActionUserStats(Action):
    
    def name(self):
        return "action_user_stats"
    
    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = "Manoj Thapa"
        user_page = requests.get("https://www.openstreetmap.org/user/Manoj%20Thapa").text
        user_soup = BeautifulSoup(user_page, 'lxml')
        user_description = user_soup.find("div", class_="user-description")
        user_description = user_description.find("p").text
        user_image= user_soup.find("img", class_= "user_image")
        user_image = user_image.get("src")
        user_actions = user_soup.find("ul", class_="secondary-actions")
        edits = user_actions.find_all("li")[0]
        edits = edits.find("span").text
        mapping_since=user_soup.find("p", class_="text-muted").find('small').text
        mapping_since=mapping_since.split(":")[1]
        mapping_since=mapping_since.replace(" ", "")
        mapping_since=mapping_since.replace("\n", "")
        dispatcher.utter_message(text="{name} \n {user_description} \n Mapping_since: {mapping_Since} \n Edits: {edits}".format(name=name, 
                                    user_description=user_description, mapping_since=mapping_since, 
                                    edits=edits), image=user_image)
        return []