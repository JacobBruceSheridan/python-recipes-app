from flask import Flask, render_template, request, make_response, redirect, url_for, flash
from tools import getRecipeById, email_support, getRecipes, read_from_file, write_to_file, get_recipe_categories, get_recipe_by_category, emailIngredients
import requests
import json
import uuid
import smtplib
from email.message import EmailMessage


app = Flask(__name__)
app.secret_key = str(uuid.uuid1)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/contactEmail', methods=['GET', 'POST'])
def contactEmail():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    email_support(name, email, message)
    flash('Email Successfully sent. Please await a response.')
    return render_template('flash.html')


@app.route('/recipes')
def recipes():
    return render_template('recipes.html')


@app.route('/category', methods=['GET', 'POST'])
def category():
    query = request.form.get('search-query')
    recipes = get_recipe_by_category(query)
    return render_template('recipes.html', recipes=recipes)


@app.route('/archived')
def archived():
    recipeList = []
    temp = read_from_file()
    if request.cookies.get('archivedId'):
        cookieId = request.cookies.get('archivedId')
        for usersCart in temp:
            if usersCart['id'] == cookieId:
                recipeList = usersCart['recipes']
    else:
        recipeList = 'Empty'
    email = ''
    if request.cookies.get('email'):
        email = request.cookies.get('email')
    return render_template('archived.html', recipes=recipeList, email=email)

# change to view categories
@app.route('/categories')
def searchPage():
    data = get_recipe_categories()
    return render_template('categories.html', categories=data['categories'])


@app.route('/deleteArchive')
def deleteArchive():
    resp = make_response(redirect(url_for('archived')))
    resp.set_cookie('archivedId', expires=0)
    temp = read_from_file()
    if request.cookies.get('archivedId'):
        for usersCart in temp:
            if request.cookies.get('archivedId') == usersCart['id']:
                temp.remove(usersCart)
    write_to_file(temp)
    return resp


@app.route('/email', methods=['GET', 'POST'])
def email():
    recipeList = []
    email = request.form.get('email')
    temp = read_from_file()
    if request.cookies.get('archivedId'):
        cookieId = request.cookies.get('archivedId')
        for usersCart in temp:
            if usersCart['id'] == cookieId:
                recipeList = usersCart['recipes']
    emailIngredients(recipeList, email)
    flash('Email successfully sent.')
    resp = make_response(render_template('flash.html'))
    resp.set_cookie('email', email, max_age=None)
    return resp


@app.route('/recipe', methods=['GET', 'POST'])
def recipe():
    recipe_id = request.form.get('recipe')
    recipe = getRecipeById(recipe_id)
    return render_template('recipe.html', recipe=recipe)


@app.route('/searchRecipes', methods=['GET', 'POST'])
def searchRecipes():
    query = request.form.get('search-query')
    recipes = getRecipes(query)
    return render_template('recipes.html', recipes=recipes)


@app.route('/archiveCurrentRecipe', methods=['GET', 'POST'])
def archiveCurrentRecipe():
    temp = []
    cookieId = ''
    archivedCart = {}

    temp = read_from_file()

    resp = make_response(redirect(url_for('archived')))

    if request.cookies.get('archivedId'):
        cookieId = request.cookies.get('archivedId')
        for usersCart in temp:
            if usersCart['id'] == cookieId:
                tempRecipes = usersCart['recipes']
                tempRecipes = tempRecipes.insert(len(tempRecipes), {
                    'id': request.form.get('recipeId'),
                    'name': request.form.get('recipeName'),
                    'image': request.form.get('recipeImage'),
                    'ingredients': request.form.get('recipeIngredients'),
                })
                usersCart = {
                    "id": usersCart['id'],
                    "recipes": tempRecipes
                }
    else:
        cookieId = str(uuid.uuid1())
        resp.set_cookie('archivedId', cookieId, max_age=None)
        archivedCart = {
            'id': cookieId,
            'recipes': [
                {
                    'id': request.form.get('recipeId'),
                    'name': request.form.get('recipeName'),
                    'image': request.form.get('recipeImage'),
                    'ingredients': request.form.get('recipeIngredients'),
                }
            ]
        }
        temp.insert(len(temp), archivedCart)

    write_to_file(temp)

    return resp


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(Exception)
def server_error(e):
    return render_template('exception.html', error=e), 500


if __name__ == '__main__':
    app.run(debug=True)
