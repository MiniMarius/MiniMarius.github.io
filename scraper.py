import os
import requests
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
import pdfquery
import json
import re

def clean_menus(menus):
    cleaned_menus = []
    
    # Regular expression pattern to match time ranges
    time_pattern = re.compile(r'\b\d{1,2}[:.]\d{2}\s*-\s*\d{1,2}[:.]\d{2}\b')
    
    # Define a function to clean up each menu item
    def clean_item(item):
        # Remove newline characters and hashtags
        item = item.replace('\n', ' ').replace('#', '')
        # Strip leading and trailing whitespace
        return item.strip()
    
    for restaurant in menus:
        cleaned_dishes = [
            {"name": clean_item(dish["name"]), "price": dish["price"]} 
            for dish in restaurant["menu"]["dishes"]
            if len(dish["name"]) >= 25 and not time_pattern.search(dish["name"])
        ]
        cleaned_menus.append({
            "name": restaurant["name"],
            "location": restaurant["location"],
            "menu": {"dishes": cleaned_dishes}
        })
    
    return cleaned_menus

# Initialize the JSON object
menus = []

# Garros
headers = {'User-Agent': 'Mozilla/5.0'}
try:
    garroshtml = requests.get("https://bistrogarros.se/menyer/meny", headers=headers)
    garroshtml.raise_for_status()
    garrosSoup = BeautifulSoup(garroshtml.content, 'html.parser')
    class_name = f'Screen__day Screen__day--visible Screen__day--{datetime.now().strftime("%A").lower()}'
    day_div = garrosSoup.find('div', {'class': class_name})

    garros_menu = []
    if day_div:
        menu_paragraph = day_div.find('p')
        if menu_paragraph:
            lunch_menu = menu_paragraph.get_text(separator="\n", strip=True)
            garros_menu = [
                {
                    "name": dish.strip(),
                    "price": "" if "ingår" in dish else "145"
                }
                for dish in lunch_menu.split('\n')
                if dish.strip() and "Fråga personalen" not in dish
            ]
except requests.exceptions.RequestException as e:
    print(f"Error fetching Garros menu: {e}")
    garros_menu = []

menus.append({
    "name": "Bistro Garros",
    "location": "Location details here",
    "menu": {"dishes": garros_menu}
})
print(garros_menu)

# PokéBurger
try:
    pokeHtml = requests.get("https://pokeburger.se/meny/alvik/", headers=headers)
    pokeHtml.raise_for_status()
    pokeSoup = BeautifulSoup(pokeHtml.content, 'html.parser')
    AllPokeMenus = pokeSoup.find_all('div', class_='dine-menu-wrapper')

    poke_dishes = []
    heading_map = {
        'VECKANS NO BOWL': 'Veckans No Bowl',
        'POKÉ BOWLS': 'Poké Bowls',
        'THE BURGERS': 'The Burgers'
    }

    for menu in AllPokeMenus[:3]:
        heading = menu.find('h2', class_='dine-menu-heading')
        if heading:
            heading = heading.text
            key = heading_map.get(heading.upper(), None)
        
            if key:
                menu_items = menu.find_all('div', class_='dine-menu-item')
            for item in menu_items:
                name = item.find('h3', class_='menu-item-name')
                description = item.find('div', class_='menu-item-desc')
                price_tag = item.find('span', class_='menu-item-price')
                
                if name and description:
                    if "11:00-14:00" in name.text:
                        continue
                    
                    price = price_tag.text.strip() if price_tag else ""
                    price = ''.join(re.findall(r'\d+', price))
                    poke_dishes.append({"name": f"{name.text.capitalize()} - {description.text.strip().lower()}", "price": price})
except requests.exceptions.RequestException as e:
    print(f"Error fetching PokéBurger menu: {e}")
    poke_dishes = []

menus.append({
    "name": "PokéBurger",
    "location": "Location details here",
    "menu": {"dishes": poke_dishes}
})

# Al Caminetto
try:
    alcamHtml = requests.get("https://www.alcaminetto.se/index.php/lunch", headers=headers)
    alcamHtml.raise_for_status()
    alcamSoup = BeautifulSoup(alcamHtml.content, 'html.parser')
    
    # Define the Swedish days of the week
    days = ["MÅNDAG", "TISDAG", "ONSDAG", "TORSDAG", "FREDAG"]
    # Get today's day name in Swedish
    today_index = datetime.now().weekday()
    today_swedish = days[today_index] if today_index < len(days) else None

    today_alcam_menu = []
    if today_swedish:
        try:
            p_tags = alcamSoup.find_all('p')
            # Iterate over each <p> tag
            for p_tag in p_tags:
                # Check if the tag contains today's day
                if today_swedish in p_tag.get_text():
                    # Get the text content from the <p> tag
                    p_text = p_tag.get_text()
                    # Use regex to split at transitions from lowercase to uppercase letters
                    dishes = re.split(r'(?<=[a-zåäö])(?=[A-ZÅÄÖ])', p_text)
                    for i, dish in enumerate(dishes):
                        # Clean up the dish name
                        dish_name = dish.strip()
                        # Ensure it's not empty and not the day name
                        if dish_name and dish_name != today_swedish:
                            # Remove the weekday from the start of the first dish
                            if i == 0 and dish_name.startswith(today_swedish):
                                dish_name = dish_name[len(today_swedish):].strip()
                            today_alcam_menu.append({"name": dish_name, "price": "139"})
                    break  # Found today's menu, no need to check further
        except Exception as e:
            today_alcam_menu = [{"name": "Error", "price": "Error"}]
    else:
        today_alcam_menu = [{"name": "Error", "price": "No menu available for today"}]

except requests.exceptions.RequestException as e:
    print(f"Error fetching Al Caminetto menu: {e}")
    today_alcam_menu = [{"name": "Error", "price": "Network issue"}]

menus.append({
    "name": "Al Caminetto",
    "location": "Location details here",
    "menu": {"dishes": today_alcam_menu}
})
#
## Gustafs
#try:
#    gustafsHtml = requests.get("https://www.gustafsrestaurang.se/index.php/lunch", headers=headers)
#    gustafsHtml.raise_for_status()
#    gustafsSoup = BeautifulSoup(gustafsHtml.content, 'html.parser')
#
#    day_translationGustafs = {
#        'monday': 'Måndag',
#        'tuesday': 'Tisdag',
#        'wednesday': 'Onsdag',
#        'thursday': 'Torsdag',
#        'friday': 'Fredag',
#        'saturday': 'Lördag',
#        'sunday': 'Söndag'
#    }
#
#    current_weekday = datetime.now().strftime('%A').lower()
#    current_day_swedish = day_translationGustafs.get(current_weekday)
#
#    todays_menu = []
#    current_day = None
#
#
#    # Ensure the container is found before proceeding
#    for element in gustafsSoup.find_all(['h3', 'h5']):
#        text = element.get_text(strip=True)
#        if text in day_translationGustafs.values():
#            current_day = text
#        elif current_day == current_day_swedish:
#            items = re.split(r'(?=[A-ZÅÄÖ])', text)
#            cleaned_items = [re.sub(r'\.[a-z]+$', '', item.strip()) for item in items if item.strip()]
#            
#            combined_items = []
#            i = 0
#            while i < len(cleaned_items):
#                words = cleaned_items[i].split()
#                if len(words) <= 2 and i < len(cleaned_items) - 1:
#                    combined_items.append(cleaned_items[i] + ' ' + cleaned_items[i+1])
#                    i += 2
#                else:
#                    combined_items.append(cleaned_items[i])
#                    i += 1
#            filtered_items = [
#                item for item in combined_items
#                if len(item) >= 15 and not re.search(r'\d', item)
#            ]
#
#            todays_menu.extend([{"name": item, "price": "149"} for item in filtered_items])
#
#except requests.exceptions.RequestException as e:
#    print(f"Error fetching Gustafs menu: {e}")
#    todays_menu = []
#
#menus.append({
#    "name": "Gustafs",
#    "location": "Location details here",
#    "menu": {"dishes": todays_menu}
#})

# Bastard Burgers
try:
    bastardHtml = requests.get("https://bastardburgers.com/se/dagens-lunch/bromma/", headers=headers)
    bastardHtml.raise_for_status()
    bastardSoup = BeautifulSoup(bastardHtml.content, "html.parser")
    menu_title = bastardSoup.find('h4')
    menu_description = bastardSoup.find('p')

    if menu_title and menu_description:
        menus.append({
            "name": "Bastard Burgers",
            "location": "Location details here",
            "menu": {"dishes": [{"name": f"{menu_title.get_text(strip=True)}: {menu_description.get_text(strip=True)}", "price": "132"}]}
        })
    else:
        menus.append({
            "name": "Bastard Burgers",
            "location": "Location details here",
            "menu": {"dishes": []}
        })
except requests.exceptions.RequestException as e:
    print(f"Error fetching Bastard Burgers menu: {e}")
    menus.append({
        "name": "Bastard Burgers",
        "location": "Location details here",
        "menu": {"dishes": []}
    })

# Sjöpaviljongen
try:
    sjoPaviljHtml = requests.get("https://sjopaviljongen.se/lunchmeny/", headers=headers)
    sjoPaviljHtml.raise_for_status()
    sjoPaviljSoup = BeautifulSoup(sjoPaviljHtml.content, "html.parser")
    
    # Find all tables
    tables = sjoPaviljSoup.find_all('table')
    sjopaviljongen_menu = []

    for table in tables:
        # Check if the table is not too short
        menu_items = table.find_all('p')
        if len(menu_items) >= 3:  # Adjust the length check as needed
            for item in menu_items:
                strong_tags = item.find_all('strong')
                combined_text = " ".join([strong_tag.get_text(strip=True) for strong_tag in strong_tags])
                
                dishes = combined_text.split('DAGENS')
                
                for dish in dishes:
                    dish_name = dish.strip()
                    if dish_name.startswith("TIPS "):
                        dish_name = dish_name[5:].strip()
                    
                    match_start = re.search(r'\d+ kr\s*(.+)', dish_name)
                    match_end = re.search(r'(.+?)\s*\d+\s*kr$', dish_name)
                    
                    if match_start:
                        cleaned_dish_name = match_start.group(1).strip()
                        price = match_start.group(0).strip()
                    elif match_end:
                        cleaned_dish_name = match_end.group(1).strip()
                        price = match_end.group(0).strip()
                    else:
                        cleaned_dish_name = dish_name.strip()
                        price = ""
                    
                    price_numeric = re.sub(r'\D', '', price)
                    if cleaned_dish_name:
                        sjopaviljongen_menu.append({"name": cleaned_dish_name, "price": price_numeric})
            break  # Exit the loop once a suitable table is found

except requests.exceptions.RequestException as e:
    print(f"Error fetching Sjöpaviljongen menu: {e}")
    sjopaviljongen_menu = []
    
menus.append({
    "name": "Sjöpaviljongen",
    "location": "Location details here",
    "menu": {"dishes": sjopaviljongen_menu}
})

# Melanders (Get PDF link and process)
try:
    melandersHtml = requests.get("https://melanders.se/restauranger/melanders-alvik/", headers=headers)
    melandersHtml.raise_for_status()
    melandersSoup = BeautifulSoup(melandersHtml.content, 'html.parser')

    # Define the Swedish days of the week
    days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag"]

    # Create a regular expression pattern to split the text based on the days
    pattern = '|'.join(days)
            
    # Find the PDF link
    pdf_link_tag = melandersSoup.find('a', text="DAGENS LUNCH")
    pdf_url = pdf_link_tag['href'] if pdf_link_tag else None

    melanders_menu = []
    if pdf_url:
        pdf_path = "menu.pdf"
        urllib.request.urlretrieve(pdf_url, pdf_path)
        pdf = pdfquery.PDFQuery(pdf_path)
        pdf.load()
        all_text = ""
        for page_number in range(len(pdf.pq('LTPage'))):
            pdf.load(page_number)
            page_text = pdf.pq('LTTextLineHorizontal').text()
            all_text += page_text + "\n"
        
        split_text = re.split(f'(?=({pattern}))', all_text)
        # Remove any leading text before the first day
        split_text = split_text[1:]
        menus_by_day = {}
        for i in range(0, len(split_text), 2):
            if i + 1 < len(split_text):
                day = split_text[i].strip()
                menu = split_text[i+1].strip()
                # Remove the day's name from the menu
                if menu.startswith(day):
                    menu = menu[len(day):].strip()
                menu = re.sub(r'\(.*?\)', '', menu)  # Remove text in parentheses
                menus_by_day[day] = menu
        # Determine today's day in Swedish
        today_index = datetime.now().weekday()  # Monday is 0, Sunday is 6
        swedish_days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]
        today_swedish = swedish_days[today_index]
        today_menu = menus_by_day.get(today_swedish, "No menu available for today")
        today_melanders_menu = []
        if today_menu != "No menu available for today":
            today_melanders_menu = [{"name": dish.strip(), "price": "149"} for dish in re.split(r'(?=[A-ZÅÄÖ])', today_menu) if dish.strip()]


except requests.exceptions.RequestException as e:
    print(f"Error fetching Melanders menu: {e}")
    
menus.append({
    "name": "Melanders",
    "location": "Location details here",
    "menu": {"dishes": today_melanders_menu}
})

# Add a timestamp to the JSON data
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
output_data = {
    "last_updated": timestamp,
    "restaurants": menus
}

output_path = os.path.join("public", "menus.json")

# Save the menus to a JSON file
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print("Menus saved to menus.json")