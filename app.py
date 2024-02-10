from flask import Flask, render_template, request, jsonify, session, url_for, redirect
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request
import base64
from datetime import datetime
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
app.secret_key = 'secret_key'

load_dotenv()
client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')

auth = HTTPBasicAuth()
@auth.verify_password
def verify_password(username, password):
    # Replace 'your_username' and 'your_password' with your desired credentials
    return username == 'admin' and password == '123'

@app.route('/')
@auth.login_required
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    modelNumber = request.form.get('modelNumber')
    priceLimit = request.form.get('priceLimit')

    partSelectURL = 'https://www.partselect.com/Models/{}/'.format(modelNumber)
    headers={'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
    response = requests.get(partSelectURL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    appliance  = ' '.join(soup.find('h1').text.replace('- Overview','').strip().split()[1:-1])

    partSelectURL = 'https://www.partselect.com/Models/{}/Parts/'.format(modelNumber)
    response = requests.get(partSelectURL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    pagination = soup.find('ul', class_='pagination js-pagination')
    if pagination is not None:
        total_page = int(pagination.find_all('li')[-2].find('a').text)
    else:
        total_page = 1
    print(total_page)
    print('response code: ', response)

    searches = []
    for page in range(1,total_page+1):
        partSelectURL = 'https://www.partselect.com/Models/{}/Parts/?start={}'.format(modelNumber,page)
        response = requests.get(partSelectURL, headers= headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        if soup.find('div', class_='row mt-3 align-items-stretch') is not None:
            partDivElements = soup.find('div', class_='row mt-3 align-items-stretch').find_all('div', class_='col-md-6 mb-3')
            for part in partDivElements:
                modelEle = part.find('div', class_='mb-1')
                manufacturerNum = modelEle.get_text(strip=True).split(':')[-1].strip()
                search = appliance + ' ' + manufacturerNum
                searches.append(search)
    session['searches'] = searches
    session['modelNumber'] = modelNumber
    session['priceLimit'] = priceLimit

    return render_template('process.html', len_searches_list=len(searches))

@app.route('/results')
def results():
    searches = session.get('searches', [])
    modelNumber = session.get('modelNumber', '')
    priceLimit = session.get('priceLimit', '')
    def find_value(params, min_price):
        ENDPOINT = 'https://svcs.ebay.com/services/search/FindingService/v1'
        headers = {
        'X-EBAY-SOA-SECURITY-APPNAME': client_id,
        'X-EBAY-SOA-OPERATION-NAME': 'findItemsAdvanced',
        'X-EBAY-SOA-RESPONSE-DATA-FORMAT': 'JSON',
        'X-EBAY-SOA-SERVICE-NAME': 'FindingService',
        'X-EBAY-SOA-SERVICE-VERSION': '1.0.0'
        }


        response = requests.get(ENDPOINT, headers=headers, params=params)
        response_json = response.json()
        items = response_json.get("findItemsAdvancedResponse", {})[0].get("searchResult", {})[0].get("item", [])
        page_url = response_json['findItemsAdvancedResponse'][0]['itemSearchURL'][0]
        di = []
        title = ''
        price = 0
        for item in items[:1]:
            title = item.get("title", "N/A")[0]
            price = item.get("sellingStatus", {})[0].get("currentPrice", {})[0].get("__value__", {})
            currency = item.get("sellingStatus", {})[0].get("currentPrice", {})[0].get("@currencyId", {})
            if float(price) >= float(min_price):
                di = [title, price+' '+currency, page_url]
            else:
                di = ['', '', page_url]

        return di


    
    all_di = []
    if len(searches)>17:
        searches = searches[:16]

    for search in searches:
        params1 = {
        'keywords': search,
        'paginationInput': {
            'entriesPerPage': 1,
            'pageNumber': 1
        },
        'itemFilter(0).name': 'ListingType',
        'itemFilter(0).value': 'FixedPrice',  # Buy It Now

        'itemFilter(1).name': 'Condition',
        'itemFilter(1).value': 'Used',  # Used Condition
        'sortOrder': 'PricePlusShippingLowest'  # Sort by price from high to low
        }
        params3 = {
                'keywords': search,
                'paginationInput': {
                    'entriesPerPage': 1,
                    'pageNumber': 1
                },
                'itemFilter(0).name': 'ListingType',
                'itemFilter(0).value': 'FixedPrice',  # Buy It Now
                'itemFilter(1).name': 'Condition',
                'itemFilter(1).value': 'New',  # Used Condition
                'sortOrder': 'PricePlusShippingLowest'  # Sort by price from high to low
            }

        
        di1 = find_value(params1,  min_price = priceLimit)
        di3 = find_value(params3,  min_price = priceLimit)
        di = [search,di1,di3]
        all_di.append(di)
        

    return render_template('results.html', results_data=all_di, modelNumber=modelNumber)
##
# if __name__ == '__main__':
#     app.run(debug=True)
