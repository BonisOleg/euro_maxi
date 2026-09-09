(function () {
  const path = location.pathname.split("/").pop() || "index.html";

  function headerHtml() {
    return `
      <div class="header-top">
        <div class="container">
          <a href="delivery.html">Доставка і оплата</a>
          <a href="about.html">Про нас</a>
          <a href="contacts.html">Контакти</a>
          <a href="offer.html">Оферта</a>
          <a href="privacy.html">Конфіденційність</a>
        </div>
      </div>
      <div class="container header-main">
        <button class="nav-toggle" type="button" aria-label="Меню" data-nav-open>
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
        </button>
        <a class="logo" href="index.html" aria-label="Euromaxi UA">
          <span class="logo-word">Euromaxi UA</span>
          <span class="logo-tag">power stations</span>
        </a>
        <a class="btn-catalog" href="catalog.html">
          <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="8" rx="1.5"/><rect x="3" y="13" width="8" height="8" rx="1.5"/><rect x="13" y="13" width="8" height="8" rx="1.5"/></svg>
          Каталог товарів
        </a>
        <form class="header-search" action="search.html" method="get" role="search">
          <label class="sr-only" for="q">Пошук</label>
          <input id="q" name="q" type="search" placeholder="Я хочу знайти" enterkeyhint="search">
          <button type="submit" aria-label="Знайти">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
          </button>
        </form>
        <div class="header-actions">
          <a class="header-phone" href="tel:+380000000000">+38 (000) 000-00-00</a>
          <a class="icon-btn" href="cart.html" aria-label="Кошик">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6h15l-1.5 9h-12z"/><path d="M6 6l-2-3H2"/><circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/></svg>
            <span class="cart-count" data-cart-count>0</span>
          </a>
        </div>
      </div>
      <div class="container mobile-search-row">
        <form class="header-search" action="search.html" method="get" role="search">
          <label class="sr-only" for="q-m">Пошук</label>
          <input id="q-m" name="q" type="search" placeholder="Я хочу знайти" enterkeyhint="search">
          <button type="submit" aria-label="Знайти">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
          </button>
        </form>
      </div>
      <div class="mobile-nav" data-mobile-nav>
        <div class="mobile-nav-panel">
          <a class="logo" href="index.html"><span class="logo-word">Euromaxi UA</span><span class="logo-tag">power stations</span></a>
          <a href="catalog.html">Каталог товарів</a>
          <a href="catalog.html?brand=Jackery">Jackery</a>
          <a href="catalog.html?brand=Bluetti">Bluetti</a>
          <a href="catalog.html?brand=Anker">Anker</a>
          <a href="cart.html">Кошик</a>
          <a href="delivery.html">Доставка і оплата</a>
          <a href="about.html">Про нас</a>
          <a href="contacts.html">Контакти</a>
          <a href="offer.html">Оферта</a>
          <a href="privacy.html">Конфіденційність</a>
          <a href="tel:+380000000000">+38 (000) 000-00-00</a>
        </div>
      </div>
    `;
  }

  function footerHtml() {
    return `
      <div class="container footer-grid">
        <div class="footer-brand">
          <a class="logo" href="index.html"><span class="logo-word">Euromaxi UA</span><span class="logo-tag">power stations</span></a>
          <p>Побутові портативні зарядні станції Jackery, Bluetti, Anker. Білий фон, сині написи; назви товарів — чорні.</p>
        </div>
        <div class="footer-col">
          <h3>Каталог</h3>
          <a href="catalog.html">Зарядні станції</a>
          <a href="catalog.html?brand=Jackery">Jackery</a>
          <a href="catalog.html?brand=Bluetti">Bluetti</a>
          <a href="catalog.html?brand=Anker">Anker</a>
        </div>
        <div class="footer-col">
          <h3>Euromaxi UA</h3>
          <a href="about.html">Про нас</a>
          <a href="contacts.html">Контакти</a>
          <a href="delivery.html">Доставка і оплата</a>
        </div>
        <div class="footer-col">
          <h3>Покупцям</h3>
          <a href="offer.html">Договір оферти</a>
          <a href="privacy.html">Політика конфіденційності</a>
          <a href="checkout.html">Оформлення</a>
        </div>
      </div>
      <div class="container footer-bottom">
        <span>© 2026 Euromaxi UA · макет</span>
        <span>Оплата: Monobank · Доставка: Нова Пошта</span>
      </div>
    `;
  }

  function mountChrome() {
    const header = document.querySelector("[data-site-header]");
    const footer = document.querySelector("[data-site-footer]");
    if (header) header.innerHTML = headerHtml();
    if (footer) footer.innerHTML = footerHtml();
  }

  function updateCartCount() {
    document.querySelectorAll("[data-cart-count]").forEach((el) => {
      el.textContent = String(window.Cart ? window.Cart.count() : 0);
    });
  }

  function bindNav() {
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

  window.renderProductCard = function renderProductCard(p) {
    const badges = [];
    if (p.hit) badges.push('<span class="badge badge-hit">Хіт</span>');
    if (p.isNew) badges.push('<span class="badge badge-new">Новинка</span>');
    if (p.sale) badges.push('<span class="badge badge-sale">Акція</span>');
    const old = p.oldPrice
      ? `<span class="price-old">${window.formatPrice(p.oldPrice)}</span>`
      : "";
    return `
      <article class="product-card">
        <a class="product-card__media" href="product.html?id=${encodeURIComponent(p.id)}">
          <div class="product-card__badges">${badges.join("")}</div>
          <img src="${p.image}" alt="${p.name}" loading="lazy" width="400" height="400">
        </a>
        <div class="product-card__body">
          <a class="product-card__title" href="product.html?id=${encodeURIComponent(p.id)}">${p.name}</a>
          <div class="product-card__meta">${p.short}</div>
          <div class="product-card__price-row">
            <span class="price">${window.formatPrice(p.price)}</span>${old}
          </div>
          <div class="price-vat">з ПДВ</div>
          <button class="btn btn-primary btn-block" type="button" data-add="${p.id}">Купити</button>
        </div>
      </article>
    `;
  };

  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-add]");
    if (!btn || !window.Cart) return;
    window.Cart.add(btn.getAttribute("data-add"), 1);
    updateCartCount();
    window.showToast("Додано до кошика");
  });

  document.addEventListener("DOMContentLoaded", () => {
    mountChrome();
    bindNav();
    updateCartCount();
    void path;
  });

  window.addEventListener("chargua:cart", updateCartCount);
})();
