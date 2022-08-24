"""
import all the reqiured librariers
"""
import requests
import json
from itertools import zip_longest
import difflib
import yaml
import re


from auth_header import Authentication as auth
from operations import Operation




class getData():
    """
    Get all site list
    """

    def getPolicySiteListID(vmanage_host,vmanage_port,header):

        api_site_policy_list = '/dataservice/template/policy/list/site'
        url_site_policy_list = Operation.url(vmanage_host,vmanage_port,api_site_policy_list)
        site_policy_list = Operation.get_method(url_site_policy_list,header)
        return site_policy_list['data']

    """
    Get all template vsmart policy list
    """
    def getVsmartPolicy(vmanage_host,vmanage_port,header):

        api_vsmart_policy = '/dataservice/template/policy/vsmart'
        url_vsmart_policy = Operation.url(vmanage_host,vmanage_port,api_vsmart_policy)
        data_vsmart_policy = Operation.get_method(url_vsmart_policy,header)
        return data_vsmart_policy['data']


    def getDataPolicyFwDef(vmanage_host,vmanage_port,header,DataPolicyFwName):

        api_DataPolicyFw_policy = '/dataservice/template/policy/definition/data'
        url_DataPolicyFw_policy = Operation.url(vmanage_host,vmanage_port,api_DataPolicyFw_policy)
        data_DataPolicyFw_policy = Operation.get_method(url_DataPolicyFw_policy,header)
        for DataPolicyFw in data_DataPolicyFw_policy['data']:
            if DataPolicyFw['name'] == DataPolicyFwName:
                break
        return DataPolicyFw["definitionId"]


        return data_DataPolicyFw_policy['data']



class parseData():

    def triggeredSiteID(siteID_entries, listID, site_ID, i=0 ):

        siteListRange = (re.split("-",siteID_entries[i]['siteId']))
        siteStart = int(siteListRange[0])
        siteEnd = int(siteListRange[len(siteListRange)-1])

        if site_ID not in range(siteStart,siteEnd+1,1) and i >= len(siteID_entries)  :
            return [False, siteStart, siteEnd]

        elif site_ID in range(siteStart,siteEnd+1,1):
            return [listID, siteStart, siteEnd]

        elif i < len(siteID_entries)-1:
            return parseData.triggeredSiteID(siteID_entries, listID, site_ID, i+1 )

        else:
            return [False, siteStart, siteEnd]


    def activePolicyInfoBasedOnSite(sitePolicyActive, infoCollectionDictSite, vSmartDataPolicy, site_ID, i=0):

        if i < len(sitePolicyActive):
            isActivatedByVsmart = sitePolicyActive[i]

            if isActivatedByVsmart["isActivatedByVsmart"] == True:
                isSiteList = parseData.triggeredSiteID(isActivatedByVsmart['entries'], isActivatedByVsmart['listId'], site_ID)


                if isSiteList[0] != False:
                    infoCollectionDictSite["siteIdName"].append(isActivatedByVsmart["name"])
                    infoCollectionDictSite["siteListId"].append(isSiteList[0])
                    infoCollectionDictSite["siteRange"].append([isSiteList[1],isSiteList[2]])
                    infoCollectionDictSite["entries"].append(isActivatedByVsmart['entries'])

                    activePolicyInfoList = []
                    activeDataPolicyList = []
                    activeDataPolicySiteID = []

                    for activePolicy in json.loads(vSmartDataPolicy["policyDefinition"])["assembly"]:

                        if ( isSiteList[0] in (activePolicy['entries'][0]['siteLists']) ) and (activePolicy['type'] == 'data'):
                            activeDataPolicyList.append(activePolicy)
                            activeDataPolicySiteID.append(isSiteList[0])


                        if isSiteList[0] in (activePolicy['entries'][0]['siteLists']):
                            activePolicyInfoList.append(activePolicy)


                    infoCollectionDictSite["policyInfo"].append(activePolicyInfoList)
                    infoCollectionDictSite["activeDataPolicy"].append(activeDataPolicyList)
                    infoCollectionDictSite["activeDataPolicySiteID"].append(activeDataPolicySiteID)

            return parseData.activePolicyInfoBasedOnSite(sitePolicyActive, infoCollectionDictSite, vSmartDataPolicy, site_ID, i+1)

        else:

            return infoCollectionDictSite
