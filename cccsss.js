const $ = new Env('soul挤派对参数获取并自动挤');
// ====================== 全局配置区 ======================
const ENV_NAME = "ncck";
const ENV_REMARK = "挤派对参数更新";
const ENV_GROUP = "soul";

const BASE_URL = "http://ltw.frp.one:45922";
const APP_KEY = "41c95947e77be7a320abadf3dec39e21";
const APP_SECRET = "25a3102096129406e82723aaa70e7be79efd2469ebe1fe0e8e00185953a160d7";
// 任务ID配置
const TASK_ID = 5;
const STOP_TASK_URL = `${BASE_URL}/api/tasks/${TASK_ID}/stop`;
const RUN_TASK_URL = `${BASE_URL}/api/tasks/${TASK_ID}/run`;
// ======================================================

!(async () => {
  await captureRequest();
})().catch((e) => {
  $.log(e);
  $.msg($.name, "抓包执行异常", String(e));
}).finally(() => {
  $.done({});
});

/**
 * 通用抓包：
 * POST => url + headers + body
 * GET  => url + headers
 * 修改逻辑：每次抓包直接覆盖环境变量，不拼接、不去重，仅保留最新一条
 * 抓包保存成功后，自动同步远程面板变量，停止并重启任务
 */
async function captureRequest() {
  // 没有请求直接退出
  if (!$request || !$request.url || !$request.headers) {
    $.done({});
    return;
  }

  try {
    const method = ($request.method || "GET").toUpperCase();
    let captureData;

    if (method === "POST") {
      captureData = {
        url: $request.url,
        headers: $request.headers,
        body: $request.body || ""
      };
    } else {
      captureData = {
        url: $request.url,
        headers: $request.headers
      };
    }

    // 转成字符串
    const newCaptureStr = JSON.stringify(captureData);

    // 直接覆盖原有环境变量，不再拼接@多账号
    $.setdata(newCaptureStr, ENV_NAME);
    $.msg($.name + " 参数已更新覆盖", "", `已覆盖环境变量 ${ENV_NAME}，准备同步远程面板`);
    $.log(`✅ 已覆盖保存最新抓包数据：${newCaptureStr}`);

    // 抓包保存成功，执行远程同步
    await syncRemoteEnv(newCaptureStr);

  } catch (e) {
    $.log("❌ 抓包异常：", e);
    $.msg($.name + " 抓取失败", "", String(e));
  }

  $.done({});
}

// Promise封装QX原生请求 $task.fetch
function httpRequest(options) {
  return new Promise((resolve, reject) => {
    $task.fetch(options).then(resp => {
      resolve({ response: resp, body: resp.body });
    }, err => {
      reject(err);
    });
  });
}

// 获取鉴权Token
async function getToken() {
  const url = `${BASE_URL}/api/open-api/token`;
  const payload = { app_key: APP_KEY, app_secret: APP_SECRET };
  const reqOpts = {
    url: url,
    method: "POST",
    body: JSON.stringify(payload),
    headers: { "Content-Type": "application/json" }
  };
  const res = await httpRequest(reqOpts);
  let data;
  try {
    data = JSON.parse(res.body);
  } catch (e) {
    throw new Error(`Token接口返回非JSON：${res.body}`);
  }
  if (!data?.data?.access_token) {
    throw new Error(`获取Token失败：${JSON.stringify(data)}`);
  }
  return { Authorization: `Bearer ${data.data.access_token}` };
}

// 查询远程环境变量ID
async function getEnvId(headers) {
  const url = `${BASE_URL}/api/envs`;
  const reqOpts = { url, method: "GET", headers };
  const res = await httpRequest(reqOpts);
  let listData;
  try {
    listData = JSON.parse(res.body);
  } catch (e) {
    throw new Error(`查询变量列表返回非JSON：${res.body}`);
  }
  const envList = listData?.data || [];
  for (const item of envList) {
    if (item.name === ENV_NAME) return item.id;
  }
  return null;
}

// 更新已有环境变量
async function updateEnv(envId, headers, value) {
  const url = `${BASE_URL}/api/envs/${envId}`;
  const payload = {
    name: ENV_NAME,
    value: value,
    remarks: ENV_REMARK,
    group: ENV_GROUP
  };
  const reqOpts = {
    url,
    method: "PUT",
    headers,
    body: JSON.stringify(payload)
  };
  const res = await httpRequest(reqOpts);
  $.log("更新接口原始返回：", res.body);
  let result;
  try {
    result = JSON.parse(res.body);
  } catch (e) {
    throw new Error(`更新变量返回非JSON：${res.body}`);
  }
  return result;
}

// 新建环境变量
async function addEnv(headers, value) {
  const url = `${BASE_URL}/api/envs`;
  const payload = {
    name: ENV_NAME,
    value: value,
    remarks: ENV_REMARK,
    group: ENV_GROUP
  };
  const reqOpts = {
    url,
    method: "POST",
    headers,
    body: JSON.stringify(payload)
  };
  const res = await httpRequest(reqOpts);
  $.log("新增接口原始返回：", res.body);
  let result;
  try {
    result = JSON.parse(res.body);
  } catch (e) {
    throw new Error(`新增变量返回非JSON：${res.body}`);
  }
  return result;
}

// 停止定时任务
async function stopTargetTask(authHeaders) {
  const reqOpts = {
    url: STOP_TASK_URL,
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders
    }
  };
  const res = await httpRequest(reqOpts);
  $.log(`停止任务ID【${TASK_ID}】接口返回：`, res.body);
  let taskResult;
  try {
    taskResult = JSON.parse(res.body);
  } catch (e) {
    throw new Error(`停止定时任务返回非JSON：${res.body}`);
  }
  if (taskResult?.data) {
    return `停止任务ID【${TASK_ID}】执行成功`;
  } else {
    return `停止任务ID【${TASK_ID}】执行失败，返回：${JSON.stringify(taskResult)}`;
  }
}

// 启动定时任务
async function runTargetTask(authHeaders) {
  const reqOpts = {
    url: RUN_TASK_URL,
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders
    }
  };
  const res = await httpRequest(reqOpts);
  $.log(`启动任务ID【${TASK_ID}】接口返回：`, res.body);
  let taskResult;
  try {
    taskResult = JSON.parse(res.body);
  } catch (e) {
    throw new Error(`启动定时任务返回非JSON：${res.body}`);
  }
  if (taskResult?.data) {
    return `启动任务ID【${TASK_ID}】执行成功`;
  } else {
    return `启动任务ID【${TASK_ID}】执行失败，返回：${JSON.stringify(taskResult)}`;
  }
}

// 同步远程面板主逻辑
async function syncRemoteEnv(localEnvValue) {
  try {
    const authHeaders = await getToken();
    const envId = await getEnvId(authHeaders);
    const apiResult = envId
      ? await updateEnv(envId, authHeaders, localEnvValue)
      : await addEnv(authHeaders, localEnvValue);

    // 同步成功判定：存在data字段
    if (apiResult?.data) {
      // 先停止任务，再重启
      const stopMsg = await stopTargetTask(authHeaders);
      const runMsg = await runTargetTask(authHeaders);
      $.msg($.name, "✅ 正在开始挤派对", `已同步jpdck\n${stopMsg}\n${runMsg}`);
    } else {
      $.msg($.name, "⚠️ 同步异常", "接口无有效data数据: " + JSON.stringify(apiResult));
    }
  } catch (error) {
    const errMsg = error.message || String(error);
    $.msg($.name, "❌ 远程同步报错", errMsg);
    $.log("同步捕获异常：", errMsg);
  }
}

// prettier-ignore
function Env(t,e){"undefined"!=typeof process&&JSON.stringify(process.env).indexOf("GITHUB")>-1&&process.exit(0);class s{constructor(t){this.env=t}send(t,e="GET"){t="string"==typeof t?{url:t}:t;let s=this.get;return"POST"===e&&(s=this.post),new Promise((e,i)=>{s.call(this.env,t,(t,s,r)=>{t?i(t):e(s)})})}get(t){return this.send.call(this.env,t)}post(t){return this.send.call(this.env,t,"POST")}}return new class{constructor(t,e){this.name=t,this.http=new s(this),this.data=null,this.dataFile="box.dat",this.logs=[],this.isMute=!1,this.isNeedRewrite=!1,this.logSeparator="\n",this.startTime=(new Date).getTime(),Object.assign(this,e),this.log("",`🔔${this.name}, 开始!`)}isNode(){return"undefined"!=typeof module&&!!module.exports}isQuanX(){return"undefined"!=typeof $task}isSurge(){return"undefined"!=typeof $httpClient&&"undefined"==typeof $loon}isLoon(){return"undefined"!=typeof $loon}toObj(t,e=null){try{return JSON.parse(t)}catch{return e}}toStr(t,e=null){try{return JSON.stringify(t)}catch{return e}}getjson(t,e){let s=e;const i=this.getdata(t);if(i)try{s=JSON.parse(this.getdata(t))}catch{}return s}setjson(t,e){try{return this.setdata(JSON.stringify(t),e)}catch{return!1}}getScript(t){return new Promise(e=>{this.get({url:t},(t,s,i)=>e(i))})}runScript(t,e){return new Promise(s=>{let i=this.getdata("@chavy_boxjs_userCfgs.httpapi");i=i?i.replace(/\n/g,"").trim():i;let r=this.getdata("@chavy_boxjs_userCfgs.httpapi_timeout");r=r?1*r:20,r=e&&e.timeout?e.timeout:r;const[o,h]=i.split("@"),n={url:`http://${h}/v1/scripting/evaluate`,body:{script_text:t,mock_type:"cron",timeout:r},headers:{"X-Key":o,Accept:"*/*"}};this.post(n,(t,e,i)=>s(i))}).catch(t=>this.logErr(t))}loaddata(){if(!this.isNode())return{};{this.fs=this.fs?this.fs:require("fs"),this.path=this.path?this.path:require("path");const t=this.path.resolve(this.dataFile),e=this.path.resolve(process.cwd(),this.dataFile),s=this.fs.existsSync(t),i=!s&&this.fs.existsSync(e);if(!s&&!i)return{};{const i=s?t:e;try{return JSON.parse(this.fs.readFileSync(i))}catch(t){return{}}}}}writedata(){if(this.isNode()){this.fs=this.fs?this.fs:require("fs"),this.path=this.path?this.path:require("path");const t=this.path.resolve(this.dataFile),e=this.path.resolve(process.cwd(),this.dataFile),s=this.fs.existsSync(t),i=!s&&this.fs.existsSync(e),r=JSON.stringify(this.data);s?this.fs.writeFileSync(t,r):i?this.fs.writeFileSync(e,r):this.fs.writeFileSync(t,r)}}lodash_get(t,e,s){const i=e.replace(/\[(\d+)\]/g,".$1").split(".");let r=t;for(const t of i)if(r=Object(r)[t],void 0===r)return s;return r}lodash_set(t,e,s){return Object(t)!==t?t:(Array.isArray(e)||(e=e.toString().match(/[^.[\]]+/g)||[]),e.slice(0,-1).reduce((t,s,i)=>Object(t[s])===t[s]?t[s]:t[s]=Math.abs(e[i+1])>>0==+e[i+1]?[]:{},t)[e[e.length-1]]=s,t)}getdata(t){let e=this.getval(t);if(/^@/.test(t)){const[,s,i]=/^@(.*?)\.(.*?)$/.exec(t),r=s?this.getval(s):"";if(r)try{const t=JSON.parse(r);e=t?this.lodash_get(t,i,""):e}catch(t){e=""}}return e}setdata(t,e){let s=!1;if(/^@/.test(e)){const[,i,r]=/^@(.*?)\.(.*?)$/.exec(e),o=this.getval(i),h=i?"null"===o?null:o||"{}":"{}";try{const e=JSON.parse(h);this.lodash_set(e,r,t),s=this.setval(JSON.stringify(e),i)}catch(e){const o={};this.lodash_set(o,r,t),s=this.setval(JSON.stringify(o),i)}}else s=this.setval(t,e);return s}getval(t){return this.isSurge()||this.isLoon()?$persistentStore.read(t):this.isQuanX()?$prefs.valueForKey(t):this.isNode()?(this.data=this.loaddata(),this.data[t]):this.data&&this.data[t]||null}setval(t,e){return this.isSurge()||this.isLoon()?$persistentStore.write(t,e):this.isQuanX()?$prefs.setValueForKey(t,e):this.isNode()?(this.data=this.loaddata(),this.data[e]=t,this.writedata(),!0):this.data&&this.data[e]||null}initGotEnv(t){this.got=this.got?this.got:require("got"),this.cktough=this.cktough?this.cktough:require("tough-cookie"),this.ckjar=this.ckjar?this.ckjar:new this.cktough.CookieJar,t&&(t.headers=t.headers?t.headers:{},void 0===t.headers.Cookie&&void 0===t.cookieJar&&(t.cookieJar=this.ckjar))}get(t,e=(()=>{})){t.headers&&(delete t.headers["Content-Type"],delete t.headers["Content-Length"]),this.isSurge()||this.isLoon()?(this.isSurge()&&this.isNeedRewrite&&(t.headers=t.headers||{},Object.assign(t.headers,{"X-Surge-Skip-Scripting":!1})),$httpClient.get(t,(t,s,i)=>{!t&&s&&(s.body=i,s.statusCode=s.status),e(t,s,i)})):this.isQuanX()?(this.isNeedRewrite&&(t.opts=t.opts||{},Object.assign(t.opts,{hints:!1})),$task.fetch(t).then(t=>{const{statusCode:s,statusCode:i,headers:r,body:o}=t;e(null,{status:s,statusCode:i,headers:r,body:o},o)},t=>e(t))):this.isNode()&&(this.initGotEnv(t),this.got(t).on("redirect",(t,e)=>{try{if(t.headers["set-cookie"]){const s=t.headers["set-cookie"].map(this.cktough.Cookie.parse).toString();s&&this.ckjar.setCookieSync(s,null),e.cookieJar=this.ckjar}}catch(t){this.logErr(t)}}).then(t=>{const{statusCode:s,statusCode:i,headers:r,body:o}=t;e(null,{status:s,statusCode:i,headers:r,body:o},o)},t=>{const{message:s,response:i}=t;e(s,i,i&&i.body)}))}post(t,e=(()=>{})){if(t.body&&t.headers&&!t.headers["Content-Type"]&&(t.headers["Content-Type"]="application/x-www-form-urlencoded"),t.headers&&delete t.headers["Content-Length"],this.isSurge()||this.isLoon())this.isSurge()&&this.isNeedRewrite&&(t.headers=t.headers||{},Object.assign(t.headers,{"X-Surge-Skip-Scripting":!1})),$httpClient.post(t,(t,s,i)=>{!t&&s&&(s.body=i,s.statusCode=s.status),e(t,s,i)});else if(this.isQuanX())t.method="POST",this.isNeedRewrite&&(t.opts=t.opts||{},Object.assign(t.opts,{hints:!1})),$task.fetch(t).then(t=>{const{statusCode:s,statusCode:i,headers:r,body:o}=t;e(null,{status:s,statusCode:i,headers:r,body:o},o)},t=>e(t));else if(this.isNode()){this.initGotEnv(t);const{url:s,...i}=t;this.got.post(s,i).then(t=>{const{statusCode:s,statusCode:i,headers:r,body:o}=t;e(null,{status:s,statusCode:i,headers:r,body:o},o)},t=>{const{message:s,response:i}=t;e(s,i,i&&i.body)})}}time(t,e=null){const s=e?new Date(e):new Date;let i={"M+":s.getMonth()+1,"d+":s.getDate(),"H+":s.getHours(),"m+":s.getMinutes(),"s+":s.getSeconds(),"q+":Math.floor((s.getMonth()+3)/3),S:s.getMilliseconds()};/(y+)/.test(t)&&(t=t.replace(RegExp.$1,(s.getFullYear()+"").substr(4-RegExp.$1.length)));for(let e in i)new RegExp("("+e+")").test(t)&&(t=t.replace(RegExp.$1,1==RegExp.$1.length?i[e]:("00"+i[e]).substr((""+i[e]).length)));return t}msg(e=t,s="",i="",r){const o=t=>{if(!t)return t;if("string"==typeof t)return this.isLoon()?t:this.isQuanX()?{"open-url":t}:this.isSurge()?{url:t}:void 0;if("object"==typeof t){if(this.isLoon()){let e=t.openUrl||t.url||t["open-url"],s=t.mediaUrl||t["media-url"];return{openUrl:e,mediaUrl:s}}if(this.isQuanX()){let e=t["open-url"]||t.url||t.openUrl,s=t["media-url"]||t.mediaUrl;return{"open-url":e,"media-url":s}}if(this.isSurge()){let e=t.url||t.openUrl||t["open-url"];return{url:e}}}};if(this.isMute||(this.isSurge()||this.isLoon()?$notification.post(e,s,i,o(r)):this.isQuanX()&&$notify(e,s,i,o(r))),!this.isMuteLog){let t=["","==============📣系统通知📣=============="];t.push(e),s&&t.push(s),i&&t.push(i),console.log(t.join("\n")),this.logs=this.logs.concat(t)}}log(...t){t.length>0&&(this.logs=[...this.logs,...t]),console.log(t.join(this.logSeparator))}logErr(t,e){const s=!this.isSurge()&&!this.isQuanX()&&!this.isLoon();s?this.log("",`❗️${this.name}, 错误!`,t.stack):this.log("",`❗️${this.name}, 错误!`,t)}wait(t){return new Promise(e=>setTimeout(e,t))}done(t={}){const e=(new Date).getTime(),s=(e-this.startTime)/1e3;this.log("",`🔔${this.name}, 结束! 🕛 ${s} 秒`),this.log(),(this.isSurge()||this.isQuanX()||this.isLoon())&&$done(t)}}(t,e)}
