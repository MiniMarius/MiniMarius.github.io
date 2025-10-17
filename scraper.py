
import os
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
    address: str = ""
    website: str = ""

restaurants = [
    Restaurant(name="Al Caminetto", menu_url="https://www.alcaminetto.se/index.php/lunch"),
    Restaurant(name="Bastard Burgers", menu_url="https://bastardburgers.com/se/dagens-lunch/bromma/"),
    Restaurant(name="Bistro Garros", menu_url="https://bistrogarros.se/menyer/meny"),
    #Restaurant(name="Brioche", menu_url="https://brioche.se/lunchmeny"),
    Restaurant(name="Gustafs Matsal", menu_url="https://gustafs.kvartersmenyn.se/"),
    Restaurant(name="Melanders", menu_url="https://melanders.se/restauranger/melanders-alvik/"),
    Restaurant(name="Poké Burger", menu_url="https://pokeburger.se/meny/alvik/"),
    Restaurant(name="Sjöpaviljongen", menu_url="https://sjopaviljongen.se/lunchmeny/"),
    #Restaurant(name="Vedugnen", menu_url="https://www.vedugnenialvik.se/meny"),
]

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

        # Use OpenAI client to process HTML and extract today's menu
        prompt = f"Extract all dishes for {today_swedish} from the following HTML content in Swedish. If {today_swedish} cannot be found, extract all dishes you can find:\n\n{html_content}"
        print(f"Sending prompt to OpenAI for {restaurant.name}")
        response = client.responses.parse(
            model="gpt-4o-mini",
            input=[{"role": "user", "content": prompt}],
            text_format=MenuSection
        )
        
        if response and response.output_parsed:
            restaurant.menu = [response.output_parsed]
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

        # Find both PDF links
        pdf_link_tag_1 = melandersSoup.find('a', text="DAGENS LUNCH")
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
        print(all_combined_text)

        prompt = f"Extract today's dishes for {today_swedish} and all sushi menus and pokebowls from the following combined text in Swedish:\n\n{all_combined_text}"
        print(f"Sending prompt to OpenAI for Melanders")
        response = client.responses.parse(
            model="gpt-4o-mini",
            input=[{"role": "user", "content": prompt}],
            text_format=MenuSection
        )

        if response and response.output_parsed:
            restaurant.menu = [response.output_parsed]
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
