from flask import Flask, render_template
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

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
