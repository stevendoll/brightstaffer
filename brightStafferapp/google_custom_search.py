import requests
import json


class GoogleCustomSearch(object):

    def google_custom(self,url):
        load_data=requests.get('https://www.googleapis.com/customsearch/v1?q='+url+'&cx=002086705837668586439:l1o6lrd_few&num=1'
                                                                             '&key=AIzaSyCMGfdDaSfjqv5zYoS0mTJnOT3e9MURWkU')
        data=json.loads(load_data.text)
        try:
            for dt in data['items']:
                result={}
                currentOrganization = []
                for key,values in dt['pagemap'].items():
                    if key in ['hcard', 'person']:
                        if key=='person':
                            for j in values:
                                current = dict()
                                result['city']=j['location']
                                result['talent_designation']=j['role']
                                current['name'] = j['org']
                                result['currentOrganization']= currentOrganization
                                currentOrganization.append(current)
                        else:
                            if key == 'hcard':
                                for j in values:
                                    result['firstName']=j['fn'].split(' ')[0]
                                    result['lastName'] = j['fn'].split(' ')[1]
                                    result['profile_image']=j['photo']


                    #for i in xyz['pagemap']['hcard']:
                    #    print (i['fn'])
            return result
        except:
            pass