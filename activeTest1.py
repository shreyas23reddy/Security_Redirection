

import requests
import json
from itertools import zip_longest
import difflib
import yaml
import re
import time


from auth_header import Authentication as auth
from operations import Operation
from getAndParseDATA import getData
from getAndParseDATA import parseData
from createAndActivate import createSiteList
from createAndActivate import createPolicy

if __name__=='__main__':

    while True:

        """ open the yaml file where the constant data is stored"""

        with open("vmanage_login1.yaml") as f:
            config = yaml.safe_load(f.read())


        """ extracting info from Yaml file"""

        vmanage_host = config['vmanage_host']
        vmanage_port = config['vmanage_port']
        username = config['vmanage_username']
        password = config['vmanage_password']
        site_ID = config['site_ID']
        Data_Policy_Fw_Name = config['DataPolicyFwName']


        """ GET the TOKEN from Authnetication call"""
        header= auth.get_header(vmanage_host, vmanage_port,username, password)

        infoCollectionDictSite = {"siteIdName":[],"siteListId":[],"entries":[],"siteRange":[],"policyInfo":[],"activeDataPolicy":[], "activeDataPolicySiteID":[] }


        """ Call to get active vSmart policy """

        vSmartPolicy = getData.getVsmartPolicy(vmanage_host,vmanage_port,header)
        for vSmartActivePolicy in vSmartPolicy:
            if vSmartActivePolicy["isPolicyActivated"] == True:
                break

        vSmartpolicyId = vSmartActivePolicy["policyId"]



        sitePolicyActive = getData.getPolicySiteListID(vmanage_host,vmanage_port,header)
        #print(f"vSmartPolicyActive {vSmartActivePolicy}")

        infoCollectedDictSite = parseData.activePolicyInfoBasedOnSite(sitePolicyActive, infoCollectionDictSite, vSmartActivePolicy, site_ID)

        #print(f" infoCollectedDictSite {infoCollectedDictSite}")

        api_create_site_policy_list = '/dataservice/template/policy/list/site'
        url_create_site_policy_list = Operation.url(vmanage_host,vmanage_port,api_create_site_policy_list)

        postNewSiteListExSiteID = { "name": "null", "description": "Desc Not Required", "type": "site", "listId": "null", "entries": []}
        postNewSiteListInSiteID = { "name": "null", "description": "Desc Not Required", "type": "site", "listId": "null", "entries": []}

        for activeDataPolicysiteLisdID,index in zip( infoCollectedDictSite['activeDataPolicySiteID'], range(len(infoCollectedDictSite['activeDataPolicySiteID'])) ):
            #print(len(infoCollectedDictSite['activeDataPolicySiteID']) , infoCollectedDictSite['activeDataPolicySiteID'] )
            #print(infoCollectedDictSite["siteRange"][index][0],infoCollectedDictSite["siteRange"][index][1])

            if len(activeDataPolicysiteLisdID) > 0 and activeDataPolicysiteLisdID != []:
                active_DataPolicy_SiteListID = activeDataPolicysiteLisdID

                if infoCollectedDictSite["siteRange"][index][0] < infoCollectedDictSite["siteRange"][index][1]:

                    oldRange = f"{infoCollectedDictSite['siteRange'][index][0]}-{infoCollectedDictSite['siteRange'][index][1]}"
                    newRange = createSiteList.newSiteRange([infoCollectedDictSite['siteRange'][index][0],infoCollectedDictSite['siteRange'][index][1]],site_ID)
                    #print(infoCollectedDictSite["entries"][index],infoCollectedDictSite["siteIdName"][index])
                    SiteListExSiteID = createSiteList.createNewSiteListExSiteID(infoCollectedDictSite["entries"][index], postNewSiteListExSiteID, infoCollectedDictSite["siteIdName"][index], oldRange, newRange, site_ID, url_create_site_policy_list, header)
                    SiteListInSiteID = createSiteList.createNewSiteListInSiteID(postNewSiteListInSiteID, infoCollectedDictSite["siteIdName"][index], site_ID, url_create_site_policy_list, header)



                else:
                    oldRange = f"{infoCollectedDictSite['siteRange'][index][0]}"
                    newRange = [infoCollectedDictSite['siteRange'][index][0]]
                    SiteListInSiteID = createSiteList.createNewSiteListInSiteID(postNewSiteListInSiteID, infoCollectedDictSite["siteIdName"][index], site_ID, url_create_site_policy_list, header)

        Data_Policy_Fw_Def = getData.getDataPolicyFwDef(vmanage_host,vmanage_port,header, Data_Policy_Fw_Name)


        newPolicy = { "policyDescription": "demoVPN", "policyType": "feature", "policyName": "demoVPN", 'policyDefinition': {"assembly": []}, 'isPolicyActivated': False }
        newPolicy["policyName"] = f"{vSmartActivePolicy['policyName']}-FW-{site_ID}"

        for vSmartActivePolicy_Assembly in (json.loads(vSmartActivePolicy["policyDefinition"]))["assembly"]:

            if vSmartActivePolicy_Assembly['definitionId'] == Data_Policy_Fw_Def:
                vSmartActivePolicy_Assembly['entries'][0]['siteLists'].append(SiteListInSiteID['listId'])
                newPolicy['policyDefinition']['assembly'].append(vSmartActivePolicy_Assembly)

            elif vSmartActivePolicy_Assembly['type'] == 'data' and active_DataPolicy_SiteListID[0] in vSmartActivePolicy_Assembly['entries'][0]['siteLists']:
                vSmartActivePolicy_Assembly['entries'][0]['siteLists'].remove(active_DataPolicy_SiteListID[0])
                try:
                    vSmartActivePolicy_Assembly['entries'][0]['siteLists'].append(SiteListExSiteID['listId'])
                except:
                    print(f" single site_ID {site_ID} configured ")

                newPolicy['policyDefinition']['assembly'].append(vSmartActivePolicy_Assembly)

            else:

                newPolicy['policyDefinition']['assembly'].append(vSmartActivePolicy_Assembly)


        newPolicyID = createPolicy.createNewCentralizedPolicy(vmanage_host, vmanage_port, newPolicy,header)
        print(newPolicyID["policyId"])
        time.sleep(20)
        newPolicyActivated = createPolicy.activateNewCentralizedPolicy(vmanage_host, vmanage_port, newPolicyID["policyId"],header)
        print(newPolicyActivated)



        exit()
