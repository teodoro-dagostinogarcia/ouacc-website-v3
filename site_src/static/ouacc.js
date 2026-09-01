document.addEventListener("DOMContentLoaded", function () {
    const nav = document.getElementById("main-nav");
    const toggle = document.querySelector(".nav-toggle");
    const groups = document.querySelectorAll(".nav-group");

    if (toggle && nav) {
        toggle.addEventListener("click", function () {
            const open = toggle.getAttribute("aria-expanded") === "true";
            toggle.setAttribute("aria-expanded", String(!open));
            nav.classList.toggle("is-open", !open);
        });
    }

    groups.forEach(function (group) {
        const button = group.querySelector(".nav-caret");
        if (!button) return;
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const open = group.classList.contains("is-open");
            groups.forEach(function (other) {
                other.classList.remove("is-open");
                const b = other.querySelector(".nav-caret");
                if (b) b.setAttribute("aria-expanded", "false");
            });
            group.classList.toggle("is-open", !open);
            button.setAttribute("aria-expanded", String(!open));
        });
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            groups.forEach(function (group) {
                group.classList.remove("is-open");
                const button = group.querySelector(".nav-caret");
                if (button) button.setAttribute("aria-expanded", "false");
            });
            if (toggle && nav) {
                toggle.setAttribute("aria-expanded", "false");
                nav.classList.remove("is-open");
            }
        }
    });
});
