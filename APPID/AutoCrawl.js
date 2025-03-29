// ==UserScript==
// @name         AutoCrawl
// @description  懶得繞過反爬的自動化獲取 https://steamdb.info/charts/ 遊戲 APP ID 的油猴腳本, 回到第一頁按下獲取即可
// @version      1.0
// @author       Canaan HS

// @match        *://steamdb.info/*

// @license      MPL-2.0

// @run-at       document-start
// @grant        GM_registerMenuCommand

// @require      https://update.greasyfork.org/scripts/487608/1561380/SyntaxLite_min.js
// ==/UserScript==

(async () => {
  const UseDelay = false;

  Syn.Menu({
    "Start Get ID": {
      func: () => {
        const new_data = {};

        function Task() {
          for (const tr of Syn.$qa("#table-apps tr.app")) {
            const name = tr.$q(".applogo").nextElementSibling.$text();
            const id = tr.$gAttr("data-appid");
            new_data[name] = id;
          }

          const next = Syn.$q("button.next");
          if (!next.$gAttr("tabindex")) {
            next.click();
            UseDelay ? requestAnimationFrame(Task) : Task();
          } else {
            Syn.OutputJson(new_data, "ID");
          }
        }

        Task();
      },
    },
  });
})();