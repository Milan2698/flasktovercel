from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)
# app.secret_key = 'secret_key'


def firstColumn(search):
    newSearch = '+'.join(search.split())
    url = f'https://www.ebay.com/sch/i.html?_from=R40&_nkw={newSearch}&LH_BIN=1&LH_ItemCondition=3000&_sop=15'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    productPriceTag = soup.find('ul', class_='srp-results srp-list clearfix').find('span', class_='s-item__price')
    if productPriceTag is not None:
        productPrice = productPriceTag.text
        heading = soup.find_all('div', class_='s-item__title')[1].find('span', role='heading').text
        if search.split()[-1] not in heading:
            productPrice = None
    else:
        productPrice = None
        
    return productPrice

def secondColumn(search):
    newSearch = '+'.join(search.split())
    url = f'https://www.ebay.com/sch/i.html?_from=R40&_nkw={newSearch}&LH_BIN=1&LH_Sold=1&LH_ItemCondition=3000&_sop=16'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    productPriceTag = soup.find('ul', class_='srp-results srp-list clearfix').find('span', class_='s-item__price')
    if productPriceTag is not None:
        productPrice = productPriceTag.text
        heading = soup.find_all('div', class_='s-item__title')[1].find('span', role='heading').text
        if search.split()[-1] not in heading:
            productPrice = None
    else:
        productPrice = None
    return productPrice

def thirdColumn(search):
    newSearch = '+'.join(search.split())
    url = f'https://www.ebay.com/sch/i.html?_from=R40&_nkw={newSearch}&LH_ItemCondition=1000&LH_BIN=1&_sop=15'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    productPriceTag = soup.find('ul', class_='srp-results srp-list clearfix').find('span', class_='s-item__price')
    if productPriceTag is not None:
        productPrice = productPriceTag.text
        heading = soup.find_all('div', class_='s-item__title')[1].find('span', role='heading').text
        if search.split()[-1] not in heading:
            productPrice = None
    else:
        productPrice = None
    return productPrice


@app.route('/api/get_data', methods=['GET'])
def get_data():
    modelNumber = request.args.get('modelNumber')

    partSelectURL = 'https://www.partselect.com/Models/{}/'.format(modelNumber)
    response = requests.get(partSelectURL)
    soup = BeautifulSoup(response.content, 'html.parser')
    appliance = soup.find('h1').text.split(modelNumber)[-1].split()[0]

    searches = []
    partDivElements = soup.find('div', class_='row mt-3 align-items-stretch').find_all('div', class_='col-md-6 mb-3')
    for part in partDivElements[:2]:
        modelEle = part.find('div', class_='mb-1')
        manufacturerNum = modelEle.get_text(strip=True).split(':')[-1].strip()
        search = appliance + ' ' + manufacturerNum
        searches.append(search)

    data = []
    for search in searches[:1]:
        di = {}
        first = firstColumn(search)
        second = secondColumn(search)
        third = thirdColumn(search)

        di['search'] = search
        di['firstColumn'] = first
        di['secondColumn'] = second
        di['thirdColumn'] = third
        print(di)
        data.append(di)

    return jsonify(data)

@app.route('/')
def index():
    return render_template('index.html')
