// ==UserScript==
// @name WorkshopEnhance
// @version 2026/08/21-Beta
// @author Canaan HS
// @description 一個簡單的工作坊網址替換腳本，為網址添加 searchtext=<標題>
// @description:zh-TW 一個簡單的工作坊網址替換腳本，為網址添加 searchtext=<標題>
// @description:zh-CN 一个简单的工作坊网址替换脚本，为网址添加 searchtext=<标题>
// @description:en A simple workshop URL replacement script that adds searchtext=<title> to the URL

// @license MPL-2.0
// @match *://steamcommunity.com/*
// @icon https://cdn-icons-png.flaticon.com/512/220/220608.png

// @noframes
// @grant window.onurlchange

// @run-at document-body
// ==/UserScript==

(() => {
    const app = /^https:\/\/steamcommunity\.com\/app\/\d+/;
    const workshop = /^https:\/\/steamcommunity\.com\/workshop\/browse\/\?appid=\d+/;
    const sharedfiles = /^https:\/\/steamcommunity\.com\/sharedfiles\/filedetails\/\?id=\d+/;
    const myworkshopfiles = /^https:\/\/steamcommunity\.com\/(?:profiles\/\d+|id\/[^/?#]+)\/myworkshopfiles\/?.*$/;

    const hotKeyTurnPage = (() => {

        const turnButtons = {
            leftButton: null,
            rightButton: null
        };

        document.addEventListener("keydown", _throttle(event => {
            const key = event.key;

            if (key === "ArrowLeft") {
                turnButtons.leftButton.click();
            } else if (key === "ArrowRight") {
                turnButtons.rightButton.click();
            }
        }, 600), { capture: true });

        return {
            register(buttons) {
                if (buttons.length >= 2) {
                    turnButtons.leftButton = buttons[0];
                    turnButtons.rightButton = buttons[1];
                }
            }
        }
    })();

    function main(url) {
        if (app.test(url)) {
            waitElem("div[style*='--gap: var(--spacing-9);'] > div:nth-child(2)", findUri)
        }
        else if (workshop.test(url)) {
            // 改成持續監聽 (現在改的 DOM 太不穩定了, 用暴力的方法)
            listenLoad(3e3, () => {
                findUri();
                hotKeyTurnPage.register(document.querySelectorAll("button[data-accent-color='accent']"));
            });
        } else if (myworkshopfiles.test(url)) {
            waitElem(".workshopBrowseItems", () => {
                findUri();
                waitElem(".pagebtn", hotKeyTurnPage.register, true);
            });
        }
        else if (sharedfiles.test(url)) {
            waitElem(".workshopItemTitle", title => reUri(url, title?.textContent ?? ""));
        }
    };

    function findUri() {
        const links = document.querySelectorAll("a[href^='https://steamcommunity.com/sharedfiles/filedetails/?id=']:not([fixed='true'])");
        if (links.length >= 2 && links.length % 2 === 0) {
            for (let i = 0; i < links.length; i += 2) {
                const [rawLink, titleLink] = [links[i], links[i + 1]];
                const titleText = titleLink.textContent.trim();

                if (!titleText) continue;

                reUri(rawLink, titleText);
                reUri(titleLink, titleText);
            }
        }
    };

    function reUri(uri, title) {
        const isElement = uri instanceof Element;
        const Uri = isElement ? uri.href : uri;

        const url = new URL(Uri);
        url.searchParams.set("searchtext", title);

        const newUri = url.href.replace(/\+/g, " ");

        isElement
            ? uri.tagName === "A" ? (uri.href = newUri, uri.setAttribute("fixed", "true")) : null
            : history.replaceState(null, '', newUri);
    };

    function _throttle(func, delay) {
        let lastTime = 0;
        return (...args) => {
            const now = Date.now();
            if ((now - lastTime) >= delay) {
                lastTime = now;
                func(...args);
            }
        }
    };

    let observer;
    function listenLoad(throttle, run) {
        if (observer) {
            observer.disconnect();
            observer = null;
        };

        observer = new MutationObserver(_throttle(run, throttle));
        observer.observe(document.body, {
            subtree: true,
            childList: true,
            attributes: true,
            characterData: true
        });
    };

    function waitElem(selector, found, all = false) {
        let timer, idleCallback;

        const query = () => {
            const result = all
                ? document.querySelectorAll(selector)
                : document.querySelector(selector);

            if (all ? result.length > 0 : result) {
                cancelIdleCallback(idleCallback);
                // clearTimeout(timer);
                found(result);
            } else {
                idleCallback = requestIdleCallback(query, { timeout: 5e2 });
            }
        }

        idleCallback = requestIdleCallback(query, { timeout: 5e2 });
        // timer = setTimeout(() => {
        // cancelIdleCallback(idleCallback);
        // }, 2e4);
    };

    function onUrlChange(callback, timeout = 15) {
        let timer;
        let cleaned = false;
        let support_urlchange = false;

        const originalPushState = history.pushState;
        const originalReplaceState = history.replaceState;

        const eventHandler = {
            urlchange: () => trigger('urlchange'),
            popstate: () => trigger('popstate'),
            hashchange: () => trigger('hashchange')
        };

        function trigger(type) {
            clearTimeout(timer);
            if (!support_urlchange && type === 'urlchange') support_urlchange = true;
            timer = setTimeout(() => {
                if (support_urlchange) off(false, true);
                callback({
                    type: type,
                    url: location.href,
                    domain: location.hostname
                });
            }, Math.max(15, timeout));
        };

        function off(all = true, clean = false) {
            if (clean && cleaned) return;

            clearTimeout(timer);
            history.pushState = originalPushState;
            history.replaceState = originalReplaceState;
            window.removeEventListener('popstate', eventHandler.popstate);
            window.removeEventListener('hashchange', eventHandler.hashchange);
            all && window.removeEventListener('urlchange', eventHandler.urlchange);

            cleaned = true;
        };

        window.addEventListener('urlchange', eventHandler.urlchange);
        window.addEventListener('popstate', eventHandler.popstate);
        window.addEventListener('hashchange', eventHandler.hashchange);
        history.pushState = function () {
            originalPushState.apply(this, arguments);
            trigger('pushState');
        };
        history.replaceState = function () {
            originalReplaceState.apply(this, arguments);
            trigger('replacestate');
        };

        return { off };
    };

    // 初次執行
    main(location.href);
    // 監聽網址變化
    onUrlChange(change => {
        main(change.url);
    });
})();