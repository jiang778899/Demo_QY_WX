/*************************************

项目功能：美团外卖柜解锁
下载地址：vx:xiaozhuzi96
脚本作者：竹子
使用声明：⚠️仅供参考，🈲转载与售卖！

**************************************
QX
[rewrite_local]
^https:\/\/deliverycommonapi.peisong.meituan.com\/mp\/cabinet\/pickup\/cabinet\/getCabinetInfo url script-response-body https://gh.con.sh/https://raw.githubusercontent.com/jiang778899/Demo_QY_WX/master/mtwmg.js
Shadowrocket
美团外卖柜解锁 = type=http-response,pattern= ^https:\/\/deliverycommonapi.peisong.meituan.com\/mp\/cabinet\/pickup\/cabinet\/getCabinetInfo,requires-body=1,max-size=0,script-path=https://gh.con.sh/https://raw.githubusercontent.com/jiang778899/Demo_QY_WX/master/mtwmg.js
[mitm] 
hostname = deliverycommonapi.peisong.meituan.com

*************************************/


var body = $response.body;

body = body.replace(/\"charge":1/g, '\"charge":0');
body = body.replace(/\"chargeMt":1/g, '\"chargeMt":0');

$done({body});
