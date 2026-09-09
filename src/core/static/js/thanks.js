(function () {
  "use strict";
  // Чистимо кошик лише після реального замовлення цього відвідувача.
  // Інакше /thanks/чужий-номер/ стирає поточні покупки.
  if (document.querySelector("[data-clear-cart]") && window.Cart) window.Cart.clear();
})();
