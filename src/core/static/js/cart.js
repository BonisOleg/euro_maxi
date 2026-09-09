(function () {
  "use strict";
  const KEY = "euromaxi_cart_v1";

  function read() {
    try {
      return JSON.parse(localStorage.getItem(KEY) || "[]");
    } catch (e) {
      return [];
    }
  }

  function write(items) {
    localStorage.setItem(KEY, JSON.stringify(items));
    window.dispatchEvent(new CustomEvent("euromaxi:cart"));
  }

  function catalog() {
    const el = document.getElementById("cart-catalog-data");
    if (!el) return [];
    try {
      return JSON.parse(el.textContent) || [];
    } catch (e) {
      return [];
    }
  }

  window.getProductBySku = function getProductBySku(sku) {
    return catalog().find((p) => p.sku === sku) || null;
  };

  window.formatPrice = function formatPrice(value) {
    return new Intl.NumberFormat("uk-UA").format(Math.round(Number(value) || 0)) + " ₴";
  };

  window.VAT_RATE = 0.2;
  window.MAX_CART_QTY = 20;
  window.vatFromGross = function vatFromGross(gross) {
    const rate = window.VAT_RATE || 0.2;
    return Math.round(((Number(gross) || 0) * rate) / (1 + rate));
  };

  function clampQty(qty) {
    const max = window.MAX_CART_QTY || 20;
    return Math.min(max, Math.max(1, parseInt(qty, 10) || 1));
  }

  window.Cart = {
    getItems() {
      return read();
    },
    count() {
      return read().reduce((sum, i) => sum + i.qty, 0);
    },
    total() {
      return read().reduce((sum, i) => {
        const p = window.getProductBySku(i.sku);
        return sum + (p ? p.price * i.qty : 0);
      }, 0);
    },
    add(sku, qty) {
      const items = read();
      const found = items.find((i) => i.sku === sku);
      const nextQty = clampQty(qty || 1);
      if (found) found.qty = clampQty(found.qty + nextQty);
      else items.push({ sku, qty: nextQty });
      write(items);
    },
    setQty(sku, qty) {
      let items = read();
      const q = clampQty(qty);
      items = items.map((i) => (i.sku === sku ? { ...i, qty: q } : i)).filter((i) => i.qty > 0);
      write(items);
    },
    remove(sku) {
      write(read().filter((i) => i.sku !== sku));
    },
    clear() {
      write([]);
    },
  };
})();
