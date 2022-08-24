import requests
import json


class Operation():
    def get_method(url, header):

        response = requests.request("GET",url=url,headers=header,verify=False)

        if response.status_code ==  requests.codes['ok']:
            return (response.json())
        else:
            raise Exception('Error: ' + str(response.status_code))

    def post_method(url, header, params={}):


        response = requests.request("POST", url=  url, headers = header, data = params, verify = False )


        if response.status_code ==  requests.codes['ok']:
            return (response.json())
        else:
            raise Exception('Error: ' + str(response.status_code))


    def url(vmanage_host,vmanage_port,api):
        """ return the URL for the privide API ENDpoint """
        """ function to get the url provide api endpoint """

        return f"https://{vmanage_host}:{vmanage_port}{api}"
