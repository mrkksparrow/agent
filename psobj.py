import os
import psutil
import traceback

PSUTIL_OBJECT = psutil

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
    

def get_bearer_token():
    file_obj = None
    try:
        tokenFile = "/var/run/secrets/kubernetes.io/serviceaccount/token"
        if os.path.isfile(tokenFile):
            file_obj=open(tokenFile,"r")
            kubeToken=file_obj.read()
            kubeToken=kubeToken.rstrip()
            if kubeToken:
                print('setting bearerToken')
                KubeGlobal.bearerToken = kubeToken
    except Exception as e:
        print('Exception -> GetbearerToken -> {0}'.format(e))
    finally:
        if file_obj:
            file_obj.close()


final= {}
final = check_if_process_running_mounted_path("/host/proc", ["kubelet", "kube proxy"])
print(final)
