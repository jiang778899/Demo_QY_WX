/**
 * Loon脚本：读取本地jpdck持久变量同步至远程面板
 * 修复：接口无code字段导致成功也报异常
 * 新增：任务启停功能总开关，true开启同步后启停任务，默认false关闭
 * 修改：BASE_URL 从 Loon持久变量 MBck 获取面板地址
 */
// ====================== 全局配置区（统一参数）======================
const ENV_NAME = "jpdck";
// 从Loon持久存储读取MBck作为远程面板BASE_URL
const BASE_URL = "http://1d141084.xq0.cn";
const APP_KEY = "336d9c4764a73c7facec5aadafda771c";
const APP_SECRET = "41d2f09fb081f5887f31c9ae4ed13deca80e5d7a2be3ac23fef3f37311400186";
const ENV_REMARK = "挤派对参数更新";
const ENV_GROUP = "soul";
// 任务控制总开关 true=同步完成后停止并重启任务 false=仅同步变量，不操作任务（默认关闭）
const TASK_CTRL_SWITCH = true ;
// 定时任务ID
const TASK_ID = 27;
// =================================================================

let localEnvValue = $persistentStore.read(ENV_NAME);
if (!localEnvValue) {
    $notification.post("同步失败", "", "Loon本地未读取到 jpdck 变量");
    $done();
}
if (!BASE_URL) {
    $notification.post("同步失败", "", "Loon持久变量 MBck 为空，请配置面板根地址");
    $done();
}
const STOP_TASK_URL = `${BASE_URL}/api/tasks/${TASK_ID}/stop`;
const RUN_TASK_URL = `${BASE_URL}/api/tasks/${TASK_ID}/run`;

// Promise封装http请求
function httpRequest(options) {
    return new Promise((resolve, reject) => {
        const method = options.method.toLowerCase();
        $httpClient[method](options, (err, resp, body) => {
            if (err) return reject(err);
            resolve({ response: resp, body: body });
        });
    });
}

// 获取接口鉴权Token
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

// 查询远程同名环境变量ID
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

// PUT覆盖更新已有环境变量
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
    console.log("更新接口原始返回：", res.body);
    let result;
    try {
        result = JSON.parse(res.body);
    } catch (e) {
        throw new Error(`更新变量返回非JSON：${res.body}`);
    }
    return result;
}

// POST新建环境变量（不存在时执行）
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
    console.log("新增接口原始返回：", res.body);
    let result;
    try {
        result = JSON.parse(res.body);
    } catch (e) {
        throw new Error(`新增变量返回非JSON：${res.body}`);
    }
    return result;
}

// 停止定时任务接口
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
    console.log(`停止任务ID【${TASK_ID}】接口返回：`, res.body);
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

// 重启定时任务接口
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
    console.log(`启动任务ID【${TASK_ID}】接口返回：`, res.body);
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

// 主执行逻辑
(async function main() {
    try {
        const authHeaders = await getToken();
        const envId = await getEnvId(authHeaders);
        // 存在变量则PUT覆盖更新，无则新建
        const apiResult = envId
            ? await updateEnv(envId, authHeaders, localEnvValue)
            : await addEnv(authHeaders, localEnvValue);

        // 同步成功判断标准：接口返回包含data字段（适配无code面板接口）
        if (apiResult?.data) {
            let notifyContent = "✅ jpdck参数同步面板完成";
            // 开关开启才执行停止+重启任务
            if (TASK_CTRL_SWITCH) {
                const stopLog = await stopTargetTask(authHeaders);
                const runLog = await runTargetTask(authHeaders);
                notifyContent += `\n${stopLog}\n${runLog}`;
            } else {
                notifyContent += "\nℹ️ 任务启停功能已关闭，修改 TASK_CTRL_SWITCH = true 开启";
            }
            $notification.post("同步成功", "", notifyContent);
        } else {
            $notification.post("同步异常", "接口无有效data返回", JSON.stringify(apiResult));
        }
    } catch (error) {
        const errMsg = error.message || String(error);
        $notification.post("同步脚本报错", "", errMsg);
        console.error("执行异常详情：", errMsg);
    }
    $done();
})();