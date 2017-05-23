import requests
import json


class GoogleCustomSearch(object):

    def google_custom(self,url):
        split_string=url.split('/')
        list_var=split_string[-2]
        linkedin_id=json.dumps(list_var)
        if linkedin_id == '"in"':
            list_var = split_string[-1]
            linkedin_id = json.dumps(list_var)
            load_data = requests.get(
                'https://www.googleapis.com/customsearch/v1?q=' + linkedin_id + '&cx=002086705837668586439:l1o6lrd_few&num=1'
                                                                                '&key=AIzaSyCMGfdDaSfjqv5zYoS0mTJnOT3e9MURWkU')
            data = json.loads(load_data.text)
        else:
            load_data = requests.get(
                'https://www.googleapis.com/customsearch/v1?q=' + linkedin_id + '&cx=002086705837668586439:l1o6lrd_few&num=1'
                                                                                '&key=AIzaSyCMGfdDaSfjqv5zYoS0mTJnOT3e9MURWkU')
            data = json.loads(load_data.text)
        try:
            for dt in data['items']:
                result={}
                currentOrganization = []
                for key,values in dt['pagemap'].items():
                    if key in ['hcard', 'person']:
                        if key == 'person':
                            for j in values:
                                current = dict()
                                try:
                                    result['city']=j['location']
                                except:
                                    result['city'] = ''
                                try:
                                    result['talent_designation']=j['role']
                                except:
                                    result['talent_designation'] = ''
                                try:
                                    current['name'] = j['org']
                                except:
                                    current['name'] = ''
                                current['from'] = ''
                                current['to'] = 'Present'
                                current['is_current'] = True
                                current['JobTitle'] = j['role']
                                try:
                                    result['currentOrganization']= currentOrganization
                                except:
                                    result['currentOrganization'] = ''
                                currentOrganization.append(current)
                        else:
                            if key == 'hcard':
                                for j in values:
                                    try:
                                        result['firstName'] = j['fn'].split(' ')[0]
                                    except:
                                        result['firstName'] = ''
                                    try:
                                        result['lastName'] = j['fn'].split(' ')[1]
                                    except:
                                        result['lastName'] = ''
                                    try:
                                        result['profile_image'] = j['photo']
                                    except:
                                        result['profile_image'] = ''

            return result
        except:
            pass