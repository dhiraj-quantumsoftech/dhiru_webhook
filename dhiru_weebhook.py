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

@app.route('/dhiru_post', methods=['GET'])
def dhiru_post():
  url = "https://www.nayaindia.com/api_new/"
  payload = {
        "number": 12524,
        "api_type": "news_listing",
        "slug": "life-mantra",
        "start": 0,
        "end": 10
    }
  response = requests.post(url, data=payload)
  return jsonify(response.json())

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

