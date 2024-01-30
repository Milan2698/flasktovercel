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
    partSelectURL = 'https://www.partselect.com/Models/{}/Parts/'.format(modelNumber)
    headers={'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
    response = requests.get(partSelectURL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    appliance  = soup.find('h1').text.split(modelNumber)[-1].split()[0]

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
    return render_template('process.html', len_searches_list=len(searches))

@app.route('/results')
def results():
    searches = session.get('searches', [])
    modelNumber = session.get('modelNumber', '')
    def find_value(search_url, search):
    
        auth_url = "https://api.ebay.com/identity/v1/oauth2/token"
        auth_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode(),
        }
        auth_payload = {
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope"
        }

        auth_response = requests.post(auth_url, headers=auth_headers, data=auth_payload)
        auth_data = auth_response.json()
        access_token = auth_data['access_token']

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        search_response = requests.get(search_url, headers=headers)
        search_data = search_response.json()

        di = []
        if "itemSummaries" in search_data:
            for item in search_data["itemSummaries"]:
                if search.split()[-1] in item['title']:
                    di = [item['title'],item['price']['value']+' '+item['price']['currency']]
                    break

        return di


    USED = '{USED}'
    FIXED_PRICE = '{FIXED_PRICE}'
    NEW = '{NEW}'
    all_di = []
    if len(searches)>17:
        searches = searches[:16]

    for search in searches:
        print('Index from searches: ',searches.index(search))

        query = search.replace(' ','%20')
        #Buy it now, used, Low to High
        search_url_1 = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={query}&limit=2&filter=conditions:{USED}&filter=buyingOptions:{FIXED_PRICE}&sort=price"

        #Buy it now, Sold Item, used, High to low
        search_url_2 = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={query}&limit=2&filter=conditions:{USED}&filter=buyingOptions:{FIXED_PRICE}&filter=lastSoldDate:[2019-01-01T00:00:00Z..{datetime.utcnow().isoformat()}z]&sort=-price"

        #New, Buy it now, Low to High
        search_url_3 = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={query}&limit=2&filter=conditions:{NEW}&filter=buyingOptions:{FIXED_PRICE}&sort=price"
        
        di1 = find_value(search_url_1, search)
        di2 = find_value(search_url_2, search) 
        di3 = find_value(search_url_3, search)
        di = [search,di1,di2,di3]
        all_di.append(di)
        

    return render_template('results.html', results_data=all_di, modelNumber=modelNumber)

# if __name__ == '__main__':
#     app.run(debug=True)
