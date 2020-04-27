import requests
import json
import smtplib
from email.message import EmailMessage

api_ley = '1'


def getRecipeById(recipeId):
    response = requests.get(
        f'https://www.themealdb.com/api/json/v1/{api_ley}/lookup.php?i={recipeId}').json()
    ingredients = []
    for x in range(19):  # 19 becuase there are 19 ingredient slots on the recipee object
        if response['meals'][0]['strIngredient'+str(x+1)] == '' or response['meals'][0]['strIngredient'+str(x+1)] == None:
            break
        ingredients.insert(x, response['meals'][0]['strMeasure'+str(
            x+1)] + ' ' + response['meals'][0]['strIngredient'+str(x+1)])
    recipe = {
        'id': response['meals'][0]['idMeal'],
        'name': response['meals'][0]['strMeal'],
        'instructions': response['meals'][0]['strInstructions'],
        'image': response['meals'][0]['strMealThumb'],
        'ingredients': ingredients,
        'youtube': response['meals'][0]['strYoutube']
    }
    return recipe


def getRecipes(query):
    response = requests.get(
        f'https://www.themealdb.com/api/json/v1/{api_ley}/search.php?s={query}').json()
    recipes = []
    if not response['meals']:
        recipes = 'Empty'
    else:
        for x in range(len(response['meals'])):
            recipes.insert(x, {
                'id': response['meals'][x]['idMeal'],
                'name': response['meals'][x]['strMeal'],
                'image': response['meals'][x]['strMealThumb']
            })

    return recipes


def get_recipe_categories():
    response = requests.get(
        f'https://www.themealdb.com/api/json/v1/{api_ley}/categories.php').json()
    return response


def get_recipe_by_category(query):
    response = requests.get(
        f'https://www.themealdb.com/api/json/v1/{api_ley}/filter.php?c={query}').json()
    recipes = []
    for x in range(len(response['meals'])):
        recipes.insert(x, {
            'id': response['meals'][x]['idMeal'],
            'name': response['meals'][x]['strMeal'],
            'image': response['meals'][x]['strMealThumb']
        })
    return recipes


def read_from_file():
    with open('./repositories/archivedRepo.json') as json_file:
        return json.load(json_file)['archives']


def write_to_file(data):
    with open('./repositories/archivedRepo.json', 'w') as outfile:
        json.dump({'archives': data}, outfile, indent=4)


def email_support(name, email, message):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        email_username = 'pythonwebrecipes@gmail.com'
        smtp.login(email_username, 'Nibster3')
        msg = EmailMessage()
        msg['Subject'] = 'Support ticket'
        msg['From'] = email_username
        msg['To'] = 'Jacobwbruce@hotmail.com'

        msg.set_content(f'From: {name}\nEmail: {email}\n\n{message}')

        smtp.send_message(msg)


def emailIngredients(recipeList, email):
    # separate the recipelist String into a string list
    ingredients = []
    for recipe in recipeList:
        ingredients.extend(
            recipe['ingredients'].strip('][').split(', '))
    # prepare email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        email_username = 'pythonwebrecipes@gmail.com'
        smtp.login(email_username, 'Nibster3')
        msg = EmailMessage()
        msg['Subject'] = 'Ingredients List'
        msg['From'] = email_username
        msg['To'] = email

        # Set basic text string content
        msg.set_content(f'List of ingredients:\n{ingredients}')

        # push all ingredients into <li> elements
        ingredientsHTML = ''
        for ingredient in ingredients:
            ingredientsHTML += f'<li>{ingredient}</li>'
        # Set HTML email content
        msg.add_alternative("""
        <!DOCKTYPE html>
        <html> 
            <body>
            <h1 style="background-color: #43a047; color: #fff">Ingredients</h1>
                <ul>
                {ingredients}
                </ul>
            </body>
        </html>
        """.format(ingredients=ingredientsHTML), subtype='html')

        # send email
        smtp.send_message(msg)
