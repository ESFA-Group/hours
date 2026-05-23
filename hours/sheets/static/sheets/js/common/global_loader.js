"use strict";
console.log("global_loader.js loaded");
window.GlobalLoader = (() => {
	console.log("hey");
	
    let counter = 0;

    function getLoader() {
        return document.getElementById("global-page-loader");
    }

    function getTextElement() {
        return document.getElementById("global-page-loader-text");
    }

    function show(message = "Loading...") {
        counter += 1;

        const loader = getLoader();
        const text = getTextElement();

        if (text) {
            text.textContent = message;
        }

        if (loader) {
            loader.classList.remove("d-none");
            loader.setAttribute("aria-hidden", "false");
        }

        document.body.classList.add("global-page-loading");
    }

    function hide() {
        counter = Math.max(0, counter - 1);

        if (counter > 0) return;

        const loader = getLoader();

        if (loader) {
            loader.classList.add("d-none");
            loader.setAttribute("aria-hidden", "true");
        }

        document.body.classList.remove("global-page-loading");
    }

    async function wrap(asyncCallback, message = "Loading...") {
        show(message);

        try {
            return await asyncCallback();
        } finally {
            hide();
        }
    }

    function isLoading() {
        return counter > 0;
    }

    return {
        show,
        hide,
        wrap,
        isLoading,
    };
})();