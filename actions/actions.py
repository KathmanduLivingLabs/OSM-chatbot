# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import SlotSet, EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from bs4 import BeautifulSoup
import lxml
import requests
from actions.api.rasaxapi import RasaXAPI

class ResetUsernameSlot(Action):
    def name(self):
        return "action_reset_username_slot"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        return [SlotSet("username", None)]

class ValidateUserNameForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_username_form"
    
    def validate_username(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `username` value."""
        print(f"Username given = {slot_value}")
        username=slot_value
        user_name=slot_value.replace(' ', '%20')
        url = "https://www.openstreetmap.org/user/{user_name}".format(user_name=user_name)

        if requests.get(url).status_code !=200:
            dispatcher.utter_message(text="Sorry, there is no user with the username {user_name}. Please check your spelling and capitallization as username is case-sensative.". format(user_name=username))
            return {"username": None}
        else:
            return {"username": slot_value}

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
        # if user_page.status_code !=200:
        #     dispatcher.utter_message(text="Sorry, there is no user with the username {user_name}. Please check your spelling and capitallization as username is case-sensative.". format(user_name=username))
        # else:
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
        
class TagInformation(Action):
    def name(self):
        return "action_tag_info"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[EventType]:
        asked_tag = tracker.get_slot('tag')
        processed_tag = asked_tag.replace(' ', '+')
        url = "https://tagfinder.herokuapp.com/search?query={user_query}&lang=en".format(user_query=processed_tag)
        tags_page = requests.get(url).text
        tags_soup = BeautifulSoup(tags_page, 'lxml')
        found = tags_soup.find('h5', class_='found').find('b').text
        top_tag = tags_soup.find_all('div', class_='search_result')
        key = top_tag.find('a', id='keyPartLabel_1').text
        label = top_tag.find('a', id='tagLabel_1').text
        image = top_tag.find('a', id='depiction').get('href')
        description = top_tag.find('p', id='descriptionEN_1').text
        wiki_link = top_tag.find('a', id='tagLabel_1').get('href')
        dispatcher.utter_message(text="Found {found} OpenStreetMap tag(s) that matched your query. The to match was: \n \
{key}{label} \n \
Description: {description} \n \
For more info about this tag visit this <a href={wiki_link}>Wiki Page</a> \n \
For other tags related to {user_query} visit: \n\
{url}".format(
        found=found, key=key, label=label, description=description, wiki_link=wiki_link, url=url
        ), image=image)
        return []

class ValidateTagForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_tag_form"
    
    def validate_tag(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `tag` value."""
        # print(f"Username given = {slot_value}")
        tag=slot_value
        processed_tag=slot_value.replace(' ', '%20')
        url = "https://tagfinder.herokuapp.com/search?query={user_query}&lang=en".format(user_query=processed_tag)
        tags_page = requests.get(url).text
        tags_soup = BeautifulSoup(tags_page, 'lxml')
        try:
            found = tags_soup.find('h5', class_='found').find('b').text
        except:
            found = 0
        if found == 0:
            dispatcher.utter_message(text="Sorry, there is no user with the username {tag_name}. Please check your spelling and capitallization as username is case-sensative.". format(tag_name=tag))
            return {"tag": None}
        else:
            return {"tag": slot_value}

class ResetTagSlot(Action):
    def name(self):
        return "action_reset_tag_slot"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        return [SlotSet("tag", None)]