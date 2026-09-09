(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector("[data-filters-toggle]");
    const filters = document.querySelector(".filters");
    if (toggle && filters) {
      toggle.addEventListener("click", () => filters.classList.toggle("is-open"));
    }

    const reset = document.querySelector("[data-filters-reset]");
    const form = document.getElementById("catalog-filter-form");
    if (reset && form) {
      reset.addEventListener("click", () => {
        form.querySelectorAll("input[type='checkbox']").forEach((i) => {
          i.checked = false;
        });
        const sort = document.getElementById("sort");
        if (sort) sort.value = "";
        if (window.htmx) window.htmx.trigger(form, "change");
      });
    }
  });
})();
