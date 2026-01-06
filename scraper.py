
import os
import random
import requests
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import pdfquery
import json
from pydantic import BaseModel

load_dotenv()
client = OpenAI()

class Dish(BaseModel):
    name: str
    description: str = "" 
    price: float
    allergens: list[str] = []  

class MenuSection(BaseModel):
    title: str
    dishes: list[Dish]

class Restaurant(BaseModel):
    name: str
    menu_url: str
    menu: list[MenuSection] = []

restaurants = [
    Restaurant(name="Al Caminetto", menu_url="https://www.alcaminetto.se/index.php/lunch"),
    Restaurant(name="Bastard Burgers", menu_url="https://bastardburgers.com/se/dagens-lunch/bromma/"),
    Restaurant(name="Bistro Garros", menu_url="https://bistrogarros.se/menyer/meny"),
    Restaurant(name="Brioche", menu_url="https://brioche.se/lunchmeny"),
    #Restaurant(name="Gustafs Matsal", menu_url="https://gustafs.kvartersmenyn.se/"),
    Restaurant(name="Melanders", menu_url="https://melanders.se/restauranger/melanders-alvik/"),
    Restaurant(name="Poké Burger", menu_url="https://pokeburger.se/meny/alvik/"),
    Restaurant(name="Sjöpaviljongen", menu_url="https://sjopaviljongen.se/lunchmeny/"),
    Restaurant(name="Vedugnen", menu_url="https://www.vedugnenialvik.se/meny"),
    Restaurant(name="Caffé Nero", menu_url="https://www.caffenero.com/se/menu/mat/lunch"),
    Restaurant(name="Joe & the Juice", menu_url="https://www.joejuice.com/store/76d02a98-93a7-4610-acf6-2bfbf6c9d51b"),
    Restaurant(name="Meegi Art Sushi", menu_url="https://qopla.com/restaurant/meegi-art-sushi/qbgOZmj7gv/home")
]

prompt_templates = {
    "Bastard Burgers": "Extract the burger options for {day} from the HTML content in Swedish. There can only be one burger per day. Also, turn off ALL CAPS from dishes",
    "Bistro Garros": "Extract all dishes for {day} from the following HTML content in Swedish. If you cannot find a price, set it to 150 for main dishes and Veg/vegatariska but not for side dishes or pannkaksbuffé which are free. Also, turn off ALL CAPS from dishes:",
    "Poké Burger": "Extract all lunch dishes from the following menu sections in Swedish: Veckans no bowl 11:00-14:00, Lunch Bowls 11:00-14:00 and THE BURGERS 11:00-14:00. Also, turn off ALL CAPS from dishes",
    "Joe & the Juice": "Identify and extract info of dishes suitable for lunch. Focus on extracting menu items that are typically consumed during lunchtime, such as sandwiches, salads, and wraps. Get the info in swedish except the titles.",
    "Meegi Art Sushi": "Identify and extract the sushi dishes only. Get the information in Swedish",
    "Vedugnen": "Extract all pizza and pasta dishes only. Get the information and price for each dish in Swedish"
}

today_index = datetime.now().weekday()
swedish_days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]
today_swedish = swedish_days[today_index]
print(f"Today's day in Swedish is: {today_swedish}")

def fetch_and_process_menu(restaurant: Restaurant):
    print(f"Fetching menu for {restaurant.name} from URL: {restaurant.menu_url}")
    try:
        response = requests.get(restaurant.menu_url)
        response.raise_for_status()
        html_content = response.text
        print(f"HTML content fetched for {restaurant.name}")

        custom_prompt = prompt_templates.get(restaurant.name)
        
        if custom_prompt:
            prompt = custom_prompt.format(day=today_swedish) + "\n\n" + html_content
        else:
            prompt = f"Extract all dishes for {today_swedish} from the following HTML content in Swedish. Also, turn off ALL CAPS from dishes:\n\n{html_content}"

        print(f"Sending prompt to OpenAI for {restaurant.name}")
        
        response = client.responses.parse(
            model="gpt-4o-mini",
            input=[{"role": "user", "content": prompt}],
            text_format=Restaurant
        )
        
        if response and response.output_parsed:
            restaurant.menu = response.output_parsed.menu
            print(f"Successfully updated menu for {restaurant.name}")
        else:
            print(f"No menu data extracted for {restaurant.name}")
        
    except Exception as e:
        print(f"Error fetching menu for {restaurant.name}: {e}")

def fetch_melanders_menu(restaurant):
    print(f"Fetching Melanders menu from URL: {restaurant.menu_url}")
    try:
        melandersHtml = requests.get(restaurant.menu_url)
        melandersHtml.raise_for_status()
        melandersSoup = BeautifulSoup(melandersHtml.content, 'html.parser')
        print("Fetched HTML for Melanders")

        # Get the current week number
        current_week_number = datetime.now().isocalendar()[1]

        # Construct the dynamic text string
        dynamic_text = f"DAGENS LUNCH v.{current_week_number}"

        # Find both PDF links
        pdf_link_tag_1 = melandersSoup.find('a', text=dynamic_text)
        pdf_link_tag_2 = melandersSoup.find('a', text="SUSHI MENY")

        pdf_urls = []
        if pdf_link_tag_1:
            pdf_urls.append(pdf_link_tag_1['href'])
        if pdf_link_tag_2:
            pdf_urls.append(pdf_link_tag_2['href'])

        all_combined_text = ""

        for index, pdf_url in enumerate(pdf_urls):
            if pdf_url:
                pdf_path = f"menu_{index}.pdf"
                urllib.request.urlretrieve(pdf_url, pdf_path)
                print(f"Downloaded PDF to {pdf_path}")
                pdf = pdfquery.PDFQuery(pdf_path)
                pdf.load()
                all_text = ""
                for page_number in range(len(pdf.pq('LTPage'))):
                    pdf.load(page_number)
                    page_text = pdf.pq('LTTextLineHorizontal').text()
                    all_text += page_text
                
                all_combined_text += all_text

        prompt = f"Extract today's dishes for {today_swedish} and all sushi menus and pokebowls from the following combined text in Swedish. Also, turn off ALL CAPS from dishes, also the default price is 149 if you can't find a specific price for a dish:\n\n{all_combined_text}"
        print(f"Sending prompt to OpenAI for Melanders")
        response = client.responses.parse(
            model="gpt-4o-mini",
            input=[{"role": "user", "content": prompt}],
            text_format=Restaurant
        )

        if response and response.output_parsed:
            restaurant.menu = response.output_parsed.menu
            print(f"Successfully updated menu for Melanders")
        else:
            print(f"No menu data extracted for Melanders")

    except Exception as e:
        print(f"Error fetching Melanders menu: {e}")

for restaurant in restaurants:
    if restaurant.name == "Melanders":
        fetch_melanders_menu(restaurant)
    else:
        fetch_and_process_menu(restaurant)

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
output_data = {
    "last_updated": timestamp,
    "restaurants": [restaurant.model_dump() for restaurant in restaurants]
}

output_path = os.path.join("public", "menus.json")
# Save the menus to a JSON file
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print(f"Menus saved to {output_path}")


webhook_url_platform = "https://default0d11ac4aef5e423a803be51aacfa43.d6.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/29dce9f536164244912a5df00ea8152c/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=owB9RZDiqi4JvuAdjgHaXpLMmzUb0QSFNI2uURRpqAQ"
webhook_url_wizards = "https://default0d11ac4aef5e423a803be51aacfa43.d6.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/69f57892411340f19dd61a0b11c40ebd/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=cUjiqy1UI5UTqfwIt5pi9OQskq4EpVu6H9od39lrSsI"

def send_adaptive_card_to_teams(webhook_url, adaptive_card_json):
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(webhook_url, headers=headers, data=json.dumps(adaptive_card_json))
    if response.status_code == 200 or response.status_code == 202:
        print("Adaptive card sent successfully")
    else:
        print(f"Failed to send adaptive card: {response.status_code} - {response.text}")

def create_adaptive_card(restaurant_highlight):
    adaptive_card_json = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "body": [
                        {
                            "type": "TextBlock",
                            "size": "Medium",
                            "weight": "Bolder",
                            "text": "Alvikslunchens Lunch-Highlight!"
                        },
                        {
                            "type": "Image",
                            "url": restaurant_highlight.get('image_url', 'https://cdn-icons-png.flaticon.com/512/5787/5787016.png'),
                            "size": "Medium"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Idag rekommenderar vi {restaurant_highlight['name']}!",
                            "wrap": "true"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Rätten heter {restaurant_highlight['dish']}",
                            "wrap": "true"
                        },
                        {
                            "type": "ActionSet",
                            "actions": [
                                {
                                    "type": "Action.OpenUrl",
                                    "title": "Se hela lunchguiden",
                                    "url": "https://alvikslunchen.se"
                                }
                            ]
                        }
                    ],
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "version": "1.3"
                }
            }
        ]
    }
    return adaptive_card_json


# Välj en slumpmässig restaurang
random_restaurant = random.choice(restaurants)
restaurant_highlight = {
    "name": random_restaurant.name,
    "dish": random.choice(random_restaurant.menu[0].dishes).name if random_restaurant.menu else "Ingen rätt tillgänglig",
    "price": random.choice(random_restaurant.menu[0].dishes).price if random_restaurant.menu else "Pris ej tillgängligt"
}

adaptive_card_json = create_adaptive_card(restaurant_highlight)

current_time = datetime.now().time()
#if current_time < datetime.strptime("09:00", "%H:%M").time():
#    send_adaptive_card_to_teams(webhook_url_platform, adaptive_card_json)
#    send_adaptive_card_to_teams(webhook_url_wizards, adaptive_card_json)
#else:
#    print("It is past 9 AM. The adaptive card will not be sent.")
#