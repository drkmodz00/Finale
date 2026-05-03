/* ─────────────────────────────────────────────
   STATE & REFS
───────────────────────────────────────────── */
let cartIcon = null;
let toastTimer = null;

document.addEventListener("DOMContentLoaded", () => {
  // Match the same cart icon selector the homepage uses
  cartIcon = document.getElementById("cartIcon")
          || document.querySelector('[href="{% url "cart" %}"]')
          || document.querySelector("[data-cart-icon]")
          || document.querySelector(".cart-icon");

  /* ── Modal add-to-cart ── */
  document.getElementById("modalAddToCart").addEventListener("click", function () {
    const url = this.dataset.url;
    if (!url) return;

    const img    = document.getElementById("modalProductImage");
    const rect   = img.getBoundingClientRect();
    const cx     = rect.left + rect.width  / 2;
    const cy     = rect.top  + rect.height / 2;

    addToCart(url, img.src, cx, cy);
  });

  /* ── Card quick-add buttons ── */
  document.querySelectorAll(".add-to-cart-btn").forEach(btn => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();

      const url    = this.dataset.url;
      const card   = this.closest("[data-img]");
      const imgSrc = card?.dataset.img;

      // Fly from the center of the card image
      const cardImg = card?.querySelector(".prod-img");
      const rect    = (cardImg || this).getBoundingClientRect();
      const cx      = rect.left + rect.width  / 2;
      const cy      = rect.top  + rect.height / 2;

      addToCart(url, imgSrc, cx, cy);
    });
  });
});


/* ─────────────────────────────────────────────
   SIDEBAR TOGGLE
───────────────────────────────────────────── */
function toggleCat(id) {
  const el    = document.getElementById(`cat-${id}`);
  const arrow = document.getElementById(`arrow-${id}`);

  const isOpen = el.classList.contains("open");

  // Close all
  document.querySelectorAll(".cat-children").forEach(c => c.classList.remove("open"));
  document.querySelectorAll(".cat-arrow").forEach(a => a.classList.remove("rotated"));

  // Open this one if it was closed
  if (!isOpen) {
    el.classList.add("open");
    arrow.classList.add("rotated");
  }
}


/* ─────────────────────────────────────────────
   ADD TO CART  (no page reload)
───────────────────────────────────────────── */
async function addToCart(url, imgSrc, originX, originY) {
  // 1. Start the fly animation immediately (optimistic UI)
  flyToCart(imgSrc, originX, originY);

  // 2. AJAX request
  try {
    const res  = await fetch(url, {
      method:  "GET",
      headers: { "X-Requested-With": "XMLHttpRequest" }
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();

    // 3. Update cart badge
    updateCartBadge(data.cart_count);

    // 4. Show toast
    showToast("Added to cart!");

  } catch (err) {
    console.error("Add to cart failed:", err);
    showToast("Something went wrong.", true);
  }
}


/* ─────────────────────────────────────────────
   FLY-TO-CART ANIMATION
   Uses double-rAF so the browser paints the
   start state before transitioning to end state.
───────────────────────────────────────────── */
function flyToCart(imgSrc, originX, originY) {
  if (!imgSrc) return;

  // Same selector chain the homepage uses — covers all base template variants
  const cartEl = cartIcon
              || document.querySelector('[href="{% url "cart" %}"]');

  if (!cartEl) return;

  const SIZE_START = 56;
  const SIZE_END   = 18;

  const cartRect = cartEl.getBoundingClientRect();

  // Land dead-center on the cart icon
  const destX = cartRect.left + cartRect.width  / 2 - SIZE_END / 2;
  const destY = cartRect.top  + cartRect.height / 2 - SIZE_END / 2;

  // Build the ghost — identical class as homepage (.fly-ghost)
  const ghost = document.createElement("img");
  ghost.src       = imgSrc;
  ghost.className = "fly-ghost";

  // Paint at start position BEFORE any transition runs
  ghost.style.cssText = `
    left:          ${originX - SIZE_START / 2}px;
    top:           ${originY - SIZE_START / 2}px;
    width:         ${SIZE_START}px;
    height:        ${SIZE_START}px;
    opacity:       1;
    border-radius: 12px;
  `;

  document.body.appendChild(ghost);

  // Double rAF — browser must paint the start frame first
  // (same technique as the working homepage)
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      ghost.style.left         = `${destX}px`;
      ghost.style.top          = `${destY}px`;
      ghost.style.width        = `${SIZE_END}px`;
      ghost.style.height       = `${SIZE_END}px`;
      ghost.style.opacity      = "0";
      ghost.style.borderRadius = "50%";
    });
  });

  setTimeout(() => ghost.remove(), 780);
}


/* ─────────────────────────────────────────────
   CART BADGE
───────────────────────────────────────────── */
function updateCartBadge(count) {
  if (!cartIcon) return;

  let badge = cartIcon.querySelector("span");

  if (!badge) {
    badge = document.createElement("span");
    badge.className =
      "absolute -top-2 -right-2 bg-red-500 text-white text-[10px] " +
      "w-4 h-4 flex items-center justify-center rounded-full font-bold";
    cartIcon.style.position = "relative";
    cartIcon.appendChild(badge);
  }

  badge.innerText = count;

  // Pop animation
  badge.classList.remove("badge-pop");
  void badge.offsetWidth; // reflow
  badge.classList.add("badge-pop");
}


/* ─────────────────────────────────────────────
   TOAST NOTIFICATION
───────────────────────────────────────────── */
function showToast(message, isError = false) {
  const toast    = document.getElementById("toast");
  const toastMsg = document.getElementById("toastMsg");
  const icon     = toast.querySelector("i");

  toastMsg.textContent = message;
  icon.className = isError
    ? "fas fa-exclamation-circle text-red-400"
    : "fas fa-check-circle text-emerald-400";

  toast.classList.remove("hidden", "toast-out");
  toast.classList.add("toast-in");

  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove("toast-in");
    toast.classList.add("toast-out");
    setTimeout(() => toast.classList.add("hidden"), 320);
  }, 2200);
}


/* ─────────────────────────────────────────────
   MODAL
───────────────────────────────────────────── */
function showProduct(card) {
  const modal = document.getElementById("productModal");

  // Populate fields
  document.getElementById("modalProductName").innerText  = card.dataset.name    || "";
  document.getElementById("modalProductImage").src       = card.dataset.img     || "";
  document.getElementById("modalCategory").innerText     = card.dataset.category || "";
  document.getElementById("modalSupplier").innerText     = card.dataset.supplier || "";
  document.getElementById("modalStockQty").innerText     = card.dataset.stock   || "—";
  document.getElementById("modalUnit1").innerText        = card.dataset.unit    || "";
  document.getElementById("modalStatus").innerText       = card.dataset.status  || "";

  // Price
  const disc    = parseFloat(card.dataset.discount)     || 0;
  const final   = parseFloat(card.dataset.finalPrice)   || 0;
  const selling = parseFloat(card.dataset.sellingPrice) || 0;

  const priceWrap = document.getElementById("modalPriceWrapper");
  if (disc > 0) {
    priceWrap.innerHTML = `
      <span class="text-2xl font-bold text-red-500">₱${final.toFixed(2)}</span>
      <span class="text-base text-stone-400 line-through">₱${selling.toFixed(2)}</span>
      <span class="text-xs bg-red-50 text-red-500 font-bold px-2 py-0.5 rounded-full">${disc.toFixed(0)}% OFF</span>
    `;
    document.getElementById("modalDiscountRibbon").classList.remove("hidden");
    document.getElementById("modalDiscountBadge").textContent = `-${disc.toFixed(0)}%`;
  } else {
    priceWrap.innerHTML = `<span class="text-2xl font-bold text-stone-900">₱${selling.toFixed(2)}</span>`;
    document.getElementById("modalDiscountRibbon").classList.add("hidden");
  }

  // Status color
  const statusEl = document.getElementById("modalStatus");
  const status   = (card.dataset.status || "").toLowerCase();
  statusEl.className = "text-sm font-semibold " + (
    status.includes("available") || status.includes("active") || status.includes("in stock")
      ? "text-emerald-600"
      : status.includes("out") || status.includes("unavailable")
        ? "text-red-500"
        : "text-stone-800"
  );

  // Store URL for add-to-cart
  document.getElementById("modalAddToCart").dataset.url = card.dataset.url;

  // Show modal
  modal.style.display = "flex";
  requestAnimationFrame(() => modal.classList.add("modal-visible"));
  document.body.style.overflow = "hidden";
}

function closeModal() {
  const modal = document.getElementById("productModal");
  modal.classList.remove("modal-visible");
  modal.style.opacity = "0";
  setTimeout(() => {
    modal.style.display  = "none";
    modal.style.opacity  = "";
    document.body.style.overflow = "";
  }, 220);
}

// ESC key closes modal
document.addEventListener("keydown", e => {
  if (e.key === "Escape") closeModal();
});
/* ─────────────────────────────
   HERO SLIDER AUTO ROTATE
───────────────────────────── */
window.heroIndex = window.heroIndex ?? 0;

function showHeroSlide(index) {
  const slides = document.querySelectorAll(".hero-slide");
  const dots = document.querySelectorAll(".dot");

  slides.forEach((slide, i) => {
    slide.style.opacity = (i === index) ? "1" : "0";
  });

  dots.forEach((dot, i) => {
    dot.className = (i === index)
      ? "dot w-2 h-2 rounded-full bg-white"
      : "dot w-2 h-2 rounded-full bg-white/40";
  });
}

function nextHeroSlide() {
  const slides = document.querySelectorAll(".hero-slide");
  window.heroIndex = (window.heroIndex + 1) % slides.length;
  showHeroSlide(window.heroIndex);
}

document.addEventListener("DOMContentLoaded", () => {
  showHeroSlide(0);

  // prevent multiple intervals stacking
  if (!window.heroIntervalStarted) {
    window.heroIntervalStarted = true;
    setInterval(nextHeroSlide, 5000);
  }
});

document.querySelectorAll(".subcategory-link").forEach(link => {
    link.addEventListener("click", () => {
        sessionStorage.setItem("scrollPos", window.scrollY);
    });
});

window.addEventListener("load", () => {
    const pos = sessionStorage.getItem("scrollPos");

    if (pos !== null) {
        window.scrollTo(0, parseInt(pos));
        sessionStorage.removeItem("scrollPos");
    }
});
