# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from bs4 import BeautifulSoup
import lxml
import requests
from actions.api.rasaxapi import RasaXAPI

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
        user_name = username.replace(' ', '%20')
        url = "https://www.openstreetmap.org/user/{user_name}".format(user_name=user_name)
        user_page = requests.get(url)
        if user_page.status_code !=200:
            dispatcher.utter_message(text="Sorry, there is no user with the username {user_name}. Please check your spelling and capitallization.". format(user_name=username))
        else:
            user_page = user_page.text  
            user_soup = BeautifulSoup(user_page, 'lxml')
            user_image= user_soup.find("img", class_= "user_image_no_margins")
            user_image = user_image.get("src")
            if "/assets" in user_image:
            	user_image = 'https://github.com/Aadesh-Baral/OSM-chatbot/blob/main/images/blanck_profile_pic.png'
            raw_data = requests.get('https://osm-stats-production-api.azurewebsites.net/users/{user_name}'.format(user_name=user_name)).json()
            building_edits = raw_data['total_building_count_add'] + raw_data['total_building_count_mod']
            changesets = raw_data['changesets']
            point_of_interest = raw_data['total_poi_count_add']
            roads = str(round(raw_data['total_road_km_add'], 1)) + ' km'
            waterways = str(round(raw_data['total_waterway_km_add'], 1))+ ' km'
            total_edits = raw_data['total_building_count_add'] + raw_data['total_building_count_mod'] + raw_data['total_waterway_count_add'] + raw_data['total_poi_count_add'] + raw_data['total_road_count_add'] + raw_data['total_road_count_mod']
            country_count = raw_data['country_count']
            mapping_since=user_soup.find("dl", class_="dl-inline").find('dd').text
            dispatcher.utter_message(text="{name} \n Mapping_since: {mapping_since} \n \
‣ Total Edits: {total_edits} \n \
‣ Country Count: {country_count} \n \
‣ Changesets: {changesets} \n \
‣ Buildings Edits: {building_edits} \n \
‣ Roads: {roads} \n \
‣ Waterways: {waterways} \n \
‣ Points Of Interest: {point_of_interest} \n \
For more information about {user} visit https://www.missingmaps.org/users/#/{user_name}".format(
    name=username, mapping_since=mapping_since, 
    total_edits=total_edits, country_count=country_count, changesets=changesets,
    building_edits=building_edits, roads=roads, waterways=waterways,
    point_of_interest=point_of_interest, user=username, user_name=user_name), 
    image=user_image)
        return []


class ActionTagFeedback(Action):
    """Tag a conversation in Rasa X as positive or negative feedback """

    def name(self):
        return "action_flag_feedback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[EventType]:

        feedback = tracker.get_slot("feedback_value")

        if feedback == "positive":
            label = '[{"value":"postive feedback","color":"76af3d"}]'
        elif feedback == "negative":
            label = '[{"value":"negative feedback","color":"ff0000"}]'
        else:
            return []

        rasax = RasaXAPI()
        rasax.tag_convo(tracker, label)
        return []


class ActionFlagResponse(Action):
    """Flag a message in conversation if user didn't like the response`"""

    def name(self):
        return "action_flag_response"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[EventType]:

        rasax = RasaXAPI()
        rasax.flag_message(tracker)
        return []
        
