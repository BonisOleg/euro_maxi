(function () {
  function renderSummary() {
    const box = document.querySelector("[data-checkout-summary]");
    if (!box) return;
    const items = window.Cart.getItems()
      .map((i) => ({ ...i, product: window.getProductById(i.id) }))
      .filter((i) => i.product);

    if (!items.length) {
      box.innerHTML = `
        <h2>Ваше замовлення</h2>
        <p>Кошик порожній.</p>
        <a class="btn btn-secondary btn-block" href="catalog.html">До каталогу</a>`;
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
      const valid = input.type === "email"
        ? /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value.trim())
        : input.value.trim().length > 0;
      field.classList.toggle("is-invalid", !valid);
      if (!valid) ok = false;
    });

    const agree = form.querySelector("#agree");
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
      e.preventDefault();
      if (!window.Cart.getItems().length) {
        window.showToast("Спочатку додайте товари");
        return;
      }
      if (!validate(form)) {
        window.showToast("Перевірте обовʼязкові поля");
        return;
      }
      const order = {
        id: "CUA-" + Date.now().toString().slice(-8),
        total: window.Cart.total(),
        payment: "Monobank",
        name: form.fullName.value.trim(),
        email: form.email.value.trim()
      };
      sessionStorage.setItem("chargua_last_order", JSON.stringify(order));
      window.Cart.clear();
      location.href = "thanks.html";
    });
  });
})();
