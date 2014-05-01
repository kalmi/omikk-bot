#encoding: utf-8

from datetime import date

from BeautifulSoup import BeautifulSoup, SoupStrainer

import re

import mechanize
import cookielib

import os
BOT_USER_AGENT = os.environ['BOT_USER_AGENT']

def get_data(user,password):
  # Browser
  br = mechanize.Browser()

  # Cookie Jar
  cj = cookielib.LWPCookieJar()
  br.set_cookiejar(cj)

  # Browser options
  br.set_handle_equiv(True)
  br.set_handle_gzip(False)
  br.set_handle_redirect(True)
  br.set_handle_referer(True)
  br.set_handle_robots(False)

  # Follows refresh 0 but not hangs on refresh > 0
  br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

  # Want debugging messages?
  #br.set_debug_http(True)
  #br.set_debug_redirects(True)
  #br.set_debug_responses(True)

  br.addheaders = [('User-agent', BOT_USER_AGENT)]

  r = br.open('http://aleph.omikk.bme.hu/F?func=BOR-INFO')
  br.select_form(nr=0)
  br.form['bor_id'] = user
  br.form['bor_verification'] = password
  br.submit()
  
  current_url = br.geturl()
  session_id = re.search(".*/F/(.*)", current_url).group(1)

  r = br.open('http://aleph.omikk.bme.hu/F/'+session_id+'?func=bor-info')
  html = r.read()
  soup = BeautifulSoup(html)
  TDs = soup.findAll('td')

  email = None
  for i in range(len(TDs)):
    if u"E-mail" in TDs[i].text:
      email = TDs[i+1]
      break
  
  beiratkozas_ervenyesseg = None  
  for i in range(len(TDs)):
    if u"Beiratkozás érvényessége" in TDs[i].text:
      beiratkozas_ervenyesseg = TDs[i+1]
      break
  
  if(not beiratkozas_ervenyesseg):
    return False
    
      
  email = email.text.replace("&nbsp;","").strip()
  beiratkozas_ervenyesseg = beiratkozas_ervenyesseg.text.replace("&nbsp;","").strip()

  year = int(beiratkozas_ervenyesseg[:4])
  month = int(beiratkozas_ervenyesseg[4:6])
  day = int(beiratkozas_ervenyesseg[6:8])

  days_till_card_expiration = (date(year, month, day) - date.today()).days
  #print days_till_card_expiration, 'nap a kártyád lejáratáig.'


  r = br.open('http://aleph.omikk.bme.hu/F/'+session_id+'?func=bor-loan')
  html = r.read()
  soup = BeautifulSoup(html)

  expirationDates = []
  try:
    table = soup.findAll('table')[2]
    TRs = table.findAll('tr')
    for tr in TRs:
      TDs = tr.findAll('td')
      if TDs:
        expirationDates.append(TDs[5].findAll('noscript')[0].text.strip())
        
    expirationDates = [date(int(x[:4]),int(x[4:6]),int(x[6:8])) for x in expirationDates]
    expirationDates.sort()

    closest = expirationDates[0]
  except IndexError:
    closest = date.max
  
  data = {}
  data['closest_expiration'] = closest
  data['email'] = email
  
  return data
  #print email
