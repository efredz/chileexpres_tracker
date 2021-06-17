import os
from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup


def get_tracking_page(track_number):
    url = 'https://www.chilexpress.cl/contingencia/Resultado'
    data = {'FindOt': track_number}
    response = requests.post(url, data=data)
    if response.ok:
        return response.content
    raise Exception('qué chucha')


def get_events(body):
    soup = BeautifulSoup(body)
    return soup.find(id='ListaTrackingOT').findAll('tr')


@dataclass
class Event:
    timestamp: str
    message: str


def clean_events(events):
    cleaned_events = [
        Event(timestamp=str(event.contents[0].string + event.contents[1].string), message=str(event.contents[2].string))
        for event in events if event.contents]
    return cleaned_events


def send_to_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage?chat_id={chat_id}&text={message}"
    requests.post(url)


def format_message(events: List[Event]) -> str:
    message = ""
    for event in events:
        message = f"{message}\n{event.timestamp}: {event.message}"
    return message

if __name__ == '__main__':
    tracking_number = os.getenv('TRACKING_NUMBER')
    html = get_tracking_page(tracking_number)
    events = get_events(html)
    cleaned_events = clean_events(events)
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    send_to_telegram(chat_id=chat_id, message=format_message(cleaned_events))
