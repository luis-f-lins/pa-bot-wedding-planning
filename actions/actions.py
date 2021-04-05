from rasa_sdk import Action
from rasa_sdk.events import SlotSet, FollowupAction
import json
import requests
import ast

from typing import Dict, Text, Any, List, Union, Optional

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from rasa_sdk.events import AllSlotsReset

processKey = 'wedding_planning'

class StartProcess(Action):
    def name(self):
        return "start_process"

    def run(self, dispatcher, tracker, domain):
        global taskGetUrl
        global processInstanceGetUrl
        global processInstanceId

        url = 'http://localhost:8080/engine-rest/process-definition/key/' + processKey + '/start'
        postPayload = {"variables": {
            "chosenDate": {"value": ''}
        },
        }

        response = requests.post(url, json=postPayload)

        print(response.json())
        processInstanceId = response.json()['id']
        taskGetUrl = 'http://localhost:8080/engine-rest/task?processInstanceId=' + processInstanceId
        processInstanceGetUrl = 'http://localhost:8080/engine-rest/process-instance/' + \
            processInstanceId
        dispatcher.utter_message(text='Okay! Let\'s start the process.')

        return [AllSlotsReset()]


def completeCurrentTask(postPayload = {}):
    global currentTaskId 
    url = 'http://localhost:8080/engine-rest/task/' + currentTaskId + '/complete'
    response = requests.post(url, json=postPayload)
    return


class AskWeddingDate(FormAction):
    def name(self) -> Text:
        return "ask_wedding_date"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["chosenDate"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "chosenDate": [
                self.from_text(intent=None),
            ]
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        postPayload = {"variables": {"chosenDate": {
            "value": tracker.get_slot("chosenDate")}}, "withVariablesInReturn": True}

        completeCurrentTask(postPayload)

        return [FollowupAction("whats_next")]


class ChooseDate(Action):
    def name(self):
        return "choose_date"

    def run(self, dispatcher, tracker, domain):
        taskKey = 'choose_date'

        jsonObj = requests.get(taskGetUrl).json()

        availableTask = None

        for i in jsonObj:
            if i['taskDefinitionKey'] == taskKey:
                availableTask = i

        if availableTask == None:
            dispatcher.utter_message(
                text='I\'m sorry, but this task is not available.')
        else:
            global currentTaskId 
            currentTaskId = availableTask['id']

            return [FollowupAction("ask_wedding_date")]


class BookBand(Action):
    def name(self):
        return "book_band"

    def run(self, dispatcher, tracker, domain):
        taskKey = 'book_band'

        jsonObj = requests.get(taskGetUrl).json()

        availableTask = None

        for i in jsonObj:
            if i['taskDefinitionKey'] == taskKey:
                availableTask = i

        if availableTask == None:
            dispatcher.utter_message(
                text='I\'m sorry, but this task is not available.')
        else:  
            global currentTaskId 
            currentTaskId = availableTask['id']
            completeCurrentTask()

            return []


class BookPhotographer(Action):
    def name(self):
        return "book_photographer"

    def run(self, dispatcher, tracker, domain):
        taskKey = 'book_photographer'

        jsonObj = requests.get(taskGetUrl).json()

        availableTask = None

        for i in jsonObj:
            if i['taskDefinitionKey'] == taskKey:
                availableTask = i

        if availableTask == None:
            dispatcher.utter_message(
                text='I\'m sorry, but this task is not available.')
        else:
            global currentTaskId 
            currentTaskId = availableTask['id']
            completeCurrentTask()

        return []


class BookCaterer(Action):
    def name(self):
        return "book_caterer"

    def run(self, dispatcher, tracker, domain):
        taskKey = 'book_caterer'

        jsonObj = requests.get(taskGetUrl).json()

        availableTask = None

        for i in jsonObj:
            if i['taskDefinitionKey'] == taskKey:
                availableTask = i

        if availableTask == None:
            dispatcher.utter_message(
                text='I\'m sorry, but this task is not available.')
        else:
            global currentTaskId 
            currentTaskId = availableTask['id']
            completeCurrentTask()

        return []

class BookVenue(Action):
    def name(self):
        return "book_venue"

    def run(self, dispatcher, tracker, domain):
        taskKey = 'book_venue'

        jsonObj = requests.get(taskGetUrl).json()

        availableTask = None

        for i in jsonObj:
            if i['taskDefinitionKey'] == taskKey:
                availableTask = i

        if availableTask == None:
            dispatcher.utter_message(
                text='I\'m sorry, but this task is not available.')
        else:
            global currentTaskId 
            currentTaskId = availableTask['id']
            completeCurrentTask()

        return []


class WhatsNext(Action):
    def name(self):
        return "whats_next"

    def run(self, dispatcher, tracker, domain):        
        jsonObj = requests.get(taskGetUrl).json()

        response = requests.get(processInstanceGetUrl)
        processStillExists = response.status_code

        if (processStillExists == 404):
            dispatcher.utter_message(text='Congratulations! You\'re all done!')

        elif len(jsonObj) > 0:
            messageToUtter = 'The available tasks are:'

            for i in jsonObj:
                messageToUtter = messageToUtter + '\n- ' + i['name']

            dispatcher.utter_message(text=messageToUtter)

        return [FollowupAction("action_listen")]
