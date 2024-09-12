// ==UserScript==
// @name         AutoCrawl
// @description  懶得繞過反爬的自動化獲取 https://steamdb.info/charts/ 遊戲 APP ID 的油猴腳本, 回到第一頁按下獲取即可
// @version      1.0
// @author       Canaan HS

// @match        *://steamdb.info/*

// @license      MPL-2.0

// @run-at       document-start
// @grant        GM_registerMenuCommand
// ==/UserScript==

(async () => {
    GM_registerMenuCommand("開始獲取", async () => {
        const data = new Map();

        function Task() {
            for (const tr of document.querySelectorAll("#table-apps tr.app")) {
                const name = tr.querySelector(".applogo").nextElementSibling.textContent;
                const id = tr.getAttribute("data-appid");
                data.set(id, name);
            };

            const next = document.querySelector("button.next");
            if (!next.getAttribute("tabindex")) {
                next.click(); // 沒在給你延遲的
                Task();
            } else {
                const json = JSON.stringify(Object.fromEntries(data), null, 4);
                const blob = new Blob([json], { type: "application/json" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "ID.json";
                a.click();
            };
        };

        Task();
    });
})();