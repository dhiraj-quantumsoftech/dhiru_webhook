from __future__ import print_function

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

# THIS IS ADDED
import requests

import json
import os

from flask import jsonify
from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


# -------------------- My Test -----------------

@app.route('/dhiru_post', methods=['POST'])
def dhiru_post():
    req = request.get_json(silent=True, force=True)
    url = "https://www.nayaindia.com/api_new"
    result = req.get("queryResult")

    parameters = result.get("parameters")

    # payload = { "api_type": "news_listing",
    #     "slug": "life-mantra",
    #     "start": 0,
    #     "end": 10
    # }

    response = requests.post(url, data=json.dumps(parameters))

    response_json = jsonify(response.json())

    response_dic = json.loads(json.dumps(response.json()))

    print(response_dic['message'])

    cardList = []

    news_arry = response_dic['data']['news_list']

    my_result = makeFulfilmentNewsList(news_arry)

    res = json.dumps(my_result, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


# def processDhiruRequest(req):

#     baseurl = 'https://www.nayaindia.com/api_new/'

#     parameters =   {
#    "api_type":"news_listing",
#     "slug":"life-mantra",
#     "start":0,
#          "length":12 }

#     response = requests.post(
#             baseurl, data=json.dumps(parameters),
#             headers={'Content-Type': 'application/json'}
#         )
#         return response.content

# -----------------------------------------------------


def makeFulfilmentNewsList(news_arry):

    fulfillmentMessages = []

    for dic in news_arry:
       # print(dic)
        attachment_url =  dic['attachment_url']
        news_slug = dic['news_slug']
        news_title = dic['news_title']
        small_summary = dic['small_summary']

        post_url = "https://www.nayaindia.com/"

        card = {
            "title": news_title,
            "subtitle": small_summary,
            "imageUri": attachment_url,
            "buttons": [{
                "text": "Read more",
                "postback": post_url
            },
                {
                "text": "Explore more",
                "postback": post_url
            }
            ]
        }

        #platform = "FACEBOOK"

        news_dic_main = {
            "card":card,
            "platform":platform
        }

        fulfillmentMessages.append(news_dic_main)
        break

    my_result = {"fulfillmentText": "Here is the news i found for you, thanks for using QuantomSoftech AI",
                 "fulfillmentMessages":fulfillmentMessages}
    print(my_result)

    return  my_result



@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    res = processRequest(req)

    res = json.dumps(res, indent=4)

    r = make_response(res)

    r.headers['Content-Type'] = 'application/json'

    return r


def processRequest(req):
    #    if req.get("queryResult").get("action") != "rate":
    #        print("Please check your action name in DialogFlow...")
    #        return {}

    result = req.get("queryResult")
    parameters = result.get("parameters")

    print(parameters['currency-name1'])
    currency1 = parameters['currency-name']
    currency2 = parameters['currency-name1']
    baseurl = 'https://api.exchangeratesapi.io/latest?base=' + currency1 + '&symbols=' + currency2;

    if baseurl is None:
        return {}

    result = urlopen(baseurl).read()
    data = json.loads(result)
    # for some the line above gives an error and hence decoding to utf-8 might help
    # data = json.loads(result.decode('utf-8'))
    res = makeWebhookResult(data, currency2)
    return res


def makeWebhookResult(data, currency2):
    query = data.get('rates')

    if query is None:
        return {}
    result = query.get(currency2)
    if result is None:
        return {}

    speech = "The exchange rate is  " + str(result)

    # Naresh
    return {

        "fulfillmentText": speech,
        "source": "Dhiru Web hook API"
    }


@app.route('/test', methods=['GET'])
def test():
    return "Hello there my friend !!"


@app.route('/webhook_dhiru', methods=['POST'])
def static_reply():
    speech = "Hello there,  this reply is from the webhook !! "
    string = "Hi There how are you !! Webhook by Dhiraj"
    Message = "GOOGLE"

    my_result = {"fulfillmentText": "This is a text response",
                 "fulfillmentMessages":
                     [{"card":
                         {
                             "title": "card title", "subtitle": "card text",
                             "imageUri": "https://assistant.google.com/static/images/molecule/Molecule-Formation-stop.png",
                             "buttons": [{
                                 "text": "button text",
                                 "postback": "https://assistant.google.com/"}
                             ]
                         },
                        "platform": "FACEBOOK"
                     }
                     ]
                 }

    res = json.dumps(my_result, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')

