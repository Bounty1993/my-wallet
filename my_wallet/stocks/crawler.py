import re
from config.settings import IEX_API_KEY
from abc import ABC, abstractmethod
from json.decoder import JSONDecodeError
import requests
from bs4 import BeautifulSoup


class BaseIEX(ABC):

    def __init__(self, ticker):
        self.url = self.get_url(ticker)

    @abstractmethod
    def get_url(self, ticker):
        pass

    def get_data(self):
        response = requests.get(self.url)
        try:
            data = response.json()
        except JSONDecodeError:
            raise ValueError('Something is wrong with request')
        return data


class QuotesIEX(BaseIEX):
    def get_url(self, ticker):
        return f'https://cloud.iexapis.com/stable/stock/{ticker}/book?token={IEX_API_KEY}'

    def get_data(self):
        data = super().get_data()
        return data.get('quote', '')


class CompanyIEX(BaseIEX):
    def get_url(self, ticker):
        return f'https://cloud.iexapis.com/stable/stock/{ticker}/company?token={IEX_API_KEY}'


class PastIEX(BaseIEX):
    def get_url(self, ticker, num=5):
        return f'https://cloud.iexapis.com/stable/stock/{ticker}/chart/{num}y?token={IEX_API_KEY}'


class DividendsIEX(BaseIEX):
    def get_url(self, ticker, num=5):
        return f'https://cloud.iexapis.com/stable/stock/{ticker}/dividends/{num}y?token={IEX_API_KEY}'


class FinancialIEX(BaseIEX):
    def get_url(self, ticker):
        return f'https://cloud.iexapis.com/stable/stock/{ticker}/financials/4?token={IEX_API_KEY}'

    def get_data(self):
        data = super().get_data()
        return data.get('financials', '')


class BaseCrawler(ABC): # pragma: no cover

    def get_soup(self):
        url = self.url.format(self.formats)
        response = requests.get(url)
        if response.status_code != 200:
            return None
        c = response.content
        soup = BeautifulSoup(c, 'lxml')
        return soup

    @abstractmethod
    def get_news(self, soup):
        pass

    @abstractmethod
    def article_text(self, article):
        pass

    def get_articles(self, news):
        articles = {}
        for i, article in enumerate(news, start=1):
            title, link, summary = self.article_text(article)
            data = {
                'title': title,
                'link': link,
                'summary': summary
            }
            articles[i] = data
        return articles

    def get_data(self):
        soup = self.get_soup()
        news = self.get_news(soup)
        articles = self.get_articles(news)
        return articles


class GoogleCrawler(BaseCrawler):   # pragma: no cover

    def __init__(self, ticker):
        self.ticker = ticker
        self.formats = self.ticker

    url = 'https://www.google.com/search?q=NASDAQ:{}&tbm=nws'

    def get_news(self, soup):
        return soup.find_all('div', 'g')

    def article_text(self, article):
        title = article.h3.text
        link = article.h3.a.get('href')[7:]
        summary = article.find('div', 'st').text
        return title, link, summary


class YahooCrawler(BaseCrawler):    # pragma: no cover

    def __init__(self, ticker):
        self.formats = ticker

    url = 'https://finance.yahoo.com/quote/{}'

    def get_news(self, soup):
        return soup.find('ul', 'My(0) Ov(h) P(0) Wow(bw)')

    def article_text(self, article):
        title = article.h3.text
        link = article.h3.a.get('href')
        link = 'https://finance.yahoo.com/' + link
        summary = article.p.text
        return title, link, summary
