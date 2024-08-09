import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Configuration
base_url = 'https://www.zomato.com/bangalore/restaurants?page='
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Initialize data storage
restaurant_links = []
restaurants_data = []


# Function to extract restaurant links from the listing page
def extract_restaurant_links(soup):
    restaurants = soup.find_all('div', class_='search-snippet-card')
    for restaurant in restaurants:
        link = restaurant.find('a', class_='result-title')['href']
        restaurant_links.append(link)


# Function to extract restaurant details from the restaurant page
def extract_restaurant_details(restaurant_link):
    response = requests.get(restaurant_link, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    try:
        restaurant_id = soup.find('meta', {'property': 'og:url'})['content'].split('/')[-1].split('?')[0]
        name = soup.find('h1', class_='sc-7kepeu-0 sc-fujyUd dYcxKh').text.strip()
        rating = soup.find('div', class_='sc-1q7bklc-1 cILgox').text.strip()
        cuisine = ', '.join([cuisine.text for cuisine in soup.find_all('div', class_='sc-16r8icm-0 sc-iBPRYJ iQzA-DM')])
        location = soup.find('div', class_='sc-1hez2tp-0 sc-lkmgSk fnWaJN').text.strip()
        timings = soup.find('div', class_='sc-1hez2tp-0 sc-cNnxps dnSnwP').text.strip()

        popular_dishes_tag = soup.find('div', class_='sc-1s0saks-0 bYlDHL')
        popular_dishes = popular_dishes_tag.text.strip() if popular_dishes_tag else 'N/A'

        known_for_tag = soup.find('div', class_='sc-1s0saks-0 dDAdJs')
        known_for = known_for_tag.text.strip() if known_for_tag else 'N/A'

        delivery_review_tag = soup.find('span', class_='sc-1hez2tp-0 sc-kpOJdX cSMCbR')
        delivery_review_number = delivery_review_tag.text.strip().split(' ')[0] if delivery_review_tag else 'N/A'

        details = {
            'restaurant_id': restaurant_id,
            'restaurant_name': name,
            'restaurant_link': restaurant_link,
            'rating': rating,
            'cuisine': cuisine,
            'location': location,
            'timings': timings,
            'dish_name': popular_dishes,
            'restaurant_known_for': known_for,
            'delivery_review_number': delivery_review_number
        }

        restaurants_data.append(details)
    except Exception as e:
        print(f"Error extracting details for restaurant {restaurant_link}: {e}")


# Scrape restaurant listings to get links
page = 1
while True:
    url = base_url + str(page)
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    if not soup.find_all('div', class_='search-snippet-card'):
        break

    extract_restaurant_links(soup)
    page += 1
    time.sleep(1)  # Be polite and avoid hammering the server

# Scrape details for each restaurant
for link in restaurant_links:
    extract_restaurant_details(link)
    time.sleep(2)  # Be polite and avoid hammering the server

# Save data to CSV file
df_restaurants = pd.DataFrame(restaurants_data)
df_restaurants.to_csv('zomato_bangalore_restaurants.csv', index=False)

# Output the extracted information
print(df_restaurants.head())
