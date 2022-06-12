import pathlib
from datetime import datetime 

import requests
import urllib.request
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

import re
import io
import os
import time

import smtplib
import imghdr
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from selenium import webdriver 
from selenium.webdriver import Edge

__author__ = 'srv'

today = datetime.now().date()

contacts = ['You'] #Add more recipients here

username = os.environ.get('EMAIL_USER') 
password = os.environ.get('EMAIL_PASS')
server = smtplib.SMTP('smtp.office365.com', 587)
number = 0

urlbuff = 'https://news.google.com/'

metal_symbols = ['XAU', 'XPT', 'XAG', 'XPD']
metal_words = ['Gold', 'gold', 'GOLD', 'Silver', 'silver', 'SILVER', 'Platinum', 'platinum', 'PLATINUM', 'Palladium', 'palladium', 'PALLADIUM', 'Rhodium', 'rhodium', 'RHODIUM']

for contact in contacts:
  subjects_file = open(f"categories/{contact}-categories.txt", "r")
  ls = list(subjects_file)
  news_file = open(f"news/{contact}-news/{today}-news.txt","w+")

  syms = open(f'symbols/{contact}-sym.txt')
  symArray = []

  for i in syms:
    symArray.append(i)

  new_symArray = [x[:-1] for x in symArray]
  isMetal = [e for e in new_symArray if e in metal_words]
  notMetal = [e for e in new_symArray if e not in metal_words]
  print(notMetal)
  print(isMetal)

  def getStockPrice(symbol):
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.53'}
    stock_url = f'https://uk.finance.yahoo.com/quote/{sym}'
    r = requests.get(stock_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    stock = {
    'symbol': symbol,
    'price': soup.find('div', {'class' : 'D(ib) Mend(20px)'}).find_all('span')[0].text,
    'change': soup.find('div', {'class' : 'D(ib) Mend(20px)'}).find_all('span')[1].text,
    }
    return stock
  
  symStockData = []
  for sym in notMetal:
    symStockData.append(getStockPrice(sym))
    print('Getting: ', sym)

  def getMetalPrice(symbol):
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.53'}
    metal_url = f'https://www.bullionbypost.co.uk/{symbol}-price/today/ounces/GBP/'
    response = requests.get(metal_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    metal = {
    'symbol': symbol,
    'price': soup.find('span', {'name' : 'current_price_field'}).text,
    'change': soup.find('span', {'name' : 'change_cell_percentage'}).text,
    }
    return metal

  symMetalData = []
  for sym in isMetal:
    print(sym)
    symMetalData.append(getMetalPrice(sym))
    print('Getting: ', sym)

  def flipMetalColour(thedata):
    negative = '-'
    if negative in thedata:
      colour = 'ff0000'
    else:
      colour = '01DF01'
    
    return colour
  
  def flipStockColour(colour):
    negative = '-'
    if negative in colour:
      colour = 'ff0000'
    else:
      colour = '01DF01'
    
    return colour

  items = []
  for i in ls:
      items.append(i)

  new_items = [x[:-1] for x in items]

  for item in new_items:
      item.strip()
      headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.53'}
      url = f'https://news.google.com/search?q={item}%20when%3A1d&hl=en-GB&gl=GB&ceid=GB%3Aen'
      
      response = requests.get(url)
      driver = webdriver.Edge()
      driver.get(url)
      time.sleep(5)

      agree_button = '/html/body/div[2]/div[3]/form/input[11]'
      agree_button.click()

      soup = BeautifulSoup(response.content, 'html.parser')
      print(soup)
      blocks = soup.find_all('a', attrs = {'class' : 'DY5T1d RZIKme'})
      print(blocks)
      text = soup.find_all('a', {'id': re.compile('^c\d+')})
      print(text)
      sources = soup.find_all('a', attrs = {'class' : 'wEwyrc AVN2gc uQIVzc Sksgp'})
      print(sources)
      storytime = soup.find_all('time', attrs = {'class' : 'WW6dff uQIVzc Sksgp'})
      print(storytime)

      for (oneuse, twouse, threeuse) in zip(blocks, sources, storytime):
          href = oneuse['href']
          headline = str(oneuse.text)
          source = str(twouse.text)
          remove = ['.com', '.COM']
          for value in remove:
            source = source.replace(value, '')
          timeof = str(threeuse.text)

          with io.open(f'news/{contact}-news/{today}-news.txt', "a",  encoding='utf-8-sig') as wf:
              wf.write(f'  <p><u>{item}</u></p>' + '\n')
              wf.write('  ' + headline + '\n\n<br>')
              wf.write(f'  <a href="{urlbuff + href}">Read this story</a><span><b> - {source},</b> {timeof}</span>' + "\n\n\n<br><br>")

      print(f'{item} related stories transferred')

  with io.open(f'news/{contact}-news/{today}-news.txt', "r",   encoding='utf-8-sig') as nwf:
      news_mail = nwf.read()
  
  if contact == 'You':
    try:
      You_tick_left = f"""
                            <p style="text-align: center; line-height: 1.2; word-break: break-word; font-family: 'Bodoni Moda', serif; font-size: 14px; mso-line-height-alt: 17px; margin: 0;">{symStockData[0]['symbol']} : <span style="color: #{flipStockColour(symStockData[0]['change'])};">{symStockData[0]['price']}, {symStockData[0]['change']}</span></p>"""+f"""
                            <p style="text-align: center; line-height: 1.2; word-break: break-word; font-family: 'Bodoni Moda', serif; font-size: 14px; mso-line-height-alt: 17px; margin: 0;">{symStockData[1]['symbol']} : <span style="color: #{flipStockColour(symStockData[1]['change'])};">{symStockData[1]['price']}, {symStockData[1]['change']}</span></p>"""+f"""
                            <p style="text-align: center; line-height: 1.2; word-break: break-word; font-family: 'Bodoni Moda', serif; font-size: 14px; mso-line-height-alt: 17px; margin: 0;">{symStockData[2]['symbol']} : <span style="color: #{flipStockColour(symStockData[2]['change'])};">{symStockData[2]['price']}, {symStockData[2]['change']}</span></p>"""+f"""
                            <p style="text-align: center; line-height: 1.2; word-break: break-word; font-family: 'Bodoni Moda', serif; font-size: 14px; mso-line-height-alt: 17px; margin: 0;">{symStockData[3]['symbol']} : <span style="color: #{flipStockColour(symStockData[3]['change'])};">{symStockData[3]['price']}, {symStockData[3]['change']}</span></p>"""

      You_tick_right = f"""
                            <p style="text-align: center; line-height: 1.2; word-break: break-word; font-family: 'Bodoni Moda', serif; font-size: 14px; mso-line-height-alt: 17px; margin: 0;">XAU : <span style="color: #{flipMetalColour(symMetalData[0]['change'])};">{symMetalData[0]['price']}, ({symMetalData[0]['change']}%)</span></p>"""+f"""
                            <p style="text-align: center; line-height: 1.2; word-break: break-word; font-family: 'Bodoni Moda', serif; font-size: 14px; mso-line-height-alt: 17px; margin: 0;">XAG : <span style="color: #{flipMetalColour(symMetalData[1]['change'])};">{symMetalData[1]['price']}, ({symMetalData[1]['change']}%)</span></p>"""+f"""
                            <p style="text-align: center; line-height: 1.2; word-break: break-word; font-family: 'Bodoni Moda', serif; font-size: 14px; mso-line-height-alt: 17px; margin: 0;">XPT : <span style="color: #{flipMetalColour(symMetalData[2]['change'])};">{symMetalData[2]['price']}, ({symMetalData[2]['change']}%)</span></p>"""+f"""
                            <p style="text-align: center; line-height: 1.2; word-break: break-word; font-family: 'Bodoni Moda', serif; font-size: 14px; mso-line-height-alt: 17px; margin: 0;">XPD : <span style="color: #{flipMetalColour(symMetalData[3]['change'])};">{symMetalData[3]['price']}, ({symMetalData[3]['change']}%)</span></p>"""

      You_stock_butt = f"""
                        <!--[if mso]></td></tr></table><![endif]-->
                        <div class="button-container" align="center" style="padding-top:5px;padding-right:10px;padding-bottom:0px;padding-left:10px;">
                          <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-spacing: 0; border-collapse: collapse; mso-table-lspace:0pt; mso-table-rspace:0pt;"><tr><td style="padding-top: 5px; padding-right: 10px; padding-bottom: 0px; padding-left: 10px" align="center"><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="https://uk.finance.yahoo.com/quote/""" + f'{symStockData[0]["symbol"]}' + """/ " style="height:25.5pt; width:129pt; v-text-anchor:middle;" arcsize="12%" strokeweight="0.75pt" strokecolor="#4bbc92" fillcolor="#4bbc92"><w:anchorlock/><v:textbox inset="0,0,0,0"><center style="color:#ffffff; font-family: 'Bodoni Moda', serif; font-size:16px"><![endif]--><a href="https://uk.finance.yahoo.com/quote/""" + f'{symStockData[0]["symbol"]}' + """/ " target="_blank" style="-webkit-text-size-adjust: none; text-decoration: none; display: inline-block; color: #ffffff; background-color: #4bbc92; border-radius: 4px; -webkit-border-radius: 4px; -moz-border-radius: 4px; width: auto; width: auto; border-top: 1px solid #4bbc92; border-right: 1px solid #4bbc92; border-bottom: 1px solid #4bbc92; border-left: 1px solid #4bbc92; padding-top: 0px; padding-bottom: 0px; font-family: 'Bodoni Moda', serif; text-align: center; mso-border-alt: none; word-break: keep-all;"><span style="padding-left:10px;padding-right:10px;font-size:16px;display:inline-block;letter-spacing:undefined;"><span style="font-size: 16px; line-height: 2; word-break: break-word; font-family: 'Bodoni Moda', serif; mso-line-height-alt: 32px;">Live """ + f'{symStockData[0]["symbol"]}' + """ Charts</span></span></a>
                          <!--[if mso]></center></v:textbox></v:roundrect></td></tr></table><![endif]-->
                        </div>
                        <div class="button-container" align="center" style="padding-top:5px;padding-right:10px;padding-bottom:0px;padding-left:10px;">
                          <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-spacing: 0; border-collapse: collapse; mso-table-lspace:0pt; mso-table-rspace:0pt;"><tr><td style="padding-top: 5px; padding-right: 10px; padding-bottom: 0px; padding-left: 10px" align="center"><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="https://www.tradingview.com/symbols/""" + f'LSE-{symStockData[1]["symbol"]}' + """/ " style="height:25.5pt; width:129pt; v-text-anchor:middle;" arcsize="12%" strokeweight="0.75pt" strokecolor="#4bbc92" fillcolor="#4bbc92"><w:anchorlock/><v:textbox inset="0,0,0,0"><center style="color:#ffffff; font-family: 'Bodoni Moda', serif; font-size:16px"><![endif]--><a href="https://www.tradingview.com/symbols/""" + f'LSE-{symStockData[1]["symbol"]}' + """/ " target="_blank" style="-webkit-text-size-adjust: none; text-decoration: none; display: inline-block; color: #ffffff; background-color: #4bbc92; border-radius: 4px; -webkit-border-radius: 4px; -moz-border-radius: 4px; width: auto; width: auto; border-top: 1px solid #4bbc92; border-right: 1px solid #4bbc92; border-bottom: 1px solid #4bbc92; border-left: 1px solid #4bbc92; padding-top: 0px; padding-bottom: 0px; font-family: 'Bodoni Moda', serif; text-align: center; mso-border-alt: none; word-break: keep-all;"><span style="padding-left:10px;padding-right:10px;font-size:16px;display:inline-block;letter-spacing:undefined;"><span style="font-size: 16px; line-height: 2; word-break: break-word; font-family: 'Bodoni Moda', serif; mso-line-height-alt: 32px;">Live """ + f'{symStockData[1]["symbol"]}' + """ Charts</span></span></a>
                          <!--[if mso]></center></v:textbox></v:roundrect></td></tr></table><![endif]-->
                        </div>
                        <div class="button-container" align="center" style="padding-top:5px;padding-right:10px;padding-bottom:0px;padding-left:10px;">
                          <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-spacing: 0; border-collapse: collapse; mso-table-lspace:0pt; mso-table-rspace:0pt;"><tr><td style="padding-top: 5px; padding-right: 10px; padding-bottom: 0px; padding-left: 10px" align="center"><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="https://www.tradingview.com/symbols/""" + f'LSE-{symStockData[2]["symbol"]}' + """/ " style="height:25.5pt; width:129pt; v-text-anchor:middle;" arcsize="12%" strokeweight="0.75pt" strokecolor="#4bbc92" fillcolor="#4bbc92"><w:anchorlock/><v:textbox inset="0,0,0,0"><center style="color:#ffffff; font-family: 'Bodoni Moda', serif; font-size:16px"><![endif]--><a href="https://www.tradingview.com/symbols/""" + f'{symStockData[2]["symbol"]}' + """/ " target="_blank" style="-webkit-text-size-adjust: none; text-decoration: none; display: inline-block; color: #ffffff; background-color: #4bbc92; border-radius: 4px; -webkit-border-radius: 4px; -moz-border-radius: 4px; width: auto; width: auto; border-top: 1px solid #4bbc92; border-right: 1px solid #4bbc92; border-bottom: 1px solid #4bbc92; border-left: 1px solid #4bbc92; padding-top: 0px; padding-bottom: 0px; font-family: 'Bodoni Moda', serif; text-align: center; mso-border-alt: none; word-break: keep-all;"><span style="padding-left:10px;padding-right:10px;font-size:16px;display:inline-block;letter-spacing:undefined;"><span style="font-size: 16px; line-height: 2; word-break: break-word; font-family: 'Bodoni Moda', serif; mso-line-height-alt: 32px;">Live """ + f'{symStockData[2]["symbol"]}' + """ Charts</span></span></a>
                          <!--[if mso]></center></v:textbox></v:roundrect></td></tr></table><![endif]-->
                        </div>
                        <div class="button-container" align="center" style="padding-top:5px;padding-right:10px;padding-bottom:0px;padding-left:10px;">
                          <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-spacing: 0; border-collapse: collapse; mso-table-lspace:0pt; mso-table-rspace:0pt;"><tr><td style="padding-top: 5px; padding-right: 10px; padding-bottom: 0px; padding-left: 10px" align="center"><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="https://uk.finance.yahoo.com/quote/""" + f'{symStockData[3]["symbol"]}' + """/ " style="height:25.5pt; width:129pt; v-text-anchor:middle;" arcsize="12%" strokeweight="0.75pt" strokecolor="#4bbc92" fillcolor="#4bbc92"><w:anchorlock/><v:textbox inset="0,0,0,0"><center style="color:#ffffff; font-family: 'Bodoni Moda', serif; font-size:16px"><![endif]--><a href="https://uk.finance.yahoo.com/quote/""" + f'{symStockData[3]["symbol"]}' + """/ " target="_blank" style="-webkit-text-size-adjust: none; text-decoration: none; display: inline-block; color: #ffffff; background-color: #4bbc92; border-radius: 4px; -webkit-border-radius: 4px; -moz-border-radius: 4px; width: auto; width: auto; border-top: 1px solid #4bbc92; border-right: 1px solid #4bbc92; border-bottom: 1px solid #4bbc92; border-left: 1px solid #4bbc92; padding-top: 0px; padding-bottom: 0px; font-family: 'Bodoni Moda', serif; text-align: center; mso-border-alt: none; word-break: keep-all;"><span style="padding-left:10px;padding-right:10px;font-size:16px;display:inline-block;letter-spacing:undefined;"><span style="font-size: 16px; line-height: 2; word-break: break-word; font-family: 'Bodoni Moda', serif; mso-line-height-alt: 32px;">Live """ + f'{symStockData[3]["symbol"]}' + """ Charts</span></span></a>
                          <!--[if mso]></center></v:textbox></v:roundrect></td></tr></table><![endif]-->
                        </div>"""

      You_metal_butt = f"""
                        <!--[if mso]></td></tr></table><![endif]-->
                        <div class="button-container" align="center" style="padding-top:5px;padding-right:10px;padding-bottom:0px;padding-left:10px;">
                          <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-spacing: 0; border-collapse: collapse; mso-table-lspace:0pt; mso-table-rspace:0pt;"><tr><td style="padding-top: 5px; padding-right: 10px; padding-bottom: 0px; padding-left: 10px" align="center"><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="https://www.tradingview.com/symbols/XAUGBP" style="height:25.5pt; width:129pt; v-text-anchor:middle;" arcsize="12%" strokeweight="0.75pt" strokecolor="#4bbc92" fillcolor="#4bbc92"><w:anchorlock/><v:textbox inset="0,0,0,0"><center style="color:#ffffff; font-family: 'Bodoni Moda', serif; font-size:16px"><![endif]--><a href="https://www.tradingview.com/symbols/XAUGBP" target="_blank" style="-webkit-text-size-adjust: none; text-decoration: none; display: inline-block; color: #ffffff; background-color: #4bbc92; border-radius: 4px; -webkit-border-radius: 4px; -moz-border-radius: 4px; width: auto; width: auto; border-top: 1px solid #4bbc92; border-right: 1px solid #4bbc92; border-bottom: 1px solid #4bbc92; border-left: 1px solid #4bbc92; padding-top: 0px; padding-bottom: 0px; font-family: 'Bodoni Moda', serif; text-align: center; mso-border-alt: none; word-break: keep-all;"><span style="padding-left:10px;padding-right:10px;font-size:16px;display:inline-block;letter-spacing:undefined;"><span style="font-size: 16px; line-height: 2; word-break: break-word; font-family: 'Bodoni Moda', serif; mso-line-height-alt: 32px;">Live Gold Charts</span></span></a>
                          <!--[if mso]></center></v:textbox></v:roundrect></td></tr></table><![endif]-->
                        </div>
                        <div class="button-container" align="center" style="padding-top:5px;padding-right:10px;padding-bottom:0px;padding-left:10px;">
                          <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-spacing: 0; border-collapse: collapse; mso-table-lspace:0pt; mso-table-rspace:0pt;"><tr><td style="padding-top: 5px; padding-right: 10px; padding-bottom: 0px; padding-left: 10px" align="center"><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="https://www.tradingview.com/symbols/XAGGBP" style="height:25.5pt; width:129pt; v-text-anchor:middle;" arcsize="12%" strokeweight="0.75pt" strokecolor="#4bbc92" fillcolor="#4bbc92"><w:anchorlock/><v:textbox inset="0,0,0,0"><center style="color:#ffffff; font-family: 'Bodoni Moda', serif; font-size:16px"><![endif]--><a href="https://www.tradingview.com/symbols/XAGGBP" target="_blank" style="-webkit-text-size-adjust: none; text-decoration: none; display: inline-block; color: #ffffff; background-color: #4bbc92; border-radius: 4px; -webkit-border-radius: 4px; -moz-border-radius: 4px; width: auto; width: auto; border-top: 1px solid #4bbc92; border-right: 1px solid #4bbc92; border-bottom: 1px solid #4bbc92; border-left: 1px solid #4bbc92; padding-top: 0px; padding-bottom: 0px; font-family: 'Bodoni Moda', serif; text-align: center; mso-border-alt: none; word-break: keep-all;"><span style="padding-left:10px;padding-right:10px;font-size:16px;display:inline-block;letter-spacing:undefined;"><span style="font-size: 16px; line-height: 2; word-break: break-word; font-family: 'Bodoni Moda', serif; mso-line-height-alt: 32px;">Live Silver Charts</span></span></a>
                          <!--[if mso]></center></v:textbox></v:roundrect></td></tr></table><![endif]-->
                        </div>
                        <div class="button-container" align="center" style="padding-top:5px;padding-right:10px;padding-bottom:0px;padding-left:10px;">
                          <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-spacing: 0; border-collapse: collapse; mso-table-lspace:0pt; mso-table-rspace:0pt;"><tr><td style="padding-top: 5px; padding-right: 10px; padding-bottom: 0px; padding-left: 10px" align="center"><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="https://www.tradingview.com/symbols/XPTGBP" style="height:25.5pt; width:129pt; v-text-anchor:middle;" arcsize="12%" strokeweight="0.75pt" strokecolor="#4bbc92" fillcolor="#4bbc92"><w:anchorlock/><v:textbox inset="0,0,0,0"><center style="color:#ffffff; font-family: 'Bodoni Moda', serif; font-size:16px"><![endif]--><a href="https://www.tradingview.com/symbols/XPTGBP" target="_blank" style="-webkit-text-size-adjust: none; text-decoration: none; display: inline-block; color: #ffffff; background-color: #4bbc92; border-radius: 4px; -webkit-border-radius: 4px; -moz-border-radius: 4px; width: auto; width: auto; border-top: 1px solid #4bbc92; border-right: 1px solid #4bbc92; border-bottom: 1px solid #4bbc92; border-left: 1px solid #4bbc92; padding-top: 0px; padding-bottom: 0px; font-family: 'Bodoni Moda', serif; text-align: center; mso-border-alt: none; word-break: keep-all;"><span style="padding-left:10px;padding-right:10px;font-size:16px;display:inline-block;letter-spacing:undefined;"><span style="font-size: 16px; line-height: 2; word-break: break-word; font-family: 'Bodoni Moda', serif; mso-line-height-alt: 32px;">Live Platinum Charts</span></span></a>
                          <!--[if mso]></center></v:textbox></v:roundrect></td></tr></table><![endif]-->
                        </div>
                        <div class="button-container" align="center" style="padding-top:5px;padding-right:10px;padding-bottom:0px;padding-left:10px;">
                          <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-spacing: 0; border-collapse: collapse; mso-table-lspace:0pt; mso-table-rspace:0pt;"><tr><td style="padding-top: 5px; padding-right: 10px; padding-bottom: 0px; padding-left: 10px" align="center"><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="https://www.tradingview.com/symbols/XPDGBP" style="height:25.5pt; width:129pt; v-text-anchor:middle;" arcsize="12%" strokeweight="0.75pt" strokecolor="#4bbc92" fillcolor="#4bbc92"><w:anchorlock/><v:textbox inset="0,0,0,0"><center style="color:#ffffff; font-family: 'Bodoni Moda', serif; font-size:16px"><![endif]--><a href="https://www.tradingview.com/symbols/XPDGBP" target="_blank" style="-webkit-text-size-adjust: none; text-decoration: none; display: inline-block; color: #ffffff; background-color: #4bbc92; border-radius: 4px; -webkit-border-radius: 4px; -moz-border-radius: 4px; width: auto; width: auto; border-top: 1px solid #4bbc92; border-right: 1px solid #4bbc92; border-bottom: 1px solid #4bbc92; border-left: 1px solid #4bbc92; padding-top: 0px; padding-bottom: 0px; font-family: 'Bodoni Moda', serif; text-align: center; mso-border-alt: none; word-break: keep-all;"><span style="padding-left:10px;padding-right:10px;font-size:16px;display:inline-block;letter-spacing:undefined;"><span style="font-size: 16px; line-height: 2; word-break: break-word; font-family: 'Bodoni Moda', serif; mso-line-height-alt: 32px;">Live Palladium Charts</span></span></a>
                          <!--[if mso]></center></v:textbox></v:roundrect></td></tr></table><![endif]-->
                        </div>
    """
    except IndexError:
      pass

  if contact == 'You':
    tl = You_tick_left
    tr = You_tick_right
    sbl = You_stock_butt
    sbr = You_metal_butt
  else:
    print("If you're reading this error, that means I'm dead.")
  
  print(news_mail)

  html = """
  <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
  <html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">

  <head>
    <!--[if gte mso 9]><xml><o:OfficeDocumentSettings><o:AllowPNG/><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml><![endif]-->
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width">
    <!--[if !mso]><!-->
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <!--<![endif]-->
    <title></title>
    <!--[if !mso]><!-->
    <link rel="preconnect" href="https://fonts.gstatic.com">
    <link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda&display=swap" rel="stylesheet">
    <!--<![endif]-->
    <style type="text/css">
      body {
        margin: 0;
        padding: 0;
      }

      table,
      td,
      tr {
        vertical-align: top;
        border-collapse: collapse;
      }

      * {
        line-height: inherit;
      }

      a[x-apple-data-detectors=true] {
        color: inherit !important;
        text-decoration: none !important;
      }
    </style>
    <style type="text/css" id="media-query">
      @media (max-width: 770px) {

        .block-grid,
        .col {
          min-width: 320px !important;
          max-width: 100% !important;
          display: block !important;
        }

        .block-grid {
          width: 100% !important;
        }

        .col {
          width: 100% !important;
        }

        .col_cont {
          margin: 0 auto;
        }

        img.fullwidth,
        img.fullwidthOnMobile {
          max-width: 100% !important;
        }

        .no-stack .col {
          min-width: 0 !important;
          display: table-cell !important;
        }

        .no-stack.two-up .col {
          width: 50% !important;
        }

        .no-stack .col.num2 {
          width: 16.6% !important;
        }

        .no-stack .col.num3 {
          width: 25% !important;
        }

        .no-stack .col.num4 {
          width: 33% !important;
        }

        .no-stack .col.num5 {
          width: 41.6% !important;
        }

        .no-stack .col.num6 {
          width: 50% !important;
        }

        .no-stack .col.num7 {
          width: 58.3% !important;
        }

        .no-stack .col.num8 {
          width: 66.6% !important;
        }

        .no-stack .col.num9 {
          width: 75% !important;
        }

        .no-stack .col.num10 {
          width: 83.3% !important;
        }

        .video-block {
          max-width: none !important;
        }

        .mobile_hide {
          min-height: 0px;
          max-height: 0px;
          max-width: 0px;
          display: none;
          overflow: hidden;
          font-size: 0px;
        }

        .desktop_hide {
          display: block !important;
          max-height: none !important;
        }
      }
    </style>
  </head>

  <body class="clean-body" style="margin: 0; padding: 0; -webkit-text-size-adjust: 100%; background-color: #ffffff;">
    <!--[if IE]><div class="ie-browser"><![endif]-->
    <table class="nl-container" style="table-layout: fixed; vertical-align: top; min-width: 320px; border-spacing: 0; border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #ffffff; width: 100%;" cellpadding="0" cellspacing="0" role="presentation" width="100%" bgcolor="#ffffff" valign="top">
      <tbody>
        <tr style="vertical-align: top;" valign="top">
          <td style="word-break: break-word; vertical-align: top;" valign="top">
            <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td align="center" style="background-color:#ffffff"><![endif]-->
            <div style="background-color:#ffffff;">
              <div class="block-grid " style="min-width: 320px; max-width: 700px; overflow-wrap: break-word; word-wrap: break-word; word-break: break-word; Margin: 0 auto; background-color: #c4c4c4;">
                <div style="border-collapse: collapse;display: table;width: 100%;background-color:#c4c4c4;">
                  <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#ffffff;"><tr><td align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:700px"><tr class="layout-full-width" style="background-color:#c4c4c4"><![endif]-->
                  <!--[if (mso)|(IE)]><td align="center" width="700" style="background-color:#c4c4c4;width:700px; border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent;" valign="top"><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 0px; padding-left: 0px; padding-top:25px; padding-bottom:0px;"><![endif]-->
                  <div class="col num12" style="min-width: 320px; max-width: 700px; display: table-cell; vertical-align: top; width: 700px;">
                    <div class="col_cont" style="width:100% !important;">
                      <!--[if (!mso)&(!IE)]><!-->
                      <div style="border-top:0px solid transparent; border-left:0px solid transparent; border-bottom:0px solid transparent; border-right:0px solid transparent; padding-top:25px; padding-bottom:0px; padding-right: 0px; padding-left: 0px;">
                        <!--<![endif]-->
                        <div class="img-container center autowidth" align="center" style="padding-right: 0px;padding-left: 0px;">
                          <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr style="line-height:0px"><td style="padding-right: 0px;padding-left: 0px;" align="center"><![endif]--><img class="center autowidth" align="center" border="0" src="https://d15k2d11r6t6rl.cloudfront.net/public/users/Integrators/BeeProAgency/629740_611703/1a0f7994-885f-45b4-9710-6318891400be_200x200.png" style="text-decoration: none; -ms-interpolation-mode: bicubic; height: auto; border: 0; width: 100%; max-width: 200px; display: block;" width="200">
                          <!--[if mso]></td></tr></table><![endif]-->
                        </div>
                        <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 25px; padding-left: 25px; padding-top: 25px; padding-bottom: 15px; font-family: 'Bodoni Moda', serif"><![endif]-->
                        <div style="color:#000000;font-family: 'Bodoni Moda', serif;line-height:1.2;padding-top:25px;padding-right:25px;padding-bottom:15px;padding-left:25px;">
                          <div class="txtTinyMce-wrapper" style="line-height: 1.2; font-size: 12px; font-family: 'Bodoni Moda', serif; color: #000000; mso-line-height-alt: 14px;">
                            <p style="font-size: 20px; line-height: 1.2; word-break: break-word; font-family: 'Bodoni Moda', serif; mso-line-height-alt: 24px; margin: 0;"><span style="font-size: 20px;">Good</span><span style="font-size: 20px;"> Morning """ + contact + """,</span></p>
                          </div>
                        </div>
                        <!--[if mso]></td></tr></table><![endif]-->
                        <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 25px; padding-left: 25px; padding-top: 5px; padding-bottom: 20px; font-family: 'Bodoni Moda', serif"><![endif]-->
                        <div style="color:#000000;font-family: 'Bodoni Moda', serif;line-height:1.2;padding-top:5px;padding-right:25px;padding-bottom:20px;padding-left:25px;">
                          <div class="txtTinyMce-wrapper" style="line-height: 1.2; font-size: 12px; font-family: 'Bodoni Moda', serif; color: #000000; mso-line-height-alt: 14px;">
                            <p style="font-size: 16px; line-height: 1.2; word-break: break-word; font-family: 'Bodoni Moda', serif; mso-line-height-alt: 19px; margin: 0;"><span style="font-size: 16px;">Enjoy today's market news.</span></p>
                          </div>
                        </div>
                        <!--[if mso]></td></tr></table><![endif]-->
                        <!--[if (!mso)&(!IE)]><!-->
                      </div>
                      <!--<![endif]-->
                    </div>
                  </div>
                  <!--[if (mso)|(IE)]></td></tr></table><![endif]-->
                  <!--[if (mso)|(IE)]></td></tr></table></td></tr></table><![endif]-->
                </div>
              </div>
            </div>
            <div style="background-color:transparent;">
              <div class="block-grid two-up" style="min-width: 320px; max-width: 700px; overflow-wrap: break-word; word-wrap: break-word; word-break: break-word; Margin: 0 auto; background-color: #c4c4c4;">
                <div style="border-collapse: collapse;display: table;width: 100%;background-color:#c4c4c4;">
                  <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:transparent;"><tr><td align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:700px"><tr class="layout-full-width" style="background-color:#c4c4c4"><![endif]-->
                  <!--[if (mso)|(IE)]><td align="center" width="375" style="background-color:#c4c4c4;width:375px; border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent;" valign="top"><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 0px; padding-left: 0px; padding-top:5px; padding-bottom:0px;"><![endif]-->
                  <div class="col num6" style="display: table-cell; vertical-align: top; max-width: 320px; min-width: 372px; width: 375px;">
                    <div class="col_cont" style="width:100% !important;">
                      <!--[if (!mso)&(!IE)]><!-->
                      <div style="border-top:0px solid transparent; border-left:0px solid transparent; border-bottom:0px solid transparent; border-right:0px solid transparent; padding-top:5px; padding-bottom:0px; padding-right: 0px; padding-left: 0px;">
                        <!--<![endif]-->
                        <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 10px; padding-left: 10px; padding-top: 10px; padding-bottom: 10px; font-family: 'Bodoni Moda', serif"><![endif]-->
                        <div style="font-family: 'Bodoni Moda', serif;line-height:1.2;padding-top:10px;padding-right:10px;padding-bottom:10px;padding-left:10px;">
                          <div class="txtTinyMce-wrapper" style="line-height: 1.2; font-family: 'Bodoni Moda', serif; font-size: 14px; mso-line-height-alt: 14px;">""" + \
                          tl + \
                          """</div>
                        </div>""" + \
                        sbl \
                        + """<!--[if (!mso)&(!IE)]><!-->
                      </div>
                      <!--<![endif]-->
                    </div>
                  </div>
                  <!--[if (mso)|(IE)]></td></tr></table><![endif]-->
                  <!--[if (mso)|(IE)]></td><td align="center" width="375" style="background-color:#c4c4c4;width:375px; border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent;" valign="top"><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 0px; padding-left: 0px; padding-top:5px; padding-bottom:5px;"><![endif]-->
                  <div class="col num6" style="display: table-cell; vertical-align: top; max-width: 320px; min-width: 372px; width: 375px;">
                    <div class="col_cont" style="width:100% !important;">
                      <!--[if (!mso)&(!IE)]><!-->
                      <div style="border-top:0px solid transparent; border-left:0px solid transparent; border-bottom:0px solid transparent; border-right:0px solid transparent; padding-top:5px; padding-bottom:5px; padding-right: 0px; padding-left: 0px;">
                        <!--<![endif]-->
                        <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 10px; padding-left: 10px; padding-top: 10px; padding-bottom: 10px; font-family: 'Bodoni Moda', serif"><![endif]-->
                        <div style="font-family:'Bodoni Moda', serif;line-height:1.2;padding-top:10px;padding-right:10px;padding-bottom:10px;padding-left:10px;">
                          <div class="txtTinyMce-wrapper" style="line-height: 1.2; font-size: 12px; font-family: 'Bodoni Moda', serif; mso-line-height-alt: 14px;">""" + \
                            tr \
                          +"""</div>
                        </div>""" + \
                        sbr \
                        + """<!--[if (!mso)&(!IE)]><!-->
                      </div>
                      <!--<![endif]-->
                    </div>
                  </div>
                  <!--[if (mso)|(IE)]></td></tr></table><![endif]-->
                  <!--[if (mso)|(IE)]></td></tr></table></td></tr></table><![endif]-->
                </div>
              </div>
            </div>
            <div style="background-color:#ffffff;">
              <div class="block-grid " style="min-width: 320px; max-width: 700px; overflow-wrap: break-word; word-wrap: break-word; word-break: break-word; Margin: 0 auto; background-color: #fafafa;">
                <div style="border-collapse: collapse;display: table;width: 100%;background-color:#fafafa;">
                  <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#ffffff;"><tr><td align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:700px"><tr class="layout-full-width" style="background-color:#fafafa"><![endif]-->
                  <!--[if (mso)|(IE)]><td align="center" width="700" style="background-color:#fafafa;width:700px; border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent;" valign="top"><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 0px; padding-left: 0px; padding-top:0px; padding-bottom:5px;"><![endif]-->
                  <div class="col num12" style="min-width: 320px; max-width: 700px; display: table-cell; vertical-align: top; width: 700px;">
                    <div class="col_cont" style="width:100% !important;">
                      <!--[if (!mso)&(!IE)]><!-->
                      <div style="border-top:0px solid transparent; border-left:0px solid transparent; border-bottom:0px solid transparent; border-right:0px solid transparent; padding-top:0px; padding-bottom:5px; padding-right: 0px; padding-left: 0px;">
                        <!--<![endif]-->
                        <div class="img-container center autowidth" align="center" style="padding-right: 0px;padding-left: 0px;">
                          <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr style="line-height:0px"><td style="padding-right: 0px;padding-left: 0px;" align="center"><![endif]--><img class="center autowidth" align="center" border="0" src="https://d15k2d11r6t6rl.cloudfront.net/public/users/Integrators/BeeProAgency/629740_611703/u.png" style="text-decoration: none; -ms-interpolation-mode: bicubic; height: auto; border: 0; width: 100%; max-width: 700px; display: block;" width="700">
                          <!--[if mso]></td></tr></table><![endif]-->
                        </div>
                        <div style="font-size:16px;text-align:center;font-family:'Bodoni Moda', serif">""" + \
                          news_mail + "<br><br><br><br>"\
                        """</div>
                        <table class="social_icons" cellpadding="0" cellspacing="0" width="100%" role="presentation" style="table-layout: fixed; vertical-align: top; border-spacing: 0; border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt;" valign="top">
                          <tbody>
                            <tr style="vertical-align: top;" valign="top">
                              <td style="word-break: break-word; vertical-align: top; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px;" valign="top">
                                <table class="social_table" align="center" cellpadding="0" cellspacing="0" role="presentation" style="table-layout: fixed; vertical-align: top; border-spacing: 0; border-collapse: collapse; mso-table-tspace: 0; mso-table-rspace: 0; mso-table-bspace: 0; mso-table-lspace: 0;" valign="top">
                                  <tbody>
                                    <tr style="vertical-align: top; display: inline-block; text-align: center;" align="center" valign="top">
                                      <td style="word-break: break-word; vertical-align: top; padding-bottom: 0; padding-right: 10px; padding-left: 10px;" valign="top"><a href="https://twitter.com/" target="_blank"><img width="32" height="32" src="https://d2fi4ri5dhpqd1.cloudfront.net/public/resources/social-networks-icon-sets/circle-color/twitter@2x.png" alt="Twitter" title="Twitter" style="text-decoration: none; -ms-interpolation-mode: bicubic; height: auto; border: 0; display: block;"></a></td>
                                      <td style="word-break: break-word; vertical-align: top; padding-bottom: 0; padding-right: 10px; padding-left: 10px;" valign="top"><a href="https://www.youtube.com/watch?v=Gr7SubkDLok" target="_blank"><img width="32" height="32" src="https://d2fi4ri5dhpqd1.cloudfront.net/public/resources/social-networks-icon-sets/circle-color/youtube@2x.png" alt="YouTube" title="YouTube" style="text-decoration: none; -ms-interpolation-mode: bicubic; height: auto; border: 0; display: block;"></a></td>
                                      <td style="word-break: break-word; vertical-align: top; padding-bottom: 0; padding-right: 10px; padding-left: 10px;" valign="top"><a href="https://www.linkedin.com/in/conrad-guest-137b43204/" target="_blank"><img width="32" height="32" src="https://d2fi4ri5dhpqd1.cloudfront.net/public/resources/social-networks-icon-sets/circle-color/linkedin@2x.png" alt="LinkedIn" title="LinkedIn" style="text-decoration: none; -ms-interpolation-mode: bicubic; height: auto; border: 0; display: block;"></a></td>
                                      <td style="word-break: break-word; vertical-align: top; padding-bottom: 0; padding-right: 10px; padding-left: 10px;" valign="top"><a href="" target="_blank"><img width="32" height="32" src="https://d2fi4ri5dhpqd1.cloudfront.net/public/resources/social-networks-icon-sets/circle-color/website@2x.png" alt="Web Site" title="Web Site" style="text-decoration: none; -ms-interpolation-mode: bicubic; height: auto; border: 0; display: block;"></a></td>
                                    </tr>
                                  </tbody>
                                </table>
                              </td>
                            </tr>
                          </tbody>
                        </table>
                        <div style="font-size:16px;text-align:center;font-family:Arial, Helvetica Neue, Helvetica, sans-serif">
                          <div style="margin-top: 40px;border-top:1px dashed #D6D6D6;margin-bottom: 40px;"></div>
                        </div>
                        <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 10px; padding-left: 10px; padding-top: 10px; padding-bottom: 10px; font-family: Arial, sans-serif"><![endif]-->
                        <div style="color:#C0C0C0;font-family:Arial, Helvetica Neue, Helvetica, sans-serif;line-height:1.2;padding-top:10px;padding-right:10px;padding-bottom:10px;padding-left:10px;">
                          <div class="txtTinyMce-wrapper" style="line-height: 1.2; font-size: 12px; font-family: Arial, Helvetica Neue, Helvetica, sans-serif; color: #C0C0C0; mso-line-height-alt: 14px;">
                            <p style="font-size: 12px; line-height: 1.2; text-align: center; word-break: break-word; font-family: Arial, Helvetica Neue, Helvetica, sans-serif; mso-line-height-alt: 14px; margin: 0;"><span style="color: #C0C0C0;">Copyright © 2021 The Morning Paper, All rights reserved. Try me and I'll sue</span></p>
                            <p style="font-size: 12px; line-height: 1.2; text-align: center; word-break: break-word; font-family: Arial, Helvetica Neue, Helvetica, sans-serif; mso-line-height-alt: 14px; margin: 0;"><span style="color: #C0C0C0;">you into oblivion.<br><br>Where to find us:</span></p>
                            <p style="font-size: 12px; line-height: 1.2; text-align: center; word-break: break-word; font-family: Arial, Helvetica Neue, Helvetica, sans-serif; mso-line-height-alt: 14px; margin: 0;"><span style="color: #C0C0C0;"><br>themorningpaper.co</span></p>
                            <p style="font-size: 12px; line-height: 1.2; text-align: center; word-break: break-word; font-family: Arial, Helvetica Neue, Helvetica, sans-serif; mso-line-height-alt: 14px; margin: 0;"><span style="color: #C0C0C0;">Enquiries@themorningpaper.com</span></p>
                            <p style="font-size: 12px; line-height: 1.2; text-align: center; word-break: break-word; font-family: Arial, Helvetica Neue, Helvetica, sans-serif; mso-line-height-alt: 14px; margin: 0;"><span style="color: #C0C0C0;"><br>Changed your mind? You can <a href="*|UNSUB|*" target="_blank" style="color: #c0c0c0;" rel="noopener">unsubscribe</a> at any time.</span></p>
                          </div>
                        </div>
                        <!--[if mso]></td></tr></table><![endif]-->
                        <div style="font-size:16px;text-align:center;font-family:Arial, Helvetica Neue, Helvetica, sans-serif">
                          <div style="height-top: 20px;">&nbsp;</div>
                        </div>
                        <!--[if (!mso)&(!IE)]><!-->
                      </div>
                      <!--<![endif]-->
                    </div>
                  </div>
                  <!--[if (mso)|(IE)]></td></tr></table><![endif]-->
                  <!--[if (mso)|(IE)]></td></tr></table></td></tr></table><![endif]-->
                </div>
              </div>
            </div>
            <div style="background-color:transparent;">
              <div class="block-grid " style="min-width: 320px; max-width: 700px; overflow-wrap: break-word; word-wrap: break-word; word-break: break-word; Margin: 0 auto; background-color: #fafafa;">
                <div style="border-collapse: collapse;display: table;width: 100%;background-color:#fafafa;">
                  <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:transparent;"><tr><td align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:700px"><tr class="layout-full-width" style="background-color:#fafafa"><![endif]-->
                  <!--[if (mso)|(IE)]><td align="center" width="700" style="background-color:#fafafa;width:700px; border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent;" valign="top"><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 0px; padding-left: 0px; padding-top:5px; padding-bottom:5px;"><![endif]-->
                  <div class="col num12" style="min-width: 320px; max-width: 700px; display: table-cell; vertical-align: top; width: 700px;">
                    <div class="col_cont" style="width:100% !important;">
                      <!--[if (!mso)&(!IE)]><!-->
                      <div style="border-top:0px solid transparent; border-left:0px solid transparent; border-bottom:0px solid transparent; border-right:0px solid transparent; padding-top:5px; padding-bottom:5px; padding-right: 0px; padding-left: 0px;">
                        <!--<![endif]-->
                        <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 10px; padding-left: 10px; padding-top: 10px; padding-bottom: 10px; font-family: 'Bodoni Moda', serif"><![endif]-->
                        <div style="color:#eceaea;font-family:'Bodoni Moda', serif;line-height:1.2;padding-top:10px;padding-right:10px;padding-bottom:10px;padding-left:10px;">
                          <div class="txtTinyMce-wrapper" style="line-height: 1.2; font-size: 12px; font-family: 'Bodoni Moda', serif; color: #eceaea; mso-line-height-alt: 14px;">
                            <p style="text-align: center; line-height: 1.2; word-break: break-word; font-family: 'Bodoni Moda', serif; mso-line-height-alt: 14px; margin: 0;">I didn't mean to put this here but I can't be bothered to remove it. <br> Why are you reading this anyway?</p>
                          </div>
                        </div>
                        <!--[if mso]></td></tr></table><![endif]-->
                        <!--[if (!mso)&(!IE)]><!-->
                      </div>
                      <!--<![endif]-->
                    </div>
                  </div>
                  <!--[if (mso)|(IE)]></td></tr></table><![endif]-->
                  <!--[if (mso)|(IE)]></td></tr></table></td></tr></table><![endif]-->
                </div>
              </div>
            </div>
            <!--[if (mso)|(IE)]></td></tr></table><![endif]-->
          </td>
        </tr>
      </tbody>
    </table>
    <!--[if (IE)]></div><![endif]-->
  </body>

  </html>"""

  def send_mail(username, password, from_addr, to_addrs, msg):
      server = smtplib.SMTP('smtp-mail.outlook.com', '587')
      server.ehlo()
      server.starttls()
      server.ehlo()
      server.login(username, password)
      server.sendmail(from_addr, to_addrs, msg.as_string())
      server.quit()

  # Read email list txt

  emails = open('email.txt')
  email_list = list(emails)
  to_addrs = email_list[number]
  number += 1

  msg = MIMEMultipart()
  from_addr = username
  msg['Subject'] = "The Morning Paper"
  msg['From'] = from_addr
  msg['To'] = to_addrs

  # Attach HTML to the email
  body = MIMEText(html, 'html')
  msg.attach(body)

  try:
      send_mail(username, password, from_addr, to_addrs, msg)
      print("Email successfully sent to", to_addrs)
  except:
      print("Email failed")