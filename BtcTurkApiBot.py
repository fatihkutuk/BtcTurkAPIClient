import time, base64, hmac, hashlib, requests, json
import math
import mysql.connector
from mysql.connector import (connection)
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import LastExchanges

import sys
avg = LastExchanges.get_last_exchange()
comission = 0.0018

def mysql_connect():
    con = connection.MySQLConnection(user='root', password='',
                                host='localhost',
                                database='btc')
    return con

def insert_exchange(market_tip,price,date):
    con = mysql_connect()
    cursor = con.cursor()
    add_exchange = ("INSERT INTO  exchanges"
               "(market_tip, price, date) "
               "VALUES (%s, %s, %s)")
    data_exchange = (market_tip, price,date)
    cursor.execute(add_exchange, data_exchange)
    con.commit()
    cursor.close()
    con.close()

def insert_operations(order_type,coin_type,order_method,quantaty,value,price,date):
    con = mysql_connect()
    cursor = con.cursor()
    add_operation = ("INSERT INTO  operations"
               "(order_type, coin_type, order_method,quantity,value,price,date) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s)")
    data_operation = (order_type,coin_type,order_method,quantaty,value,price,date)
    cursor.execute(add_operation, data_operation)
    con.commit()
    cursor.close()
    con.close()               
   
def get_last_operation():
    con = mysql_connect()
    cursor = con.cursor()
    query = ("SELECT * FROM operations  order by id desc limit 1")   
    cursor.execute(query) 
    result = cursor.fetchall()
    for x in result:
        return x
    con.commit()
    cursor.close()
    con.close()   

#Mail Gönder
def send_mail(subject,body,mail):
    message= MIMEMultipart()   
    message["From"] = "Your Email Adress" 
    message["To"] = mail   
    message["Subject"] = subject 
    body= body
    body_text = MIMEText(body,"plain") 
    message.attach(body_text)    
    try:
        mail = smtplib.SMTP("Your Email Host",587)  
        mail.ehlo()
        mail.starttls()    
        mail.login("Your Email Adress","Your Email Password")
        mail.sendmail(message["From"],message["To"],message.as_string())
        print("Mail ",mail," Adresine Basarili bir sekilde gonderildi.")
        mail.close()
    except:
        sys.stderr.write("Bir hata olustu. Tekrar deneyin...")
        sys.stderr.flush()   
#Alım yada satım için apiye istekte bulunur : Type -> buy, sell. quantity-> 0-xxx, market_code-> coin market kodu örn: USDT_TRY.
def make_order(type,quantity,market_code):
    base = "https://api.btcturk.com"
    method = "/api/v1/order"
    uri = base+method
    apiKey = "Your Public Key"
    apiSecret = "Your Secret Key"
    apiSecret = base64.b64decode(apiSecret)
    stamp = str(int(time.time())*1000)
    data = "{}{}".format(apiKey, stamp).encode("utf-8")
    signature = hmac.new(apiSecret, data, hashlib.sha256).digest()
    signature = base64.b64encode(signature)
    headers = {"X-PCK": apiKey, "X-Stamp": stamp, "X-Signature": signature, "Content-Type" : "application/json"}
    params={"quantity": quantity,"newOrderClientId":"BtcTurk Python API Test", "orderMethod":"market", "orderType":type, "pairSymbol":market_code}
    result = requests.post(url=uri, headers=headers, json=params)
    result = result.json()
    print(json.dumps(result, indent=2))
    if type=="sell":
      send_mail("'"+market_code+"' Piyasa Bilgilendirme","'"+market_code+"' Satildi, yeni TL = "+try_info(),"fatihkutuk@outlook.com")
    if type=="buy":
      send_mail("'"+market_code+"' Piyasa Bilgilendirme","'"+market_code+"' Alındı, yeni USDT = "+coin_info(13),"fatihkutuk@outlook.com")


#Coinler için market bilgileri getirir
def coin_market_info(market_code,info):
    base = "https://api.btcturk.com"
    method = "/api/v2/ticker?pairSymbol="+market_code
    uri = base+method
    result = requests.get(url=uri)
    result = result.json()
    return result['data'][0][info]
#Coinler için son alış veya satış işlemi bilgilerinizi getirir. İstediğiniz Bigiyi dönderir. Örn: trade_info("USDT","buy","amount")). Amount = Hacim, price=aldığınız kur değeri
def trade_info(trade_code,order_type,info):
    base = "https://api.btcturk.com"
    method = "/api/v1/users/transactions/trade?symbol="+trade_code+"&type="+order_type+""
    uri = base+method

    apiKey = "Your Public Key"
    apiSecret = "Your Secret Key"
    apiSecret = base64.b64decode(apiSecret)

    stamp = str(int(time.time())*1000)
    data = "{}{}".format(apiKey, stamp).encode("utf-8")
    signature = hmac.new(apiSecret, data, hashlib.sha256).digest()
    signature = base64.b64encode(signature)
    headers = {"X-PCK": apiKey, "X-Stamp": stamp, "X-Signature": signature, "Content-Type" : "application/json"}

    result = requests.get(url=uri, headers=headers)
    result = result.json()    

    return result['data'][0][info]
#hesabınızdaki Türk lirasi miktarını getirir    
def try_info():
    base = "https://api.btcturk.com"
    method = "/api/v1/users/balances"
    uri = base+method

    apiKey = "Your Public Key"
    apiSecret = "Your Secret Key"
    apiSecret = base64.b64decode(apiSecret)

    stamp = str(int(time.time())*1000)
    data = "{}{}".format(apiKey, stamp).encode("utf-8")
    signature = hmac.new(apiSecret, data, hashlib.sha256).digest()
    signature = base64.b64encode(signature)
    headers = {"X-PCK": apiKey, "X-Stamp": stamp, "X-Signature": signature, "Content-Type" : "application/json"}

    result = requests.get(url=uri, headers=headers)
    result = result.json()
    return result['data'][0]['free']
#Hesaptaki USDT miktarını verir
def coin_info(code):
    base = "https://api.btcturk.com"
    method = "/api/v1/users/balances"
    uri = base+method

    apiKey = "Your Public Key"
    apiSecret = "Your Secret Key"
    apiSecret = base64.b64decode(apiSecret)

    stamp = str(int(time.time())*1000)
    data = "{}{}".format(apiKey, stamp).encode("utf-8")
    signature = hmac.new(apiSecret, data, hashlib.sha256).digest()
    signature = base64.b64encode(signature)
    headers = {"X-PCK": apiKey, "X-Stamp": stamp, "X-Signature": signature, "Content-Type" : "application/json"}

    result = requests.get(url=uri, headers=headers)
    result = result.json()
    return result['data'][code]['free']
#Yapılan Son İşlem
def coin_ochl():
    base = "https://graph-api.btcturk.com"
    method = "/v1/ohlcs?pair=USDT_TRY&from="+ datetime.timedelta(-1) +"&to="+datetime.date.today()
    uri = base+method

    result = requests.get(url=uri)
    result = result.json()
    return result

def last_trade(market_code):
    base = "https://api.btcturk.com"
    method = "/api/v1/allOrders?pairSymbol="+market_code
    uri = base+method

    apiKey = "Your Public Key"
    apiSecret = "Your Secret Key"
    apiSecret = base64.b64decode(apiSecret)

    stamp = str(int(time.time())*1000)
    data = "{}{}".format(apiKey, stamp).encode("utf-8")
    signature = hmac.new(apiSecret, data, hashlib.sha256).digest()
    signature = base64.b64encode(signature)
    headers = {"X-PCK": apiKey, "X-Stamp": stamp, "X-Signature": signature, "Content-Type" : "application/json"}

    result = requests.get(url=uri, headers=headers)
    result = result.json()
    return result['data'][0]
#Alış işleminiz için şartlar uygun mu kontrol eder true yada false çevirir


def desicion_to_buy(market_code,trade_code,factor):
    ortalama_orani = coin_market_info(market_code,"last")/avg

    last_user_trade = last_trade(market_code)
    last_quantity = last_user_trade['quantity']
    try_count = try_info()
    coin_market_now = coin_market_info(market_code,"last")
    potantiel_coin = float(try_count)/float(coin_market_now)*(1-float(comission))
    target_coin= float(last_quantity)*float(factor)

    if last_user_trade['type']=="sell":
        if potantiel_coin >= target_coin and ortalama_orani < 0.95:
            return True
        else:
            print("------------------- '"+market_code+"' ALIS ---------------------")
            print("Kosullar Alis icin Uygun Degil, Bekleniyor.")
            print("Son Satis = ",last_quantity)
            print("Hedef Alim = ",(target_coin)) 
            print("Anlik Potansiyel Alim = ",potantiel_coin)
            print("Güncel = ",market_code," = ",coin_market_info(market_code,"last"))
            print("En Yüksek ",market_code," = ",coin_market_info(market_code,"high"))
            print("En Düşük ",market_code," = ",coin_market_info(market_code,"low"))
            print("Ortalama ",market_code," = ",avg)
            print("Ortalamanın güncel fiyata oranı = ",ortalama_orani)

            return 11         
    else:
        return False
#Satış işlemi uygun mu kontrol eder
def desicion_to_sell(market_code,trade_code,factor):
    ortalama_orani = coin_market_info(market_code,"last")/avg

    last_user_trade = last_trade(market_code)
    last_quantity = float(last_user_trade['amount'])*float(last_user_trade['price'])/float(1-comission)
    USDT_count = coin_info(13)#13 USDT için, diğerleri için api dökümantosyonuna bakın
    coin_market_now = coin_market_info(market_code,"last")
    potantiel_try = float(USDT_count)*float(coin_market_now)*(1-float(comission))
    target_coin= float(last_quantity)*float(factor)
    if last_user_trade['type'] == "buy":
        if potantiel_try > target_coin and ortalama_orani > 1.05 :
            return True
        else:
            print("------------------- '"+market_code+"' SATIS ---------------------")
            print("Kosullar Satis icin Uygun Degil, Bekleniyor.")
            print("Son Alis = ",last_quantity)
            print("Hedef Satis = ",(target_coin)) 
            print("Anlik Potansiyel Satis = ",potantiel_try)
            print("Güncel = ",market_code," = ",coin_market_info(market_code,"last"))
            print("En Yüksek ",market_code," = ",coin_market_info(market_code,"high"))
            print("En Düşük ",market_code," = ",coin_market_info(market_code,"low"))
            print("Ortalama ",market_code," = ",avg)
            print("Ortalamanın güncel fiyata oranı = ",ortalama_orani)
            return 11                     
    else:
        return False

#Satış veya Alış İşlemi Yapar
def buy_or_sell(market_code,trade_code,factor):
    last_user_trade = last_trade(market_code)
    if last_user_trade['type'] == 'buy':
        sell = desicion_to_sell(market_code,trade_code,factor)
        if sell == True:

            make_order("sell",round(float(coin_info(13))-float(0.01),2),market_code)
            insert_operations('sell',market_code,'market',last_user_trade['amount'],float(coin_market_info(market_code,"last")),float(try_info()),time.strftime('%Y-%m-%d %H:%M:%S'))                      
        else:
            return False    
    elif last_user_trade['type'] == 'sell':
        buy = desicion_to_buy(market_code,trade_code,factor)
        if buy == True:

            make_order("buy",round(float(try_info())-float(0.01),2),market_code)
            insert_operations('buy',market_code,'market',last_user_trade['amount'],float(coin_market_info(market_code,"last")),float(try_info()),time.strftime('%Y-%m-%d %H:%M:%S'))                      
        else:
            return False

while 1 :
    try:
        buy_or_sell("USDT_TRY","USDT",1.01)
        insert_exchange("USDT_TRY",coin_market_info("USDT_TRY","last"),time.strftime('%Y-%m-%d %H:%M:%S'))
        time.sleep(1)
    except Exception as identifier:
        send_mail("Bot Hataya Dustu !","Bot Hataya Dustu Kontrol edin","fatihkutuk@outlook.com")
        time.sleep(1)
