import requests
import json
from itertools import zip_longest
import difflib
import yaml
import re


from auth_header import Authentication as auth
from operations import Operation


class createSiteList():

    def newSiteRange(siteRange,siteID):
        if siteID == siteRange[0]:
            return ([f'{siteRange[0]+1}-{siteRange[1]}'])
        elif siteID == siteRange[1]:
            return ([f'{siteRange[0]}-{siteRange[1]-1}'])
        else :
            return ([f'{siteRange[0]}-{siteID-1}',f'{siteID+1}-{siteRange[1]}'])


    def createNewSiteListExSiteID(siteListIDEntries, postNewSiteListExSiteID, site_name, oldRange, newRange, siteID, url_create_site_policy_list, header):
        postNewSiteListExSiteID["name"] = f"{site_name}_ex{siteID}"
        for itr in siteListIDEntries:
            if itr['siteId'] == oldRange:
                for jtr in newRange:
                    postNewSiteListExSiteID['entries'].append({'siteId': jtr})
            else:
                postNewSiteListExSiteID['entries'].append(itr)

        return Operation.post_method(url_create_site_policy_list, header, params=json.dumps(postNewSiteListExSiteID))



    def createNewSiteListInSiteID(postNewSiteListInSiteID, site_name, siteID,  url_create_site_policy_list, header):
        postNewSiteListInSiteID["name"] = f"{site_name}_only_{siteID}"
        postNewSiteListInSiteID['entries'].append({'siteId': f'{siteID}'})

        return Operation.post_method(url_create_site_policy_list, header, params=json.dumps(postNewSiteListInSiteID))

class createPolicy():

    def createNewCentralizedPolicy(vmanage_host,vmanage_port, newPolicy, header):
        api_vsmart_post_policy = '/dataservice/template/policy/vsmart'
        url_vsmart_post_policy = Operation.url(vmanage_host,vmanage_port, api_vsmart_post_policy)
        data_vsmart_post_policy = Operation.post_method(url_vsmart_post_policy,header,params=json.dumps(newPolicy))
        return data_vsmart_post_policy


    def activateNewCentralizedPolicy(vmanage_host,vmanage_port, newPolicyID, header):
        api_vsmart_activate_policy = f'/dataservice/template/policy/vsmart/activate/{newPolicyID}'
        print(api_vsmart_activate_policy)
        url_vsmart_activate_policy = Operation.url(vmanage_host,vmanage_port, api_vsmart_activate_policy)
        data_vsmart_activate_policy = Operation.post_method(url_vsmart_activate_policy,header,params=json.dumps({"isEdited": "true"}))
        return data_vsmart_activate_policy
