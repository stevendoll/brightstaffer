import http.cookiejar as cookielib
import os
import urllib
import re
import string
from bs4 import BeautifulSoup
from lxml import html
import csv, os, json
import requests
import random
from random import shuffle
from collections import OrderedDict
# from exceptions import ValueError
from time import sleep

#username = "user@email.com"
#password = "password"




class LinkedInParser(object):

    def linkedin_data(self,url):

        # #cookie_filename = "parser.cookies.txt"
        # dir_path = os.path.dirname(os.path.abspath(__file__))
        # # previous_path = os.path.split(dir_path)[0]
        #
        # # basepath = os.path.basename()
        # # Keras training parameters
        # cookies_file = 'parser.cookies.txt'
        # cookies_file_model_file = os.path.join(dir_path, cookies_file)
        # if os.path.exists(cookies_file_model_file):
        #     os.remove(cookies_file_model_file)
        # self.cj = cookielib.MozillaCookieJar(cookies_file_model_file)
        # if os.access(cookies_file_model_file, os.F_OK):
        #     self.cj.load()
        # self.opener = urllib.request.build_opener(
        #     urllib.request.HTTPRedirectHandler(),
        #     urllib.request.HTTPHandler(debuglevel=0),
        #     urllib.request.HTTPSHandler(debuglevel=0),
        #     urllib.request.HTTPCookieProcessor(self.cj)
        # )
        # self.opener.addheaders = [
        #     ('User-agent', ("Chrome/57.0.2987.133 (Macintosh; Intel Mac OS X 10_12_0)"))
        # ]
        #
        # # Login
        # #self.loginPage()

        title = self.loadTitle(url)
        #self.cj.save()
        return title

    def loadPage(self, url, data=None):
        """
        Utility function to load HTML from URLs for us with hack to continue despite 404
        """
        # We'll print the url in case of infinite loop
        # print "Loading URL: %s" % url
        try:
            if data is not None:
                response = self.opener.open(url, data)
            else:
                response = self.opener.open(url)
            return ''.join([str(l) for l in response.readlines()])
        except Exception as e:
            # If URL doesn't load for ANY reason, try again...
            # Quick and dirty solution for 404 returns because of network problems
            # However, this could infinite loop if there's an actual problem
            return self.loadPage(url, data)

    def loadSoup(self, url, data=None):
        """
        Combine loading of URL, HTML, and parsing with BeautifulSoup
        """
        html = self.loadPage(url, data)
        soup = BeautifulSoup(html,"html.parser")
        return soup

    # def loginPage(self):
    #     """
    #     Handle login. This should populate our cookie jar.
    #     """
    #     soup = self.loadSoup("https://www.linkedin.com/")
    #     csrf = soup.find(id="loginCsrfParam-login")['value']
    #     login_data = urllib.parse.urlencode({
    #         'session_key': self.login,
    #         'session_password': self.password,
    #         'loginCsrfParam': csrf,
    #     }).encode('utf8')
    #
    #     self.loadPage("https://www.linkedin.com/uas/login-submit", login_data)
    #     return

    def loadTitle(self,url):
        #url='https://www.linkedin.com/in/chandan-varma-89203b54/'
        user_agent={1:"Chrome/57.0.2987.133 (Macintosh; Intel Mac OS X 10_12_0)",
                    2:"Mozilla/5.0 (X11; Linux x86_32) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36",
                    3:"Mozilla/5.0 (X11; Window x86_32) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36",
                    4:'b',
                    5:'c',
                    6:'d',
                    7:'e',
                    8:'f',
                    9:'g',
                    10:'h'}
        agent=random.choice(list(user_agent))
        print (agent)
        try:
            headers = {
                'User-Agent': user_agent[agent]}
            response = requests.get(url)
            #page = self.loadSoup(url)
            formatted_response = str(response.content).replace('<!--', '').replace('-->', '')
            doc = html.fromstring(formatted_response)
            talent_name = doc.xpath('//h1[@id="name"]//text()')
            #print (''.join (talent_name))
            if talent_name:
                try:
                    #json_formatted_data = json.loads(datafrom_xpath[0])
                    talent_name=''.join(talent_name).split(' ')
                    talent_first_name= talent_name[0]
                    talent_last_name = talent_name[-1]
                    talent_location=doc.xpath('//span[@class="locality"]//text()')
                    talent_location=''.join(doc.xpath('//span[@class="locality"]//text()')).split(',')
                    talent_city=talent_location[0]
                    try:
                        talent_state = talent_location[1]
                        talent_country = talent_location[2]
                    except:
                        talent_state= ''
                        talent_country = ''
                    talent_Industry=''.join(doc.xpath('//dd[@class="descriptor"]//text()'))
                    talnet_company=doc.xpath('//h5[@class="item-subtitle"]/a')
                    currentOrganization=[]
                    pastOrganization = []
                    j = 0

                    for i in range(len(talnet_company)):
                        temp_dict = {}
                        talnet_company1 = doc.xpath('//h5[@class="item-subtitle"]/a[1]/text()')[i]
                        company_start_time = doc.xpath('//span[@class="date-range"]/time[1]/text()')[i]
                        if company_start_time:
                            company_start_time = company_start_time.split()[-1]
                        #company_end_time = doc.xpath('//span[@class="date-range"]/time'+str([i])+'/text()')[i]
                        if i==0:
                            talent_designation = doc.xpath('//h4[@class="item-title"]/a[1]/text()')[i]
                            company_end_time=doc.xpath('//span[@class="date-range"]/text()')[0]
                        else:
                            i=i-1
                            talent_designation = doc.xpath('//h4[@class="item-title"]/text()')[i]
                            company_end_time = doc.xpath('//span[@class="date-range"]/time' + str([2]) + '/text()')[i]
                        if company_end_time:
                            company_end_time = company_end_time.split()[-1]
                        temp_dict['name']=talnet_company1
                        temp_dict['from']=company_start_time
                        temp_dict['to']=company_end_time
                        temp_dict['JobTitle']=talent_designation
                        if j == 0:
                            currentOrganization.append(temp_dict)
                        else:
                            pastOrganization.append((temp_dict))
                        j += 1

                    #i=i+1
                    talent_education = doc.xpath('//ul[@class="schools"]/li[@class="school"]/header/h4[@class="item-title"]/a/text()')
                    education = []
                    for y in range(len(talent_education)):
                        edu_dict = {}
                        education_name = doc.xpath('//ul[@class="schools"]/li[@class="school"]/header/h4[@class="item-title"]/a/text()')[y]
                        education_history = doc.xpath('//h5[@class="item-subtitle"]/span[@class="translated translation"]/text()')[y]
                        edu_start_time = doc.xpath('//ul[@class="schools"]/li[@class="school"]/div[@class="meta"]/span[@class="date-range"]/time[1]/text()')[y]
                        edu_end_time = doc.xpath('//ul[@class="schools"]/li[@class="school"]/div[@class="meta"]/span[@class="date-range"]/time[2]/text()')[y]
                        edu_dict['name'] = education_name
                        edu_dict['from'] = edu_start_time
                        edu_dict['to'] = edu_end_time
                        education.append(edu_dict)

                    result = {
                        'firstName': talent_first_name,
                        'lastName':talent_last_name,
                        'city':talent_city,
                        'state': talent_state,
                        'county': talent_country,
                        'industryFocus':talent_Industry,
                        'linkedinProfileUrl': url,
                        'currentOrganization':currentOrganization,
                        'pastOrganization': pastOrganization,
                        'education':education

                    }
                    return result
                except:
                    pass

            # Retry in case of captcha or login page redirection
            if len(response.content) < 2000 or "trk=login_reg_redirect" in url:
                if response.status_code == 404:
                    print ("linkedin page not found")
                else:
                    raise ValueError('redirecting to login page or captcha found')

        except:
            print ("retrying :")

#parser = LinkedInParser("chandan.varma@kiwitech.com", 'AAA@064110')

