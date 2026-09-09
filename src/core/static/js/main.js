(function () {
  "use strict";

  function updateCartCount() {
    document.querySelectorAll("[data-cart-count]").forEach((el) => {
      el.textContent = String(window.Cart ? window.Cart.count() : 0);
    });
  }

  function bindMobileNav() {
    const mobile = document.querySelector("[data-mobile-nav]");
    const openBtn = document.querySelector("[data-nav-open]");
    if (!mobile || !openBtn) return;
    openBtn.addEventListener("click", () => mobile.classList.add("is-open"));
    mobile.addEventListener("click", (e) => {
      if (e.target === mobile) mobile.classList.remove("is-open");
    });
  }

  window.showToast = function showToast(text) {
    let el = document.querySelector(".toast");
    if (!el) {
      el = document.createElement("div");
      el.className = "toast";
      document.body.appendChild(el);
    }
    el.textContent = text;
    el.classList.add("is-visible");
    clearTimeout(window.__toastTimer);
    window.__toastTimer = setTimeout(() => el.classList.remove("is-visible"), 2200);
  };

  function qtyFromWidget(el) {
    const widget = el.closest("[data-buy-widget]");
    const qtyField = widget ? widget.querySelector("[data-qty] input") : null;
    return qtyField ? Math.max(1, parseInt(qtyField.value, 10) || 1) : 1;
  }

  document.addEventListener("click", (e) => {
    const buyNow = e.target.closest("[data-buy-now]");
    if (buyNow && window.Cart) {
      const sku = buyNow.getAttribute("data-buy-now");
      if (sku && !window.Cart.getItems().some((i) => i.sku === sku)) {
        window.Cart.add(sku, qtyFromWidget(buyNow));
        updateCartCount();
      }
      return;
    }
    const btn = e.target.closest("[data-add]");
    if (!btn || !window.Cart) return;
    const sku = btn.getAttribute("data-add");
    window.Cart.add(sku, qtyFromWidget(btn));
    updateCartCount();
    window.showToast("Додано до кошика");
  });

  document.addEventListener("click", (e) => {
    const stepBtn = e.target.closest("[data-qty-plus], [data-qty-minus]");
    if (!stepBtn) return;
    const wrap = stepBtn.closest("[data-qty]");
    const input = wrap ? wrap.querySelector("input") : null;
    if (!input) return;
    const delta = stepBtn.hasAttribute("data-qty-plus") ? 1 : -1;
    input.value = Math.max(1, (parseInt(input.value, 10) || 1) + delta);
  });

  document.addEventListener("DOMContentLoaded", () => {
    bindMobileNav();
    updateCartCount();
  });

  window.addEventListener("euromaxi:cart", updateCartCount);
})();
