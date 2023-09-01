import os
import sys, traceback, json
import xml.etree.ElementTree as ET

try:
    import requests
    REQUEST_MODULE = requests
except Exception as e:
    REQUEST_MODULE = None




def load_xml_root_from_file(xmlFileName):
    root = None
    file_obj = None
    try:
        if os.path.isfile(xmlFileName):
            file_obj = open(xmlFileName,'rb')
            byte_data = file_obj.read()
            fileSysEncoding = sys.getfilesystemencoding()
            perfData = byte_data.decode(fileSysEncoding)
            root = ET.fromstring(perfData)
        else:
            print('LoadXmlRootFromFile -> xmlFileName not available')
    except Exception as e:
        print('LoadXmlRootFromFile -> Exception -> {0}'.format(e))
    finally:
        if file_obj:
            file_obj.close()
    return root
    
    
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
            #print(r.status_code)
            #print(data)
            return r.status_code,json.loads(data)
        except Exception as e:
            print('curlapiWithToken -> Exception -> {0}'.format(e))
        return -1,{}
        
def process_groups(group,itemsGroupValList,thisDic):
    print('ProcessGroups ....... ')
    try:
        if group:
            name = group.get('Name')
            if name:
                groupDic = {}
                for item in group.findall("item"):
                    process_items(item,itemsGroupValList,groupDic)
                for itemsG in group.findall("itemsGroup"):
                    items_group(itemsG,itemsGroupValList,groupDic)
                thisDic[name] = groupDic
            else:
                print('ProcessGroups -> Name is None')            
    except Exception as e:
        print('ProcessGroups -> Exception -> {0}'.format(e))
    return None
    
def get_dict_node(dictNode,path):
    try:
        toReturnNode = dictNode
        pathExists = False
        #AgentLogger.log(AgentLogger.KUBERNETES,str(path))
        if path != "":
            for patharg in path.split('/'):
                if patharg=="#":
                    patharg="/"
                
                if patharg in toReturnNode:
                    tempNode = toReturnNode[patharg]
                    toReturnNode = tempNode
                    pathExists = True
                else:
                    print('path - ' + str(patharg) + 'does not exist')
                    pathExists = False
                    break
                
        if pathExists:
            return toReturnNode
    except Exception as e:
        print('GetItemsGroupNode -> Exception -> {0}'.format(e))
    return None
    
def get_items_val(dataNode,path,name,getAsList):
    try:
        toReturnNode = dataNode
        if path:
            for patharg in path.split('/'):
                if patharg in toReturnNode:
                    tempNode = toReturnNode[patharg]
                    toReturnNode = tempNode
                else:
                    toReturnNode =''
                    break
        if getAsList:
            return toReturnNode

        if name in toReturnNode:
            return toReturnNode[name]
        else:
            print('GetItemsVal -> toReturnNode - NONE')
    except Exception as e:
        print('GetItemsVal -> Exception -> {0}'.format(e))
        traceback.print_exc()
    return None
    
def process_items(item,valNode,thisDic):
    #AgentLogger.log(AgentLogger.KUBERNETES,'ProcessItems ....... ')
    try:   
        name = item.get('Name')
        path = item.get('Path')
        shortName = item.get('shortName')
        toString = item.get('ToString')        
        getAsList = item.get('getAsList')
        script_path = item.get('module')
        script_name = item.get('method')
        args = item.get('args')
        val = None
        
        if not script_path:
            val = get_items_val(valNode,path,name,getAsList)

        if script_path and args in thisDic:
            #args_value = thisDic[args]
            #script_path=sys.modules[script_path]
            val='kavin'
            print('result -- {}'.format(val))

        #adding  if item is not present
        if val is None:
            print('value for path - ' + str(path) + 'does not exist -> hence adding "" val')
            val = ""
        
        if toString:
            val = json.dumps(val)
            
        unit_stripper = item.get("strip_unit")
        
        if unit_stripper:
            val = Math(val, unit_stripper)
        
        rate = item.get("rate")
        if rate:
            print('rate :: {} val :: {} name :: {}'.format(rate,val,name))
            ref_name=""
            if 'podRef' in valNode:
                ref_name = valNode['podRef']['name']
            elif 'node' in valNode:
                ref_name = valNode['node']['nodeName']
            val = 0
        
        expression = item.get("expr")
        if expression and len(str(val)) > 0:
            print('expr:: {} val :: {} name :: {}'.format(expression,val,name))
            val = float(val)
            d={name:val}
            val = 0
        
        if thisDic is None: #case 1 - directly return the val
            return val
        else:               #case 2 - add it to the dict 
            thisDic[shortName] = val
    except Exception as e:
        print('ProcessItems -> Exception -> {0}'.format(e))
        traceback.print_exc()
    return None 
    
def process_key_value_items_group(itemsGroup,itemsGroupValList,dictToAdd):
    try:
        thisDic = {}
        for key in itemsGroup.findall('Key'):
            keyVal = process_items(key,itemsGroupValList,None)
            if keyVal and keyVal != "":
               for value in key.findall('Value'):
                   valVal = process_items(value,itemsGroupValList,None)
                   if valVal:
                       dictToAdd[keyVal] = valVal                
    except Exception as e:
        print('ProcessNodeValueItemsGroup -> Exception -> {0}'.format(e))
    return None

def process_items_group(itemsGroup,itemsGroupValList,dictToAdd):
    print('ProcessItemsGroup ....... ')    
    try:
        thisDic = {}
        rootName = None
        rootVal = None
        for root in itemsGroup.findall('Root'):
            rootName = root.get('Name')
            val = process_items(root,itemsGroupValList,None)
            if rootVal:
                rootVal = rootVal + "_" + val #handling multiple roots
            else:
                rootVal = val
        
        if rootVal:        
            
            for group in itemsGroup.findall("Group"):
                process_groups(group,itemsGroupValList,thisDic)
            for item in itemsGroup.findall("item"):
                process_items(item,itemsGroupValList,thisDic)
            for itemsG in itemsGroup.findall("itemsGroup"):
                 items_group(itemsG,itemsGroupValList,thisDic)
            for merge in itemsGroup.findall("Merge"):
                merge_items_groups(merge,thisDic)
                                 
            #map id
            
            dictToAdd[rootVal] = thisDic
        else:
           print('ProcessItemsGroup -> rootVal is None') 
    except Exception as e:
        print('ProcessItemsGroup -> Exception -> {0}'.format(e))
    return None   

def items_group(itemsGroup,ItemsGroupValDict,dictToAdd):
    print('ItemsGroup ....... ')
    try:       
        if itemsGroup:               
            name = itemsGroup.get('Name')
            path = itemsGroup.get('Path')
            isKeyValuepair = itemsGroup.get('isKeyValuepair')
            isHidden = itemsGroup.get('isHidden')
            
            mapIdVal = itemsGroup.get('MapId')
            if mapIdVal and mapIdVal == 'False':
                print('not mapping ids')
                mapID = False
            else:
                mapID = True
            
            #get val
            itemsGroupValList = get_dict_node(ItemsGroupValDict,path)
            if itemsGroupValList:            
                if name and path:
                    dictToAddInner = {}
                    
                    if isHidden:
                        dict = dictToAdd
                    else:
                        dict = dictToAddInner                   
                    
                    if isKeyValuepair:
                        for itemsGroupValList1 in itemsGroupValList:
                            process_key_value_items_group(itemsGroup,itemsGroupValList1,dict)
                    else:
                        for itemsGroupValList1 in itemsGroupValList:
                            process_items_group(itemsGroup,itemsGroupValList1,dict)
                    
                    if not isHidden:        
                        if dictToAddInner is not None:
                            dictToAdd[name] = dictToAddInner
            else:
                print('value for path - ' + str(path) + 'does not exist')
    except Exception as e:
        print('ItemsGroup -> Exception -> {0}'.format(e))

def MergeDataDictionaries(dict1,dict2):
    try:
        if dict1 and not dict2:
            return dict1
        
        if dict2 and not dict1:
            return dict2
         
        dictNew = dict(mergedicts(dict1,dict2))              
        return dictNew
    except Exception as e:
        print('Exception while MergeDictionaries')
    return None

def merge_items_groups(merge,valDic):
    print('MergeItemsGroups')
    try:            
        itemsGroup1 = merge.get('itemsGroup1')
        itemsGroup2 = merge.get('itemsGroup2')
        newKey = merge.get('key')
        
        if valDic and newKey:
            itemsGroupDic1 = None
            itemsGroupDic2 = None
            
            if itemsGroup1 in valDic:
                itemsGroupDic1 = valDic.get(itemsGroup1)
                del valDic[itemsGroup1]
            if itemsGroup2 in valDic:
                itemsGroupDic2 = valDic.get(itemsGroup2)
                del valDic[itemsGroup2]
            
            dictNew = MergeDataDictionaries(itemsGroupDic1,itemsGroupDic2)
            if dictNew:
                valDic[newKey] = dictNew
            else:
                print('MergeItemsGroups -> failed')
    except Exception as e:
        print('MergeItemsGroups -> Exception -> {0}'.format(e))

def load_k8s_config_xml(xmlFile, isConf = True,isPerf = False, throughProxy=False, node=""):
    parsedData = {}
    useToken = None
    valDict = {}
    dcErrors = idDict = {}
    try:
        root = load_xml_root_from_file(xmlFile)
        if root is not None:
            
            for api in root.findall('api'):
                url = api.get('url')
                url = "https://api-int.aws-cls-os.itja.p1.openshiftapps.com:6443" + url
                #url = KubeUtil.replace_tokens(url, node, throughProxy)
                #apiType = api.get('Type')
                useToken = api.get('UseToken')
                #sendAlways
                sendAlways = False
                sendAlwaysStr = api.get('SendAlways')
                if sendAlwaysStr and sendAlwaysStr.lower() == "true":
                    sendAlways = True
                
                perf_api = api.get("perf")
                
                proceed_with_api = True
                
                if (isConf and perf_api)  or (isPerf and not perf_api):
                    proceed_with_api = False
                    
                print('proceed_with_api -- {} -- api -- {}'.format(proceed_with_api,api))
                
                if proceed_with_api:
                    print('processing url....')
                    status = None
                    status,valDict = curl_api_with_token(url) if perf_api else curl_api_with_token(url) 
                    
                    #add to DCError
                    if status and status != 200:
                        print('dcError - adding {0}'.format(url))
                        dcErrors[url] = status
                    
                    if valDict and valDict is not {}:
                        for group in api.findall("Group"):
                            process_groups(group,valDict,parsedData)
                        for itemsGroup in api.findall("itemsGroup"):
                            items_group(itemsGroup,valDict,parsedData)
                        for merge in api.findall("Merge"):
                            merge_items_groups(merge,parsedData)
                    else:
                        print('valDict is empty/None - skipping api - ' + url)
                else:
                    print('skipping url - {0}'.format(url))

            #map container ids
            
            #add Pods,Nodes,Containers count
            root.clear()
    except Exception as e:
        print('LoadK8sConfigXml -> Exception -> {0}'.format(e))
        traceback.print_exc()
    return json.dumps(parsedData)
    
print(load_k8s_config_xml('/opt/t.xml'))
