from flask import Flask, render_template, request, jsonify, session
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

app = Flask(__name__)
# app.secret_key = 'secret_key'

access_token = os.getenv("EBAY_ACCESS_TOKEN")
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/perform_search', methods=['POST'])
def perform_search():
    modelNumber = request.json['modelNumber']

    partSelectURL = 'https://www.partselect.com/Models/{}/Parts/'.format(modelNumber)
    response = requests.get(partSelectURL)
    soup = BeautifulSoup(response.content, 'html.parser')

    appliance = soup.find('h1').text.split(modelNumber)[-1].split()[0]

    pagination = soup.find('ul', class_='pagination js-pagination')
    if pagination is not None:
        total_page = int(pagination.find_all('li')[-2].find('a').text)
    else:
        total_page = 1

    searches = []
    for page in range(1, total_page + 1):
        partSelectURL = 'https://www.partselect.com/Models/{}/Parts/?start={}'.format(modelNumber, page)
        response = requests.get(partSelectURL)
        soup = BeautifulSoup(response.content, 'html.parser')
        partDivElements = soup.find('div', class_='row mt-3 align-items-stretch').find_all('div', class_='col-md-6 mb-3')
        for part in partDivElements:
            modelEle = part.find('div', class_='mb-1')
            manufacturerNum = modelEle.get_text(strip=True).split(':')[-1].strip()
            search = appliance + ' ' + manufacturerNum
            searches.append(search)

    # Store data in the session
    # session['modelNumber'] = modelNumber
    # session['searches'] = searches
    # modelNumber = session.get('modelNumber', None)
    # searches = session.get('searches', [])

    return jsonify({'searches_length': len(searches)})

@app.route('/results')
def results():
    modelNumber = request.args.get('modelNumber')
    searches = request.args.get('searches').split(',')
    # modelNumber = session.get('modelNumber', None)
    # searches = session.get('searches', [])
    

    def API(query):
        search_url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={query}&limit=1"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        search_response = requests.get(search_url, headers=headers)
        search_data = search_response.json()
        di = dict()
        if "itemSummaries" in search_data:
            for item in search_data["itemSummaries"]:
                di['Title'] = item['title']
                di['Price'] = item['price']['value'] + ' ' + item['price']['currency']
        else:
            di = {"Title": "No search results found", "Price": ""}
        return di

    results_list = []
    for search in searches[:5]:
        query = search.replace(' ', '%20')
        result = API(query)
        results_list.append(result)

    return render_template('results.html', modelNumber=modelNumber, results_list=results_list)

