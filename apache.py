#!/usr/bin/python3

import sys
import json

# Change the Apache stats URL accordingly here. Retain the "?auto" suffix.
url = "https://hostname/server-status?auto"
username = "site24x7"
password = "example"

# if any impacting changes to this plugin kindly increment the plugin version here
PLUGIN_VERSION = "1"

# Setting this to true will alert you when there is a communication problem while posting plugin data to server
HEARTBEAT = "true"

dict_reqdMet = {'Total Accesses':'total_accesses',
                'Total kBytes':'total_kbytes',
                'CPULoad':'cpu_load',
                'Uptime':'uptime',
                'ReqPerSec':'req_per_sec',
                'BytesPerSec':'bytes_per_sec',
                'BytesPerReq':'bytes_per_req',
                'BusyWorkers':'busy_workers',
                'IdleWorkers':'idle_workers'
                }

METRICS_UNITS = {'total_kbytes':'Bytes',
                 'uptime':'Seconds',
                 'bytes_per_sec':'Bytes',
                 'bytes_per_req':'Bytes'
                 }

PYTHON_MAJOR_VERSION = sys.version_info[0]
if PYTHON_MAJOR_VERSION == 3:
    import urllib
    import urllib.request as urlconnection
    from urllib.error import URLError, HTTPError
    from http.client import InvalidURL
elif PYTHON_MAJOR_VERSION == 2:
    import urllib2 as urlconnection
    from urllib2 import HTTPError, URLError
    from httplib import InvalidURL

class apache():
    def __init__(self):
        self._userName = username
        self._userPass = password
        self._url = url
        self.dictApacheData = {}

    def main(self):
        self.metric_collector()
        print(str(json.dumps(self.dictApacheData)))

    def metric_collector(self):
        try:
            if self._userName and self._userPass:
                password_mgr = urlconnection.HTTPPasswordMgrWithDefaultRealm()
                password_mgr.add_password(None, url, self._userName, self._userPass)
                auth_handler = urlconnection.HTTPBasicAuthHandler(password_mgr)
                opener = urlconnection.build_opener(auth_handler)
                urlconnection.install_opener(opener)
            response = urlconnection.urlopen(url, timeout=10)
            if response.getcode() == 200:
                byte_responseData = response.read()
                str_responseData = byte_responseData.decode('UTF-8')
                self._parseStats(str_responseData)
            else:
                self.dictApacheData['status'] = 0
                self.dictApacheData['msg'] = 'Error_code' + str(response.getcode())
        except HTTPError as e:
            self.dictApacheData['status'] = 0
            self.dictApacheData['msg'] = 'Error_code : HTTP Error ' + str(e.code)
        except URLError as e:
            self.dictApacheData['status'] = 0
            self.dictApacheData['msg'] = 'Error_code : URL Error ' + str(e.reason)
        except InvalidURL as e:
            self.dictApacheData['status'] = 0
            self.dictApacheData['msg'] = 'Error_code : Invalid URL'
        except Exception as e:
            self.dictApacheData['status'] = 0
            self.dictApacheData['msg'] = 'Exception occured in collecting data : ' + str(e)

    def _parseStats(self, str_responseData):
        try:
            # dictApacheData = {}
            listStatsData = str_responseData.split('\n')
            for eachStat in listStatsData:
                stats = eachStat.split(':')
                if str(stats[0]) in dict_reqdMet:
                    self.dictApacheData.setdefault(dict_reqdMet[str(stats[0])], str.strip(str(stats[1])))
            self.dictApacheData['plugin_version'] = PLUGIN_VERSION
            self.dictApacheData['heartbeat_required'] = HEARTBEAT
            self.dictApacheData['units'] = METRICS_UNITS
            # print(str(json.dumps(dictApacheData)))
        except TypeError as e:
            self.dictApacheData['status'] = 0
            self.dictApacheData['msg'] = 'Type error in _parseStats'
            # print(str(json.dumps({'Error_code': 'Type error in _parseStats'})))
        except Exception as e:
            self.dictApacheData['status'] = 0
            self.dictApacheData['msg'] = 'Exception in _parse stats' + str(e)
            # print(str(json.dumps({'Error_code':str(e)})))

if __name__ == '__main__':
    ap = apache()
    ap.main()
