#!/usr/bin/env python
import urllib
import json
import os
from datetime import datetime, date

from flask import Flask, request, make_response

app = Flask(__name__)

cashBalance = '3.12M'

deficitAmount = '42K'

cashBalanceForecast = {
	'1' : '1.11M',
	'2' : '2.11M',
	'3' : '3.11M',
	'4' : '4.11M',
	'5' : '5.11M'
}

amountofTransactions = {
	     'unreconciled bank transactions': '0',
	     'unreconciled system transactions': '28.3K'
	}

numberofTransactions = {
	     'unreconciled bank transactions': 0,
	     'unreconciled system transactions': 52
	}


numberOfAccounts = {
	     'deficit': 2,
	     'missing statements': 11
	}

riksyAccountDetails = [
	{
	     'accountGroup': 'BofA-204',
	     'current': '0',
	     'target': '25K',
	     'deficit': '25K'
	},
	{
	     'accountGroup': 'AP BofA - USD',
	     'current': '13K',
	     'target': '30K',
	     'deficit': '17K'
	}
]

riksyAccountRank = {
	'1' : 'BofA-204',
	'2' : 'AP BofA - USD' 
}

deficitAccountList = ['BofA-204','AP BofA - USD']

missingStatementsAccountList = [ 'Mutaties', 'CE AR BofA - USD', 'QAForeign', 'CE ForecastAccount-EUR-1', 'CE AR BofA - CAD', '1. DB Girokonto Euro-911', 
								 'JPYAccount', 'CE AR Exceptions', 'CE AP BofA - USD', 'CE AP BofA - CAD','AP BofA - USD']


@app.route("/webhook",methods=['POST'])
def webhook():
	req = request.get_json(silent=True, force=True)

	print("Request:")
	print(json.dumps(req,indent=4))

	res = makeWebhookResult(req)

	res = json.dumps(res, indent=4)

	r = make_response(res)
	r.headers['Content-Type'] = 'application/json'
	return r

def makeWebhookResult(req):

	result = req.get("result")
	action = result.get("action")

	if action == "query.cash.balance":
		speech = "The cash balance is " + cashBalance + "."
		return {
	        "speech": speech,
	        "displayText": speech,
	        "source": "api-ai-cash-managemet"
		}

	elif action == "query.total.amount":
		speech = "The total deficit amount is " + deficitAmount + "."
		return {
	        "speech": speech,
	        "displayText": speech,
	        "source": "api-ai-cash-managemet"
		}

	elif action == "query.transactions.number":

		parameters = result.get("parameters")
		transactionType = parameters.get("transactionType")

		speech = "The total number of " + transactionType + " is " + str(numberofTransactions[transactionType]) + "."
		return {
	        "speech": speech,
	        "displayText": speech,
	        "source": "api-ai-cash-managemet"
		}

	elif action == "query.transactions.amount":

		parameters = result.get("parameters")
		transactionType = parameters.get("transactionType")

		speech = "The total amount of " + transactionType + " is " + str(amountofTransactions[transactionType]) + "."
		return {
	        "speech": speech,
	        "displayText": speech,
	        "source": "api-ai-cash-managemet"
		}

	elif action == "query.total.number":

		parameters = result.get("parameters")
		account_type = parameters.get("account_type")

		speech = "The total number of " + account_type + " accounts is " + str(numberOfAccounts[account_type]) + "."
		return {
	        "speech": speech,
	        "displayText": speech,
	        "source": "api-ai-cash-managemet"
		}

	elif action == "query.account.list":

		parameters = result.get("parameters")
		account_type = parameters.get("account_type")
		if account_type == "deficit":
			speech = "The list of " + account_type + " accounts: " + str(deficitAccountList)
		elif account_type == "missing statements":
			speech = "The list of " + account_type + " accounts: " + str(missingStatementsAccountList)
		else:
			speech = "No such type of account"
		return {
	        "speech": speech,
	        "displayText": speech,
	        "source": "api-ai-cash-managemet"
		}

	elif action == "query.account.balance":

		parameters = result.get("parameters")
		account_group = parameters.get("account_group")
		balance_type = parameters.get("balance_type")
		print (balance_type)
		speech = "No such account group or balance type"

		if balance_type[0] == "current":
			for account in riksyAccountDetails:
				if account["accountGroup"] == account_group[0]:
					speech = "The " + balance_type[0]+ " balance of account " + account_group[0] + " is " + account["current"] + "."
		elif balance_type[0] == "target":
			for account in riksyAccountDetails:
				if account["accountGroup"] == account_group[0]:
					speech = "The " + balance_type[0] + " balance of account " + account_group[0] + " is " + account["target"] + "."
		elif balance_type[0] == "deficit":
			for account in riksyAccountDetails:
				if account["accountGroup"] == account_group[0]:
					speech = "The " + balance_type[0] + " amount of account " + account_group[0] + " is " + account["deficit"] + "."
		return {
	        "speech": speech,
	        "displayText": speech,
	        "source": "api-ai-cash-managemet"
		}

	elif action == "query.account.name":

		parameters = result.get("parameters")
		rank = parameters.get("rank").get("rank")

		if int(rank) > len(riksyAccountRank):
			speech = "The rank you requested is largest than the size of deficit list"
		elif int(rank) <= 0:
			speech = "The requested rank is invalid"
		else:
			account_group = riksyAccountRank[rank]
			speech = "The account group you requested from the deficit list is " + account_group + "."

		return {
	        "speech": speech,
	        "displayText": speech,
	        "source": "api-ai-cash-managemet"
		}
	elif action == "query.account.forecast":

		parameters = result.get("parameters")
		targetDate = datetime.strptime(parameters.get("date"), '%Y-%m-%d').date()
		currentDate = date.today()
		diff = (targetDate - currentDate).days
		if diff >=1 & diff <=5:
			speech = "The cash balance forecast on " + str(targetDate) + " is " + cashBalanceForecast[str(diff)] + "."
		else:
			speech = "The date you requested should be from tomorrow to the next 5 days"
		return {
	        "speech": speech,
	        "displayText": speech,
	        "source": "api-ai-cash-managemet"
		}

	else:
		return {}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
