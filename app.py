import time

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/cookify'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(5000), nullable=False, unique=True)
    ingredients = db.Column(db.String(5000), nullable=False)
    ingredients2 = db.Column(db.String(5000))
    steps = db.Column(db.String(5000), nullable=False)
    thumbnail = db.Column(db.String(5000))

def save_recipe_to_database(recipe_detail):
    with app.app_context():
        existing_recipe = Recipe.query.filter_by(title=recipe_detail['title']).first()
        if existing_recipe:
            print(f"Recipe '{recipe_detail['title']}' already exists. Skipping...")
            return

        new_recipe = Recipe(
            title=recipe_detail['title'],
            ingredients=', '.join(recipe_detail['ingredients']),
            ingredients2=', '.join(recipe_detail['ingredients2']),
            steps=', '.join(recipe_detail['steps']),
            thumbnail=recipe_detail['thumbnail']
        )

        db.session.add(new_recipe)
        db.session.commit()



def get_recipe_detail(recipe_id):
    url = f'https://www.10000recipe.com/recipe/{recipe_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }

    max_retries = 3
    retries = 0

    while retries < max_retries:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            retries += 1
            time.sleep(2)  # Wait for a few seconds before retrying
        else:
            # Successfully retrieved the response
            break
    else:
        # Max retries reached, handle this as needed
        print(f"Max retries reached for recipe {recipe_id}. Skipping...")
        return None

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.select_one('.view2_summary h3').text
        ingredients = [li.text for li in soup.select('.ready_ingre3 ul:nth-child(1) li')]
        ingredients2 = [li.text for li in soup.select('.ready_ingre3 ul:nth-child(2) li')]
        steps = soup.select('.view_step_cont')
        descriptions = [step.select_one('.media-body').text.strip() for step in steps]
        thumbnail = soup.select_one('.centeredcrop img')['src']

        recipe_detail = {
            'title': title,
            'ingredients': ingredients,
            'ingredients2': ingredients2,
            'steps': descriptions,
            'thumbnail': thumbnail
        }

        return recipe_detail
    else:
        print(f'Error: {response.status_code}')
        return None

def get_recipe_items(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        recipe_items = soup.find_all('a', class_='thumbnail')
        return recipe_items
    else:
        return []

def get_recipe_items_for_range(base_url, page_start, page_end):
    all_recipe_items = []
    for page in range(page_start, page_end + 1):
        url = f"{base_url}&page={page}"
        recipe_items = get_recipe_items(url)
        all_recipe_items.extend(recipe_items)
    return all_recipe_items

def save_recipes_in_range(base_url, page_start, page_end):
    with app.app_context():
        db.create_all()

    for page in range(page_start, page_end + 1):
        url = f"{base_url}&page={page}"
        recipe_items = get_recipe_items(url)

        for item in recipe_items:
            recipe_id = item['href'].split('/')[-1]
            recipe_detail = get_recipe_detail(recipe_id)

            if recipe_detail:
                save_recipe_to_database(recipe_detail)
                print(f"Recipe '{recipe_detail['title']}' saved to the database!")

        print(f"Finished saving recipes on page {page}")

if __name__ == '__main__':
    save_recipes_in_range("https://www.10000recipe.com/profile/recipe.html?uid=gdubu33", 51, 245)
