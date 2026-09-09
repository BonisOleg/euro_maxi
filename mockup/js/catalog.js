(function () {
  function params() {
    return new URLSearchParams(location.search);
  }

  function selectedValues(name) {
    return [...document.querySelectorAll(`input[name="${name}"]:checked`)].map((i) => i.value);
  }

  function inPowerRange(value, range) {
    if (range === "0-500") return value <= 500;
    if (range === "501-1500") return value >= 501 && value <= 1500;
    if (range === "1501+") return value >= 1501;
    return true;
  }

  function inCapacityRange(value, range) {
    if (range === "0-500") return value <= 500;
    if (range === "501-1000") return value >= 501 && value <= 1000;
    if (range === "1001+") return value >= 1001;
    return true;
  }

  function applyFilters(list) {
    const brands = selectedValues("brand");
    const powers = selectedValues("power");
    const batteries = selectedValues("battery");
    const capacities = selectedValues("capacity");
    let result = list.slice();

    const brandParam = params().get("brand");
    if (brandParam && !brands.length) {
      result = result.filter((p) => p.brand.toLowerCase() === brandParam.toLowerCase());
    } else if (brands.length) {
      result = result.filter((p) => brands.includes(p.brand));
    }

    if (powers.length) {
      result = result.filter((p) => powers.some((range) => inPowerRange(p.power, range)));
    }

    if (batteries.length) {
      result = result.filter((p) => batteries.includes(p.batteryType));
    }

    if (capacities.length) {
      result = result.filter((p) => capacities.some((range) => inCapacityRange(p.capacity, range)));
    }

    const sort = document.getElementById("sort")?.value || "popular";
    if (sort === "price-asc") result.sort((a, b) => a.price - b.price);
    if (sort === "price-desc") result.sort((a, b) => b.price - a.price);
    if (sort === "power-desc") result.sort((a, b) => b.power - a.power);
    if (sort === "capacity-desc") result.sort((a, b) => b.capacity - a.capacity);
    if (sort === "popular") result.sort((a, b) => Number(b.hit) - Number(a.hit) || b.price - a.price);

    return result;
  }

  function render() {
    const grid = document.querySelector("[data-catalog-grid]");
    const count = document.querySelector("[data-catalog-count]");
    if (!grid) return;
    const items = applyFilters(window.EUROMAXI_PRODUCTS || []);
    grid.innerHTML =
      items.map(window.renderProductCard).join("") ||
      '<div class="empty-state"><h2>Нічого не знайдено</h2><p>Скиньте фільтри або змініть умови пошуку.</p></div>';
    if (count) count.textContent = `Знайдено: ${items.length}`;
  }

  document.addEventListener("DOMContentLoaded", () => {
    const brandParam = params().get("brand");
    if (brandParam) {
      const input = document.querySelector(`input[name="brand"][value="${brandParam}"]`);
      if (input) input.checked = true;
    }

    document.querySelectorAll(".filters input, #sort").forEach((el) => {
      el.addEventListener("change", render);
    });

    const toggle = document.querySelector("[data-filters-toggle]");
    const filters = document.querySelector(".filters");
    if (toggle && filters) {
      toggle.addEventListener("click", () => filters.classList.toggle("is-open"));
    }

    const reset = document.querySelector("[data-filters-reset]");
    if (reset) {
      reset.addEventListener("click", () => {
        document.querySelectorAll(".filters input").forEach((i) => {
          i.checked = false;
        });
        render();
      });
    }

    render();
  });
})();
