import os
import psutil

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
    

final= {}
final = check_if_process_running_mounted_path("/host/proc", ["kubelet", "kube proxy"])
print(final)
