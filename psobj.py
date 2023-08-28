import os, sys, json
import psutil
import traceback
import requests

PSUTIL_OBJECT = psutil
REQUEST_MODULE = requests

def check_if_process_running_mounted_path(mountPath,filter_list):
    try:
        final_list = []
        if os.path.ismount(mountPath) and filter_list:
            PSUTIL_OBJECT.PROCFS_PATH = mountPath
            for proc in PSUTIL_OBJECT.process_iter():
                try:
                    pinfo = proc.as_dict(attrs=["name", "exe", "cmdline", "pid"])
                except Exception as e:
                    continue
                if type(pinfo["cmdline"]) is list:
                    process_name = " ".join(pinfo["cmdline"]).strip()
                    if process_name:
                        for process in filter_list:
                            if process in process_name:
                                final_list.append(process_name)
                        if final_list:
                            str = ' '.join(final_list)
        return final_list
    except Exception as e:
    	print("exception")
    return None

def curl_api_without_token(url):
    try:
        proxies = {"http": None,"https": None}        
        r = REQUEST_MODULE.get(url,proxies=proxies,verify=False,timeout=60)
        print('curlapiWithoutToken -> url - ' + url)
        print('curlapiWithoutToken -> statusCode - ' + str(r.status_code))
        data = r.content
        if isinstance(data, bytes):
            data = data.decode()
        print(r.status_code)
        print(data)
        return r.status_code,data
    except Exception as e:
        print('curlapiWithoutToken -> Exception -> {0}'.format(e))
    return -1,{}

def curl_api_with_token(url):
        try:            
            bearerToken = get_bearer_token()
            headers = {'Authorization' : 'Bearer ' + bearerToken}
            proxies = {"http": None,"https": None}
            r = REQUEST_MODULE.get(url,headers=headers,proxies=proxies,verify=False,timeout=500)
            print('curlapiWithToken -> url - ' + url)
            print('curlapiWithToken -> statusCode - ' + str(r.status_code))
            data = r.content
            if isinstance(data, bytes):
                data = data.decode()
            if "/metrics/cadvisor" in url or '/healthz' in url or '/livez' in url:
                return r.status_code,data
            print(r.status_code)
            print(data)
            return r.status_code,json.loads(data)
        except Exception as e:
            print('curlapiWithToken -> Exception -> {0}'.format(e))
        return -1,{}


def get_bearer_token():
    file_obj = None
    bearerToken = None
    try:
        tokenFile = "/var/run/secrets/kubernetes.io/serviceaccount/token"
        if os.path.isfile(tokenFile):
            file_obj=open(tokenFile,"r")
            kubeToken=file_obj.read()
            kubeToken=kubeToken.rstrip()
            if kubeToken:
                print('setting bearerToken')
                bearerToken = kubeToken
    except Exception as e:
        print('Exception -> GetbearerToken -> {0}'.format(e))
    finally:
        if file_obj:
            file_obj.close()
        return bearerToken

def isApiServerPingable():
    is_api_server_pingable = 0
    try:
       kube_cluster = str(sys.argv[1])
       url = "https://"+kube_cluster+"/livez"
       status,valDict = curl_api_with_token(url)
       print(status)
       print(valDict)
       if status == 200:
           is_api_server_pingable = 1
    except Exception as e:
       traceback.print_exc()
    return is_api_server_pingable

url = sys.argv[1]
curl_api_with_token(url)
curl_api_without_token(url)
#isApiServerPingable()
final= {}
final = check_if_process_running_mounted_path("/host/proc", ["kubelet", "kube proxy"])
#print(final)
