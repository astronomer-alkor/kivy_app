import requests

BASE_URL = 'http://f967f9fb.ngrok.io'


def get_categories_structure():
    return requests.get(f'{BASE_URL}/api/v0/get_structure').json()


def get_catalog(url):
    return requests.get(f'{BASE_URL}/api/v0{url}').json()


def get_product(category, product):
    return requests.get(f'{BASE_URL}/api/v0/{category}/{product}').json()
