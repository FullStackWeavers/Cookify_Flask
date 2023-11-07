import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify, request
import crawling

app = Flask(__name__)

@app.route('/')
def index():
    recipe_list = crawling.crawl_recipe_list()
    return render_template('index.html', recipe_list=recipe_list)

@app.route('/recipe/<string:recipe_id>')
def recipe_detail(recipe_id):
    recipe = crawling.get_recipe_detail(recipe_id)
    # print(recipe)
    return render_template('recipe_detail.html', recipe=recipe)

@app.route('/home')
def home():

        # 베이스 URL 설정
        base_url = "https://www.10000recipe.com/profile/recipe.html?uid=gdubu33"

        current_page = request.args.get('page', default=1, type=int)

        # 페이지 범위 설정 (10 페이지씩)
        page_start = current_page
        page_end = current_page + 9

        # 현재 페이지 범위의 레시피 아이템 가져오기
        recipe_items = crawling.get_recipe_items_for_range(base_url, page_start, page_end)

        return render_template('recipes.html', recipe_items=recipe_items, current_page=current_page)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5005, debug=True)
