// ==UserScript==
// @name WorkshopEnhance
// @version 2025/03/09
// @author Canaan HS
// @description 一個簡單的工作坊網址替換腳本，為網址添加 searchtext=<標題>
// @description:zh-TW 一個簡單的工作坊網址替換腳本，為網址添加 searchtext=<標題>
// @description:zh-CN 一个简单的工作坊网址替换脚本，为网址添加 searchtext=<标题>
// @description:en A simple workshop URL replacement script that adds searchtext=<title> to the URL

// @license MPL-2.0
// @match *://steamcommunity.com/*
// @icon https://cdn-icons-png.flaticon.com/512/220/220608.png

// @noframes
// @run-at document-body
// @grant none
// ==/UserScript==

(async () => {
    const url = location.href;
    const app = /^https:\/\/steamcommunity\.com\/app\/\d+/;
    const workshop = /^https:\/\/steamcommunity\.com\/workshop\/browse\/\?appid=\d+/;
    const sharedfiles = /^https:\/\/steamcommunity\.com\/sharedfiles\/filedetails\/\?id=\d+/;

    if (app.test(url)) {
        WaitElem(".workshop_home_content", content => {
            content.querySelectorAll("a.workshop_item_link").forEach(a => {
                const title = a.querySelector(".workshop_item_title")?.textContent;
                title && ReUri(a, title);
            })
        })
    } else if (workshop.test(url)) {
        WaitElem(".workshopBrowseItems", items => {
            items.querySelectorAll("div.workshopItem").forEach(div => {
                const title = div.querySelector(".workshopItemTitle")?.textContent;
                title && div.querySelectorAll("a").forEach(a => ReUri(a, title));
            })
        })
    } else if (sharedfiles.test(url)) {
        WaitElem(".workshopItemTitle", title => ReUri(url, title?.textContent ?? ""));
    }

    function ReUri(uri, title) {
        const isElement = uri instanceof Element;
        const Uri = isElement ? uri.href : uri;

        const newUri = Uri.includes("&searchtext=")
            ? Uri.replace(/(&searchtext=)(.*)?/, `$1${title}`)
            : `${Uri}&searchtext=${title}`;

        isElement ? uri.href = newUri : history.replaceState(null, '', newUri);
    };

    function WaitElem(selector, found) {
        const observer = new MutationObserver(() => {
            const result = document.querySelector(selector);
            if (result) {
                observer.disconnect();
                found(result);
            }
        });
        observer.observe(document.body, {subtree: true, childList: true});
    };
})();