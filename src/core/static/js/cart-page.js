(function () {
  "use strict";

  function renderCart() {
    const root = document.querySelector("[data-cart-root]");
    if (!root) return;
    const catalogUrl = root.getAttribute("data-catalog-url") || "/";
    const checkoutUrl = root.getAttribute("data-checkout-url") || "/";

    const items = window.Cart.getItems()
      .map((i) => ({ ...i, product: window.getProductBySku(i.sku) }))
      .filter((i) => i.product);

    if (!items.length) {
      root.innerHTML = `
        <div class="empty-state">
          <h2>Кошик порожній</h2>
          <p>Додайте зарядну станцію з каталогу.</p>
          <a class="btn btn-primary" href="${catalogUrl}">До каталогу</a>
        </div>`;
      return;
    }

    const rows = items
      .map(
        (i) => `
      <article class="cart-item" data-sku="${i.sku}">
        <a href="${i.product.url}"><img src="${i.product.image}" alt="${i.product.name}"></a>
        <div>
          <a class="cart-item__title" href="${i.product.url}">${i.product.name}</a>
          <div class="cart-item__meta">${i.product.sku} · ${i.product.short}</div>
          <div class="qty">
            <button type="button" data-minus aria-label="Менше">−</button>
            <input type="number" value="${i.qty}" min="1" inputmode="numeric" data-qty>
            <button type="button" data-plus aria-label="Більше">+</button>
          </div>
          <button class="cart-item__remove" type="button" data-remove>Видалити</button>
        </div>
        <div class="cart-item__side">
          <strong class="price">${window.formatPrice(i.product.price * i.qty)}</strong>
        </div>
      </article>`
      )
      .join("");

    const total = window.Cart.total();
    root.innerHTML = `
      <div class="cart-layout">
        <div>${rows}</div>
        <aside class="summary">
          <h2>Разом</h2>
          <div class="summary-row"><span>Товари (з ПДВ)</span><span>${window.formatPrice(total)}</span></div>
          <div class="summary-row summary-vat"><span>в т.ч. ПДВ 20%</span><span>${window.formatPrice(window.vatFromGross(total))}</span></div>
          <div class="summary-row"><span>Доставка</span><span>за тарифами НП</span></div>
          <div class="summary-row summary-total"><span>До сплати</span><span>${window.formatPrice(total)}</span></div>
          <a class="btn btn-primary btn-block" href="${checkoutUrl}">Оформити замовлення</a>
          <a class="btn btn-secondary btn-block" href="${catalogUrl}">Продовжити покупки</a>
        </aside>
      </div>`;
  }

  document.addEventListener("DOMContentLoaded", () => {
    const root = document.querySelector("[data-cart-root]");
    if (!root) return;
    renderCart();

    root.addEventListener("click", (e) => {
      const item = e.target.closest(".cart-item");
      if (!item) return;
      const sku = item.getAttribute("data-sku");
      if (e.target.matches("[data-remove]")) {
        window.Cart.remove(sku);
        renderCart();
      }
      if (e.target.matches("[data-minus]")) {
        const input = item.querySelector("[data-qty]");
        window.Cart.setQty(sku, Math.max(1, (parseInt(input.value, 10) || 1) - 1));
        renderCart();
      }
      if (e.target.matches("[data-plus]")) {
        const input = item.querySelector("[data-qty]");
        window.Cart.setQty(sku, (parseInt(input.value, 10) || 1) + 1);
        renderCart();
      }
    });

    root.addEventListener("change", (e) => {
      if (!e.target.matches("[data-qty]")) return;
      const item = e.target.closest(".cart-item");
      window.Cart.setQty(item.getAttribute("data-sku"), e.target.value);
      renderCart();
    });
  });

  window.addEventListener("euromaxi:cart", renderCart);
})();
