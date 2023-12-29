from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from flask_httpauth import HTTPBasicAuth
from time import sleep
import random
import os
from scrapingbee import ScrapingBeeClient
from dotenv import load_dotenv
# Load environment variables from the .env file
load_dotenv()
# Access the API key
api_key = os.getenv("API_KEY")

auth = HTTPBasicAuth()


app = Flask(__name__)
chromedriver_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'chromedriver.exe')


@auth.verify_password
def verify_password(username, password):
    # Replace 'your_username' and 'your_password' with your desired credentials
    return username == 'admin' and password == '123'


def firstColumn(search):
    newSearch = '+'.join(search.split())
    url = f'https://www.ebay.com/sch/i.html?_from=R40&_nkw={newSearch}&LH_BIN=1&LH_ItemCondition=3000&_sop=15'
    print(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    total_result = int(soup.find('h1', class_='srp-controls__count-heading').find('span').text)
    productPrice = None
    if total_result != 0:
        productPriceUL = soup.find('ul', class_='srp-results srp-list clearfix')
        if productPriceUL is None:
            productPriceUL = soup.find('ul', class_='srp-results srp-grid clearfix')
        productPriceTag = productPriceUL.find('span', class_='s-item__price')
        if productPriceTag is not None:
            productPrice = productPriceTag.text
            heading = soup.find_all('div', class_='s-item__title')[1].find('span', role='heading').text
            if search.split()[-1] not in heading:
                productPrice = None

        
    return productPrice

def secondColumn(search):
    newSearch = '+'.join(search.split())
    url = f'https://www.ebay.com/sch/i.html?_from=R40&_nkw={newSearch}&LH_BIN=1&LH_Sold=1&LH_ItemCondition=3000&_sop=16'
    print(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    total_result = int(soup.find('h1', class_='srp-controls__count-heading').find('span').text)
    productPrice = None
    if total_result != 0:
        productPriceUL = soup.find('ul', class_='srp-results srp-list clearfix')
        if productPriceUL is None:
            productPriceUL = soup.find('ul', class_='srp-results srp-grid clearfix')
        productPriceTag = productPriceUL.find('span', class_='s-item__price')
        if productPriceTag is not None:
            productPrice = productPriceTag.text
            heading = soup.find_all('div', class_='s-item__title')[1].find('span', role='heading').text
            if search.split()[-1] not in heading:
                productPrice = None

    return productPrice

def thirdColumn(search):
    newSearch = '+'.join(search.split())
    url = f'https://www.ebay.com/sch/i.html?_from=R40&_nkw={newSearch}&LH_ItemCondition=1000&LH_BIN=1&_sop=15'
    print(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    total_result = int(soup.find('h1', class_='srp-controls__count-heading').find('span').text)
    productPrice = None
    if total_result != 0:
        productPriceUL = soup.find('ul', class_='srp-results srp-list clearfix')
        if productPriceUL is None:
            productPriceUL = soup.find('ul', class_='srp-results srp-grid clearfix')
        productPriceTag = productPriceUL.find('span', class_='s-item__price')
        if productPriceTag is not None:
            productPrice = productPriceTag.text
            heading = soup.find_all('div', class_='s-item__title')[1].find('span', role='heading').text
            if search.split()[-1] not in heading:
                productPrice = None

    return productPrice


@app.route('/api/get_data', methods=['GET'])
def get_data():
    modelNumber = request.args.get('modelNumber')
    print(modelNumber)

    searches = []
    client = ScrapingBeeClient(api_key=api_key)
    partSelectURL = 'https://www.partselect.com/Models/{}/Parts/'.format(modelNumber)
    response = client.get(partSelectURL)

    soup = BeautifulSoup(response.content, "html.parser")
    appliance = soup.find('h1').text.split(modelNumber)[-1].split()[0]
    partDivElements = soup.find('div', class_='row mt-3 align-items-stretch').find_all('div', class_='col-md-6 mb-3')
    for part in partDivElements:
        modelEle = part.find('div', class_='mb-1')
        manufacturerNum = modelEle.get_text(strip=True).split(':')[-1].strip()
        search = appliance + ' ' + manufacturerNum
        searches.append(search)
    
    # partSelectURL = 'https://www.partselect.com/Models/{}/Parts/'.format(modelNumber)
    # response = requests.get(partSelectURL)
    # soup = BeautifulSoup(response.content, 'html.parser')

    # appliance = soup.find('h1').text.split(modelNumber)[-1].split()[0]
    # pagination = soup.find('ul', class_='pagination js-pagination')
    # if pagination is not None:
    #     total_page = int(pagination.find_all('li')[-2].find('a').text)
    # else:
    #     total_page = 1

    # searches = []

    # for page in range(1,total_page+1):
    #     partSelectURL = 'https://www.partselect.com/Models/{}/Parts/?start={}'.format(modelNumber,page)
    #     response = requests.get(partSelectURL)
    #     soup = BeautifulSoup(response.content, 'html.parser')
    #     partDivElements = soup.find('div', class_='row mt-3 align-items-stretch').find_all('div', class_='col-md-6 mb-3')
    #     for part in partDivElements:
    #         modelEle = part.find('div', class_='mb-1')
    #         manufacturerNum = modelEle.get_text(strip=True).split(':')[-1].strip()
    #         search = appliance + ' ' + manufacturerNum
    #         searches.append(search)
    #     # t = random.randint(2,6)
    #     # sleep(t)
    #         print(len(searches))


    data = []
    for search in searches[:2]:
        di = {}
        first = firstColumn(search)
        second = secondColumn(search)
        third = thirdColumn(search)

        di['search'] = search
        di['firstColumn'] = first
        di['secondColumn'] = second
        di['thirdColumn'] = third
        data.append(di)

    # Include the length of the searches list in the returned JSON data
    response_data = {'length': len(searches), 'data': data}

    return jsonify(response_data)

    # return jsonify(data)

@app.route('/')
@auth.login_required
def index():
    return render_template('index.html')


# if __name__ == '__main__':
#     app.run(debug=True)
