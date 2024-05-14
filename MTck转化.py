import json, os
import datetime
import time
import requests,re,random

#获取青龙token
def token():
    url = 'http://127.0.0.1:5700/open/auth/token?client_id=********&client_secret=********'
    try:
        ceshi = requests.get(url=url,timeout=(10,10)).json()
    # print(ceshi["data"]["token"])
        return(ceshi["data"]["token"])
    except:
        print("青龙token获取失败")
        exit()

#获取全部CK
def getck(token):
    url = 'http://127.0.0.1:5700/open/envs'
    headers = {
        'Connection': 'keep-alive',
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
        "Accept-Encoding": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        'Authorization': 'Bearer '+ token
    }
    try:
        ck = requests.get(url=url,headers=headers,timeout=(10,10)).json()
        # print(ck["data"])
        return(ck["data"])
    except:
        print("获取全部CK失败")
        exit()

#更新青龙CK
def update_ck(token,ck,name,remarks,id):
    url = 'http://127.0.0.1:5700/open/envs'
    headers = {
        'Connection': 'keep-alive',
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
        "Accept-Encoding": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        'Authorization': 'Bearer '+ token
    }
    body = json.dumps({
        "value": ck,
        "name": name,
        "remarks": remarks,
        "id": id
    })
    try:
        res = requests.put(url=url,headers=headers,data=body,timeout=(10,10)).json()
        if res['code'] == 200:
            print(f"{remarks}更新CK成功")
            return True
        else:  
            print(f"更新失败：{res}")
            return False
    except Exception as e:
        print(f"更新异常，{e}")
        return False
    
#添加青龙CK
def add_ck(token,ck,remarks):
    url = 'http://127.0.0.1:5700/open/envs'
    headers = {
        'Connection': 'keep-alive',
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
        "Accept-Encoding": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        'Authorization': 'Bearer '+ token
    }
    payload = json.dumps([
        {
            "value": ck,
            "name": "MTCK",
            "remarks": remarks
        }
    ])
    try:
        res = requests.post(url, data=payload, headers=headers,timeout=(10,10)).json()
        if res['code'] == 200:
            print(f"{remarks}添加CK成功")
            return True
        else:  
            print(f"添加失败：{res}")
            return False
    except Exception as e:
        print(f"添加异常，{e}")
        return False
    
ql_token = token()
ck_lists = getck(ql_token)
for ck_list in ck_lists:
    if ck_list["name"] == "COOKIE_MT":
        mt_ck = ck_list["value"]
        print(mt_ck)
# exit()
if mt_ck == "":
    print("未获取到CK，请检查青龙环境变量")
    exit()
else:
    cklist=[]
    namechecklist=[]
    ckchecklist=[]
    cklists = mt_ck.split('\n')
    for ck in cklists:
        if ck.strip():  # 使用strip()方法来移除首尾空白字符，然后检查是否为空
            parts = ck.split("@")
            namechecklist.append(parts[0])
            ckchecklist.append(parts[1])
for i in range(len(namechecklist)):
    find = False
    userid = re.findall(r'userId=([A-Za-z_0-9\-]*)', ckchecklist[i],re.IGNORECASE)[0]
    for ck_list in ck_lists:
        if ck_list["name"] == "MTCK" and userid in ck_list["value"]:
            id = ck_list["id"]
            update_ck(ql_token,ckchecklist[i],"MTCK",namechecklist[i],id)
            find = True
            break
    if find == False:
        add_ck(ql_token,ckchecklist[i],namechecklist[i])
    