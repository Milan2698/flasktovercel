from flask import Flask
# import requests
# from bs4 import BeautifulSoup


app = Flask(__name__)
app.secret_key = 'secret_key'





@app.route('/')
def index():
    return 'Hello vercel'
    # , methods=['GET', 'POST']
    # if request.method == 'POST':
    #     model_number = request.form['modelNumber']
    #     result_data = findPrice(model_number)
    #     return render_template('index.html', result=result_data)

    # return render_template('index.html', result=None)

# if __name__ == '__main__':
#     app.run()