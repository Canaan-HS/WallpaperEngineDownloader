import path from "path";
import { fileURLToPath } from "url";
process.chdir(path.dirname(fileURLToPath(import.meta.url)));

import fs from "fs";
const file = {
    read(path, parse = true) {
        return new Promise((resolve, reject) => {
            fs.readFile(path, "utf-8", (err, data) => {
                const Read = err ? false : data ?? false;
                if (Read) resolve(parse ? JSON.parse(Read) : data);
                else {
                    console.log(err);
                    resolve({});
                }
            })
        })
    },
    write(outPutData, saveName) {
        const Content = saveName.endsWith("json")
            ? JSON.stringify(outPutData, null, 4)
            : outPutData;

        fs.writeFile(
            saveName, Content,
            err => {
                err ? console.log(`${saveName}: 輸出失敗`) : console.log(`${saveName}: 輸出成功`);
            });
    },
    delete(path) {
        return new Promise((resolve, reject) => {
            fs.unlink(path, err => {
                if (err) {
                    console.log(`${path}: 刪除失敗`, err);
                    resolve(false);
                } else {
                    console.log(`${path}: 刪除成功`);
                    resolve(true);
                }
            });
        });
    }
};

/* 這原先是為瀏覽器的請求來寫的, 不見得完全適用於 node 環境 */
const request = (() => {
    const bodyProcess = (body) =>
        (typeof body === 'object' && body !== null && !(body instanceof FormData) && !(body instanceof Blob) && !(body instanceof ArrayBuffer))
            ? JSON.stringify(body) : body;

    const createMockXHR = (response, type, status, statusText, responseHeaders, responseURL) => {
        const headerObj = responseHeaders instanceof Headers
            ? Object.fromEntries(responseHeaders)
            : (responseHeaders || {});

        return {
            response,
            status,
            statusText,
            responseURL,
            responseText: (type === 'text' || type === 'json') ? (typeof response === 'string' ? response : JSON.stringify(response)) : null,
            responseType: type,
            readyState: 4,
            headers: headerObj,
            getAllResponseHeaders: () => {
                return Object.entries(headerObj).map(([k, v]) => `${k}: ${v}`).join('\r\n');
            },
            getResponseHeader: (name) => {
                return headerObj[Object.keys(headerObj).find(k => k.toLowerCase() === name.toLowerCase())] || null;
            }
        };
    };

    function send(url, options = {}) {
        if (!url) return Promise.reject('Invalid URL');

        let {
            headers = {},           // 請求標頭
            method = 'GET',         // 請求方法
            body = null,            // 允許發送數據 (如 POST)
            timeout = 0,            // 超時時間 0 為不設定
            reTry = 3,              // 失敗重試次數
            useFetch = true,        // 是否使用 Fetch API (不支援會自動切換成 XHR)
            responseType = "text",  // 期望的回應類型 json, text, blob, arraybuffer...
            progressThrottle = 100, // 進度回調的間隔
            onload, onloadstart, onreadystatechange,
            onprogress, onupprogress, onerror, ontimeout, onloadend, onabort
        } = options || {};

        let requestPromise, abortController = null;

        requestPromise = new Promise((resolve, reject) => {
            const task = {
                async _fetch() {
                    const controller = new AbortController();
                    abortController = controller;
                    const signal = controller.signal;

                    let timeoutId;
                    if (timeout > 0) {
                        timeoutId = setTimeout(() => {
                            controller.abort();
                            ontimeout?.(new Event('timeout'));
                            reject('Timeout');
                        }, timeout);
                    }

                    try {
                        onloadstart?.(new Event('loadstart'));

                        const response = await fetch(url, {
                            method,
                            headers,
                            body: bodyProcess(body),
                            signal
                        });

                        if (timeoutId) clearTimeout(timeoutId);

                        if (!response.ok) {
                            if (method === 'GET' && reTry-- > 0) {
                                setTimeout(task._fetch, 2e3 / reTry);
                                return;
                            };

                            const errObj = {
                                status: response.status,
                                statusText: response.statusText,
                                response
                            };

                            onerror?.(errObj);
                            onloadend?.(new Event('loadend'));
                            return reject(errObj);
                        }

                        let result;
                        if (onprogress && response.body) {
                            const reader = response.body.getReader();
                            const contentLength = +response.headers.get('Content-Length') || 0;
                            const lengthComputable = contentLength > 0;
                            let receivedLength = 0;
                            let chunks = [];
                            let lastProgressTime = 0;

                            while (true) {
                                const { done, value } = await reader.read();
                                if (done) break;
                                chunks.push(value);
                                receivedLength += value.length;

                                const now = Date.now();
                                if (now - lastProgressTime >= progressThrottle) {
                                    lastProgressTime = now;
                                    onprogress({
                                        loaded: receivedLength,
                                        total: contentLength,
                                        lengthComputable
                                    })
                                }
                            }

                            const chunksAll = new Uint8Array(receivedLength);
                            let position = 0;
                            for (let chunk of chunks) {
                                chunksAll.set(chunk, position);
                                position += chunk.length;
                            }

                            if (responseType === 'json') {
                                result = JSON.parse(new TextDecoder("utf-8").decode(chunksAll));
                            } else if (responseType === 'text') {
                                result = new TextDecoder("utf-8").decode(chunksAll);
                            } else if (responseType === 'blob') {
                                result = new Blob([chunksAll]);
                            } else if (responseType === 'arraybuffer') {
                                result = chunksAll.buffer;
                            } else {
                                result = new TextDecoder("utf-8").decode(chunksAll);
                            }
                        } else {
                            result = await {
                                'json': async () => await response.json(),
                                'text': async () => await response.text(),
                                'blob': async () => await response.blob(),
                                'arraybuffer': async () => await response.arrayBuffer()
                            }[responseType]();
                        }

                        const mockXHR = createMockXHR(
                            result,
                            responseType,
                            response.status,
                            response.statusText,
                            response.headers,
                            response.url
                        );

                        onload?.(mockXHR);
                        onloadend?.(new Event('loadend'), mockXHR);
                        resolve(result);
                    } catch (err) {
                        err.name === 'AbortError'
                            ? onabort?.(new Event('abort'))
                            : onerror?.(err);

                        onloadend?.(new Event('loadend'));
                        reject(err);
                    }
                },
                _xhr() {
                    const xhr = new XMLHttpRequest();
                    abortController = xhr;

                    xhr.open(method, url);
                    xhr.responseType = responseType;
                    if (timeout > 0) xhr.timeout = timeout;

                    for (const [key, value] of Object.entries(headers)) {
                        xhr.setRequestHeader(key, value);
                    }

                    if (onloadstart) xhr.onloadstart = onloadstart;
                    if (onprogress || onupprogress) {
                        const progress = onprogress
                            ? [xhr.onprogress, onprogress]
                            : [xhr.upload.onprogress, onupprogress];

                        let lastTime = 0;
                        progress[0] = e => {
                            const now = Date.now();
                            if (now - lastTime >= progressThrottle) {
                                lastTime = now;
                                progress[1](e, xhr);
                            }
                        }
                    }

                    if (onabort) xhr.onabort = onabort;
                    if (ontimeout) xhr.ontimeout = ontimeout;
                    if (onerror) xhr.onerror = onerror;
                    if (onloadend) xhr.onloadend = onloadend;
                    if (onreadystatechange) xhr.onreadystatechange = onreadystatechange;

                    xhr.onload = () => {
                        if (onload) onload(xhr);
                        if ((xhr.status >= 200 && xhr.status < 300) || xhr.status === 0) {
                            resolve(xhr.response);
                        } else {
                            if (method === 'GET' && reTry-- > 0) {
                                setTimeout(task._xhr, 2e3 / reTry);
                                return;
                            };

                            reject({ status: xhr.status, statusText: xhr.statusText, xhr });
                        }
                    };

                    try {
                        xhr.send(bodyProcess(body));
                    } catch (err) {
                        reject(err);
                    }
                }
            };

            useFetch ? task._fetch() : task._xhr();
        });

        requestPromise.abort = () => {
            if (abortController) {
                if (
                    abortController instanceof XMLHttpRequest
                    || abortController instanceof AbortController
                ) {
                    abortController.abort();
                } else {
                    console.warn('Abort not supported');
                }
            }
        };

        return requestPromise;
    };

    return {
        get: (url, options) => send(url, { ...options, method: 'GET' }),
        post: (url, options) => send(url, { ...options, method: 'POST' }),
        put: (url, options) => send(url, { ...options, method: 'PUT' }),
        delete: (url, options) => send(url, { ...options, method: 'DELETE' }),
        head: (url, options) => send(url, { ...options, method: 'HEAD' }),
        options: (url, options) => send(url, { ...options, method: 'OPTIONS' }),
        patch: (url, options) => send(url, { ...options, method: 'PATCH' }),
        trace: (url, options) => send(url, { ...options, method: 'TRACE' })
    }
})();

file.read("./ID.json").then(async data => {
    let index = 1;
    const cleanData = {}, timeout = 6e4; // 保險一點停久一點
    const verified = await file.read("./verified.json");

    for (const [name, id] of Object.entries(data)) {
        let success = false;

        while (!success) {
            try {
                if (verified[name]) {
                    cleanData[name] = id;
                    console.log(`[${index}] 保存: ${name}`);
                    break;
                }

                const response = await request.get(`https://store.steampowered.com/api/appdetails?appids=${id}`, { responseType: "json", reTry: 0 });

                success = true;
                if (response?.[id]?.data?.categories?.some(d => d.id === 30)) {
                    cleanData[name] = id;
                    console.log(`[${index}] 保存: ${name}`);
                } else {
                    console.log(`[${index}] 移除: ${name}`);
                }
            } catch (e) {
                if (e.status === 429) {
                    console.log(`[${index}] 請求過多等待中: ${name}`);
                    await new Promise(resolve => setTimeout(resolve, timeout));
                } else {
                    console.log(`[${index}] 自行檢查: https://steamcommunity.com/app/${id}/workshop/`);
                    success = true;
                }
            }
        }

        if (index % 100 === 0) file.write(cleanData, "./temp.json"); // 這是為了防止中途中斷丟失
        index++;
    }

    file.delete("./temp.json");
    file.write(cleanData, "./ID.json");
});