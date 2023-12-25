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


@app.route('/')
def index():
    # response = requests.get('https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2334524.m570.l1313&_nkw=Refrigerator+Door+Shelf+Retainer+Bin')
    # a = response.content
    return render_template('index.html')
    # , methods=['GET', 'POST']
    # if request.method == 'POST':
    #     model_number = request.form['modelNumber']
    #     result_data = findPrice(model_number)
    #     return render_template('index.html', result=result_data)

    # return render_template('index.html', result=None)

# if __name__ == '__main__':
#     app.run()