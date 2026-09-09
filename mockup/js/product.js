(function () {
  function qs(name) {
    return new URLSearchParams(location.search).get(name);
  }

  document.addEventListener("DOMContentLoaded", () => {
    const root = document.querySelector("[data-product-root]");
    if (!root) return;
    const product = window.getProductById(qs("id")) || window.EUROMAXI_PRODUCTS[0];
    if (!product) {
      root.innerHTML =
        '<div class="empty-state"><h2>Товар не знайдено</h2><a class="btn btn-primary" href="catalog.html">До каталогу</a></div>';
      return;
    }

    document.title = `${product.name} — Euromaxi UA`;

    const badges = [];
    if (product.hit) badges.push('<span class="badge badge-hit">Хіт</span>');
    if (product.isNew) badges.push('<span class="badge badge-new">Новинка</span>');
    if (product.sale) badges.push('<span class="badge badge-sale">Акція</span>');

    const thumbs = product.images
      .map(
        (src, i) =>
          `<button type="button" class="${i === 0 ? "is-active" : ""}" data-thumb="${src}"><img src="${src}" alt=""></button>`
      )
      .join("");

    root.innerHTML = `
      <nav class="breadcrumbs" aria-label="Хлібні крихти">
        <a href="index.html">Головна</a><span aria-hidden="true">/</span>
        <a href="catalog.html">Каталог</a><span aria-hidden="true">/</span>
        <span>${product.name}</span>
      </nav>
      <div class="product-layout">
        <div class="gallery">
          <div class="gallery-main"><img data-main-img src="${product.image}" alt="${product.name}"></div>
          <div class="gallery-thumbs">${thumbs}</div>
        </div>
        <div class="product-info">
          <div class="product-info__brand">${product.brand}</div>
          <h1>${product.name}</h1>
          <div class="product-info__badges">${badges.join("")}</div>
          <div class="product-info__sku">Артикул: ${product.sku}</div>
          <div class="product-info__stock is-in">В наявності</div>
          <div class="product-info__price">
            <span class="price">${window.formatPrice(product.price)}</span>
            ${product.oldPrice ? `<span class="price-old">${window.formatPrice(product.oldPrice)}</span>` : ""}
            <span class="price-vat">з ПДВ</span>
          </div>
          <div class="specs">
            <div class="spec-row"><span class="spec-label">Ємність акумулятора</span><span class="spec-value">${product.capacity} Вт·год</span></div>
            <div class="spec-row"><span class="spec-label">Номінальна (робоча) потужність</span><span class="spec-value">${product.power} Вт</span></div>
            <div class="spec-row"><span class="spec-label">Тип акумуляторної батареї</span><span class="spec-value">${product.batteryType}</span></div>
            <div class="spec-row"><span class="spec-label">Вихідні інтерфейси (розʼєми)</span><span class="spec-value">${product.outputs}</span></div>
            <div class="spec-row"><span class="spec-label">Способи зарядки</span><span class="spec-value">${product.charging}</span></div>
            <div class="spec-row"><span class="spec-label">Додаткові функції</span><span class="spec-value">${product.features}</span></div>
            <div class="spec-row"><span class="spec-label">Вага</span><span class="spec-value">${product.weight} кг</span></div>
            <div class="spec-row"><span class="spec-label">Розмір</span><span class="spec-value">${product.size}</span></div>
            <div class="spec-row"><span class="spec-label">Робоча температура</span><span class="spec-value">${product.temp}</span></div>
          </div>
          <div class="product-buy">
            <div class="qty" data-qty>
              <button type="button" data-qty-minus aria-label="Менше">−</button>
              <input type="number" value="1" min="1" inputmode="numeric" aria-label="Кількість">
              <button type="button" data-qty-plus aria-label="Більше">+</button>
            </div>
            <button class="btn btn-primary" type="button" data-buy>Додати до кошика</button>
            <a class="btn btn-outline" href="checkout.html">Оформити</a>
          </div>
          <div class="product-desc">
            <h2>Опис</h2>
            <p>${product.description}</p>
            <p>Ціна вказана з ПДВ (20%). Фото та тексти — заглушки для макета.</p>
          </div>
        </div>
      </div>
    `;

    const qtyInput = root.querySelector("[data-qty] input");
    root.querySelector("[data-qty-minus]").addEventListener("click", () => {
      qtyInput.value = Math.max(1, (parseInt(qtyInput.value, 10) || 1) - 1);
    });
    root.querySelector("[data-qty-plus]").addEventListener("click", () => {
      qtyInput.value = (parseInt(qtyInput.value, 10) || 1) + 1;
    });

    root.querySelector("[data-buy]").addEventListener("click", () => {
      const qty = Math.max(1, parseInt(qtyInput.value, 10) || 1);
      window.Cart.add(product.id, qty);
      document.querySelectorAll("[data-cart-count]").forEach((el) => {
        el.textContent = String(window.Cart.count());
      });
      window.showToast("Додано до кошика");
    });

    root.querySelectorAll("[data-thumb]").forEach((btn) => {
      btn.addEventListener("click", () => {
        root.querySelectorAll("[data-thumb]").forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");
        root.querySelector("[data-main-img]").src = btn.getAttribute("data-thumb");
      });
    });
  });
})();
