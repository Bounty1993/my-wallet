# my-wallet website

My Wallet jest stroną na której użytkownik może zapoznać się z bieżącymi kursami giełdowymi spółek amerykańskich oraz ETF-ów. Ponadto widoczne są dane finasowy, przeszłe kursy oraz najnowsze informacje prasowe. Możliwe jest także stworzenie własnej kompozycji spółek i śledzenia ich wyników.

**Projekt nie jest skończony**

Użyte technologie:
* Python: 3.7x
* Django Web Framework: 2.2
* PostgreSQL
* Redis 3.2
* Celery
* Docker
* Twitter Bootstrap 4
* jQuery 3

##Instrukcja uruchomienia

###Docker
Najlepszy sposób to użycie dockera. Docker pozwala uruchomić stronę bez konieczności instalowania PostgreSQL oraz Redisa

```
$ mkdir my_wallet
$ git clone adres
$ cd my_wallet
```
Następnie należy za pomocą dockera uruchomić stronę. 
```
$ docker-compose build
$ docker-compose up
```
Adres strony:
```
https://localhost:8000
```

###Virtaul environment
```
$ mkdir my_wallet
$ git clone https://github.com/Bounty1993/my-wallet.git
$ cd my_wallet
```
Instalacja virtual environment:
```
$ pip intall virtualenv
$ virtualenv venv
$ source venv/bin/activate
```
Następnie należy zainstalować biblioteki Django oraz Pythona:
```
$ pip install -r requirements/dev.txt
```
Na końcu konieczne jeszcze jest skonfigurowanie lub zainstalowanie PostgreSQL, Redis oraz Celery.

Adres strony:
```
https://localhost:8000
```

### Źródła
Zdjęcia pobrane z strony unsplash.com. Poniżej linki do wszystkich:
* https://unsplash.com/photos/JrtlTputiWw
* https://unsplash.com/photos/uJhgEXPqSPk
* https://unsplash.com/photos/FumjLlfuvhg

Dane giełdowe pobierane są z API dostaracznego przez IEX. Link do strony: 
* https://iextrading.com/developer/docs/.

Część danych (raporty roczne) nie są aktualne. Do bieżących danych można uzyskać dostęp zakładając konto pod linkiem: https://iexcloud.io/cloud-login#/register/ i uzyskując klucz API. 




