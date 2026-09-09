(function () {
  const KEY = "chargua_cart_v1";

  function read() {
    try {
      return JSON.parse(localStorage.getItem(KEY) || "[]");
    } catch (e) {
      return [];
    }
  }

  function write(items) {
    localStorage.setItem(KEY, JSON.stringify(items));
    window.dispatchEvent(new CustomEvent("chargua:cart"));
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
        const p = window.getProductById(i.id);
        return sum + (p ? p.price * i.qty : 0);
      }, 0);
    },
    add(id, qty) {
      const items = read();
      const found = items.find((i) => i.id === id);
      const nextQty = Math.max(1, qty || 1);
      if (found) found.qty += nextQty;
      else items.push({ id, qty: nextQty });
      write(items);
    },
    setQty(id, qty) {
      let items = read();
      const q = Math.max(1, parseInt(qty, 10) || 1);
      items = items
        .map((i) => (i.id === id ? { ...i, qty: q } : i))
        .filter((i) => i.qty > 0);
      write(items);
    },
    remove(id) {
      write(read().filter((i) => i.id !== id));
    },
    clear() {
      write([]);
    }
  };
})();
