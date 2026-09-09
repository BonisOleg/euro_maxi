(function () {
  "use strict";
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-thumb]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const gallery = btn.closest(".gallery");
        if (!gallery) return;
        gallery.querySelectorAll("[data-thumb]").forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");
        const main = gallery.querySelector("[data-main-img]");
        if (main) main.src = btn.getAttribute("data-thumb");
      });
    });
  });
})();
