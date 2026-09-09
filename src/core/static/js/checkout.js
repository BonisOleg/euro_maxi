(function () {
  "use strict";

  function renderSummary() {
    const box = document.querySelector("[data-checkout-summary]");
    if (!box) return;
    const catalogUrl = box.getAttribute("data-catalog-url") || "/";
    const items = window.Cart.getItems()
      .map((i) => ({ ...i, product: window.getProductBySku(i.sku) }))
      .filter((i) => i.product);

    if (!items.length) {
      box.innerHTML = `
        <h2>Ваше замовлення</h2>
        <p>Кошик порожній.</p>
        <a class="btn btn-secondary btn-block" href="${catalogUrl}">До каталогу</a>`;
      return;
    }

    const list = items
      .map(
        (i) =>
          `<div class="summary-row"><span>${i.product.name} × ${i.qty}</span><span>${window.formatPrice(i.product.price * i.qty)}</span></div>`
      )
      .join("");

    const total = window.Cart.total();
    const vat = window.vatFromGross(total);
    box.innerHTML = `
      <h2>Ваше замовлення</h2>
      ${list}
      <div class="summary-row summary-vat"><span>в т.ч. ПДВ 20%</span><span>${window.formatPrice(vat)}</span></div>
      <div class="summary-row"><span>Доставка</span><span>НП (розрахунок)</span></div>
      <div class="summary-row summary-total"><span>Разом (з ПДВ)</span><span>${window.formatPrice(total)}</span></div>`;
  }

  function validate(form) {
    let ok = true;
    form.querySelectorAll(".field").forEach((field) => {
      const input = field.querySelector("input, select, textarea");
      if (!input || !input.required) return;
      const valid =
        input.type === "email"
          ? input.value.trim() === "" || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value.trim())
          : input.value.trim().length > 0;
      field.classList.toggle("is-invalid", !valid);
      if (!valid) ok = false;
    });

    const agree = form.querySelector("#id_agree, [name='agree']");
    const agreeField = form.querySelector("[data-agree-field]");
    if (agree && agreeField) {
      agreeField.classList.toggle("is-invalid", !agree.checked);
      if (!agree.checked) ok = false;
    }
    return ok;
  }

  document.addEventListener("DOMContentLoaded", () => {
    renderSummary();
    const form = document.querySelector("[data-checkout-form]");
    if (!form) return;

    form.addEventListener("submit", (e) => {
      if (form.getAttribute("data-submitting") === "1") {
        e.preventDefault();
        return;
      }
      const items = window.Cart.getItems();
      if (!items.length) {
        e.preventDefault();
        window.showToast("Спочатку додайте товари");
        return;
      }
      if (!validate(form)) {
        e.preventDefault();
        window.showToast("Перевірте обовʼязкові поля");
        return;
      }
      const cartInput = form.querySelector("[data-cart-data-input]");
      if (cartInput) cartInput.value = JSON.stringify(items);
      form.setAttribute("data-submitting", "1");
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;
    });
  });
})();
