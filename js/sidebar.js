(function () {
    "use strict";

    var desktopBreakpoint = 768;
    var fixedTop = 10;

    function activeOffset() {
        return Math.min(300, Math.max(80, window.innerHeight * 0.3));
    }

    function documentTop(element) {
        return element.getBoundingClientRect().top + window.pageYOffset;
    }

    function initSidebar() {
        var sidebar = document.querySelector(".bs-docs-sidebar");
        var nav = sidebar && sidebar.querySelector(".bs-docs-sidenav");

        if (!sidebar || !nav) {
            return;
        }

        var links = Array.prototype.slice.call(nav.querySelectorAll('a[href^="#"]'));
        var sections = links.map(function (link) {
            var hash = link.getAttribute("href").slice(1);
            var id;

            try {
                id = decodeURIComponent(hash);
            } catch (error) {
                id = hash;
            }

            return {
                link: link,
                target: document.getElementById(id)
            };
        }).filter(function (section) {
            return section.target;
        });

        var fixedThreshold = 0;
        var navHeight = 0;

        function setActive(section) {
            links.forEach(function (link) {
                var item = link.parentNode;
                var isCurrent = section && link === section.link;

                if (item && item.nodeType === 1) {
                    if (isCurrent) {
                        item.classList.add("active");
                    } else {
                        item.classList.remove("active");
                    }
                }

                if (isCurrent) {
                    link.setAttribute("aria-current", "location");
                } else {
                    link.removeAttribute("aria-current");
                }
            });
        }

        function updateActive() {
            if (!sections.length) {
                return;
            }

            var marker = window.pageYOffset + activeOffset();
            var current = sections[0];

            sections.forEach(function (section) {
                if (documentTop(section.target) <= marker) {
                    current = section;
                }
            });

            var root = document.documentElement;
            if (window.pageYOffset + window.innerHeight >= root.scrollHeight - 2) {
                current = sections[sections.length - 1];
            }

            setActive(current);
        }

        function clearFixedPosition() {
            nav.classList.remove("is-fixed");
            nav.style.left = "";
            nav.style.width = "";
            nav.style.height = "";
            sidebar.style.minHeight = "";
        }

        function updatePosition() {
            if (window.innerWidth <= desktopBreakpoint) {
                clearFixedPosition();
                return;
            }

            if (window.pageYOffset >= fixedThreshold) {
                var sidebarRect = sidebar.getBoundingClientRect();
                nav.classList.add("is-fixed");
                nav.style.left = sidebarRect.left + "px";
                nav.style.width = sidebarRect.width + "px";
                nav.style.height = navHeight + "px";
            } else {
                nav.classList.remove("is-fixed");
                nav.style.left = "";
                nav.style.width = "";
                nav.style.height = "";
            }
        }

        function update() {
            updatePosition();
            updateActive();
        }

        function measure() {
            clearFixedPosition();

            if (window.innerWidth > desktopBreakpoint) {
                var navRect = nav.getBoundingClientRect();
                fixedThreshold = navRect.top + window.pageYOffset - fixedTop;
                navHeight = navRect.height;
                sidebar.style.minHeight = (navHeight + 30) + "px";
            }

            update();
        }

        links.forEach(function (link) {
            link.addEventListener("click", function () {
                var selected = sections.filter(function (section) {
                    return section.link === link;
                })[0];
                setActive(selected);
            });
        });

        window.addEventListener("scroll", update, { passive: true });
        window.addEventListener("resize", measure);
        window.addEventListener("load", measure);
        measure();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initSidebar);
    } else {
        initSidebar();
    }
}());
