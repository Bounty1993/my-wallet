[![Build Status](https://travis-ci.org/Bounty1993/my-wallet.svg?branch=master)](https://travis-ci.org/Bounty1993/my-wallet)
[![Coverage Status](https://coveralls.io/repos/github/Bounty1993/my-wallet/badge.svg?branch=master)](https://coveralls.io/github/Bounty1993/my-wallet?branch=master)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

# my-wallet website

My Wallet is a website where users can create different portfolios to test investing strategies. It possible to buy and sell American stocks virtually. Additionally the users can find current share prices of US companies and ETF-s. Moreover My Wallet offers access to current financial data and market indicators.
The purpose is to create the place where you can find most essentials tools for stock market analysis.

Technology Stack:

* Python 3.7
* Django Web Framework
* Django Rest Framework
* PostgreSQL
* Redis 3.2
* Celery
* Docker
* Twitter Bootstrap 4
* jQuery 3

### Installation

My Wallet uses Redis and Postgresql so the best way to get it running is to use Docker. Below you can find instruction.

```
$ mkdir my_wallet
$ cd my_wallet
$ git clone https://github.com/Bounty1993/my-wallet.git
$ cd my_wallet
```
Use Docker to build image and run containers:

```
$ docker-compose build
$ docker-compose run web python manage.py migrate --noinput
$ docker-compose up
```

Now it should work. Check it out:

```
http://localhost:8000/
```

If you want to see any data you can load it. Unfortunately there will be no current prices(See EXTERNAL API KEYS ):
```
$ docker-compose run web python manage.py loaddata db.json
```

### OAuth 
My Wallet can use OAuth. Currently only Facebook and Google+ are available. If you want to use them you have to provide API token for Facebook(SOCIAL_AUTH_FACEBOOK_KEY and SOCIAL_AUTH_FACEBOOK_SECRET) or Google+ (SOCIAL_AUTH_GOOGLE_OAUTH2_KEY and SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET). From then everything should work. To get more information visit [social-auth-app-django](https://python-social-auth-docs.readthedocs.io/en/latest/configuration/django.html)

### Mail
If you wan to use email notifications please set all necessary environment variables. You can do that in setting.py or in example.env.

### External API KEYS

My Wallet uses [IEX Cloud API](https://iexcloud.io/) to get data and current stock prices. It is required to provide IEX_API_KEY in config.settings.py if you want to see current prices and make virtual transactions. Currently IEX Cloud is free up to 500 000 credits per month.



