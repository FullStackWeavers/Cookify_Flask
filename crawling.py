import requests
from bs4 import BeautifulSoup

# 기존 코드...

def get_recipe_detail(recipe_id):
    url = f'https://www.10000recipe.com/recipe/{recipe_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # print(soup)
        # 레시피 상세 정보 추출하는 코드 작성
        title = soup.select_one('.view2_summary h3').text
        ingredients = [li.text for li in soup.select('.ready_ingre3 ul:nth-child(1) li')]
        ingredients2 = [li.text for li in soup.select('.ready_ingre3 ul:nth-child(2) li')]
        steps = soup.select('.view_step_cont')
        descriptions = [step.select_one('.media-body').text.strip() for step in steps]

        recipe_detail = {
            'title': title,
            'ingredients': ingredients,
            'ingredients2': ingredients2,
            'steps': descriptions
        }

        return recipe_detail
    else:
        print('Error:', response.status_code)
        return None


def crawl_recipe_list():
    url = 'https://www.10000recipe.com/recipe/list.html'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    response = requests.get(url, headers=headers)
    recipe_list = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        recipes = soup.select('.common_sp_list_ul.ea4 .common_sp_list_li')

        for recipe in recipes:
            link_element = recipe.select_one('.common_sp_thumb .common_sp_link')
            title = recipe.select_one('.common_sp_caption .common_sp_caption_tit.line2').text
            if link_element:
                img = link_element.select_one('a img:not([src*="icon_vod.png"])')['src']
                # print(img)
                uid = link_element['href']
                recipe_id = uid.split('/')[-1]

                # print(recipe_id)
                recipe_list.append({
                    'title': title,
                    'img': img,
                    'id': recipe_id,
                    'url': f'https://www.10000recipe.com/recipe/{recipe_id}'
                })
            else:
                print('링크를 찾을 수 없습니다.')
    else:
        print('Error:', response.status_code)

    return recipe_list
