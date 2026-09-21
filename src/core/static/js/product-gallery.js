(function () {
  "use strict";

  function pathOf(src) {
    try {
      return new URL(src, window.location.href).pathname;
    } catch (err) {
      return src;
    }
  }

  function sourcesOf(gallery) {
    const thumbs = [...gallery.querySelectorAll("[data-thumb]")];
    if (thumbs.length) {
      return thumbs.map((btn) => btn.getAttribute("data-thumb")).filter(Boolean);
    }
    const main = gallery.querySelector("[data-main-img]");
    return main && main.src ? [main.src] : [];
  }

  function initGallery(gallery) {
    const main = gallery.querySelector("[data-main-img]");
    const openBtn = gallery.querySelector("[data-gallery-open]");
    const lightbox = gallery.querySelector("[data-lightbox]");
    if (!main || !openBtn || !lightbox) return;

    const lightboxImg = lightbox.querySelector("[data-lightbox-img]");
    const countEl = lightbox.querySelector("[data-lightbox-count]");
    const prevBtn = lightbox.querySelector("[data-lightbox-prev]");
    const nextBtn = lightbox.querySelector("[data-lightbox-next]");
    const backdrop = lightbox.querySelector("[data-lightbox-backdrop]");
    const closeBtns = lightbox.querySelectorAll("[data-lightbox-close]");
    const thumbs = [...gallery.querySelectorAll("[data-thumb]")];

    let index = 0;
    let ignoreClose = false;
    let scrollY = 0;

    document.body.appendChild(lightbox);

    function sources() {
      return sourcesOf(gallery);
    }

    function setIndex(next) {
      const list = sources();
      if (!list.length) return;
      index = (next + list.length) % list.length;
      const src = list[index];
      main.src = src;
      lightboxImg.src = src;
      thumbs.forEach((btn, i) => btn.classList.toggle("is-active", i === index));
      if (countEl) {
        countEl.textContent = list.length > 1 ? `${index + 1} / ${list.length}` : "";
      }
      const multi = list.length > 1;
      if (prevBtn) prevBtn.hidden = !multi;
      if (nextBtn) nextBtn.hidden = !multi;
    }

    function open() {
      const list = sources();
      if (!list.length) return;
      const current = pathOf(main.src);
      const found = list.findIndex((src) => pathOf(src) === current);
      ignoreClose = true;
      lightbox.hidden = false;
      scrollY = window.scrollY;
      document.body.classList.add("is-lightbox-open");
      document.body.style.top = `-${scrollY}px`;
      setIndex(found >= 0 ? found : 0);
      lightbox.querySelector("[data-lightbox-close]")?.focus();
    }

    function close() {
      if (lightbox.hidden) return;
      lightbox.hidden = true;
      document.body.classList.remove("is-lightbox-open");
      document.body.style.top = "";
      window.scrollTo(0, scrollY);
      openBtn.focus();
    }

    thumbs.forEach((btn, i) => {
      btn.addEventListener("click", () => setIndex(i));
    });

    openBtn.addEventListener("pointerdown", (event) => {
      event.stopPropagation();
      open();
    });
    openBtn.addEventListener("click", (event) => {
      event.preventDefault();
      if (lightbox.hidden) open();
    });

    document.addEventListener("pointerup", () => {
      window.setTimeout(() => {
        ignoreClose = false;
      }, 0);
    });

    backdrop?.addEventListener("pointerup", (event) => {
      if (ignoreClose) return;
      if (event.target === backdrop) close();
    });

    closeBtns.forEach((btn) => {
      btn.addEventListener("click", close);
    });

    prevBtn?.addEventListener("click", () => setIndex(index - 1));
    nextBtn?.addEventListener("click", () => setIndex(index + 1));

    document.addEventListener("keydown", (event) => {
      if (lightbox.hidden) return;
      if (event.key === "Escape") close();
      if (event.key === "ArrowLeft") setIndex(index - 1);
      if (event.key === "ArrowRight") setIndex(index + 1);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-gallery]").forEach(initGallery);
  });
})();
