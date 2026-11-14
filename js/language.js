(function () {
    "use strict";

    var translations = window.scicomTranslations;
    var storageKey = "scicom-language";
    var language = "en";
    var entries = [];
    var buttons = document.querySelectorAll("[data-language]");

    function normalize(value) {
        return value.replace(/\s+/g, " ").trim();
    }

    function remember(node, attribute) {
        var original = attribute ? node.getAttribute(attribute) : node.nodeValue;
        var key = normalize(original);
        if (!Object.prototype.hasOwnProperty.call(translations, key)) {
            return;
        }
        entries.push({ node: node, attribute: attribute, original: original, values: translations[key] });
    }

    // Keep the original DOM, links and event handlers intact when switching languages.
    var walker = document.createTreeWalker(document.documentElement, NodeFilter.SHOW_TEXT, {
        acceptNode: function (node) {
            return /^(SCRIPT|STYLE|NOSCRIPT)$/.test(node.parentNode.tagName)
                ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
        }
    });
    var node;
    while ((node = walker.nextNode())) {
        remember(node, null);
    }
    document.querySelectorAll("[title], [alt], [aria-label]").forEach(function (element) {
        ["title", "alt", "aria-label"].forEach(function (attribute) {
            if (element.hasAttribute(attribute)) {
                remember(element, attribute);
            }
        });
    });

    function setLanguage(nextLanguage) {
        language = nextLanguage === "ko" ? "ko" : "en";
        entries.forEach(function (entry) {
            var value = entry.original.replace(/\S[\s\S]*\S|\S/, entry.values[language]);
            if (entry.attribute) {
                entry.node.setAttribute(entry.attribute, value);
            } else {
                entry.node.nodeValue = value;
            }
        });
        document.documentElement.lang = language;
        buttons.forEach(function (button) {
            button.setAttribute("aria-pressed", String(button.getAttribute("data-language") === language));
        });
        try {
            window.localStorage.setItem(storageKey, language);
        } catch (error) {
            // Language switching still works when browser storage is unavailable.
        }
        // Re-measure sticky sidebars after translated text changes their height.
        window.dispatchEvent(new Event("resize"));
    }

    buttons.forEach(function (button) {
        button.addEventListener("click", function () {
            setLanguage(button.getAttribute("data-language"));
        });
    });
    try {
        language = window.localStorage.getItem(storageKey) || language;
    } catch (error) {
        // The original English page is the default for a first visit.
    }
    setLanguage(language);
}());
