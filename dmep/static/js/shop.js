// ─── CATEGORY TOGGLE ─────────────────────────────────────────────────────────

function toggleCat(id) {
  const el = document.getElementById("cat-" + id);
  if (!el) return;

  const isHidden = el.classList.contains("hidden");

  // Close all other open subcategory panels
  document.querySelectorAll(".subcat").forEach(x => {
    if (x.id !== "cat-" + id) x.classList.add("hidden");
  });

  el.classList.toggle("hidden", !isHidden);
  localStorage.setItem("cat-" + id, isHidden ? "open" : "closed");
}

// ─── ON PAGE LOAD ─────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {

  // Restore previously open category panels
  document.querySelectorAll('[id^="cat-"]').forEach(el => {
    const state = localStorage.getItem(el.id);
    el.classList.toggle("hidden", state !== "open");
  });

  // Keep parent open when a subcategory link is clicked
  document.querySelectorAll(".subcat-link").forEach(link => {
    link.addEventListener("click", function () {
      const parentId = this.dataset.parent;
      if (parentId) localStorage.setItem("cat-" + parentId, "open");
    });
  });

});

// ─── PRODUCT MODAL ────────────────────────────────────────────────────────────

function showProduct(card) {
  const name         = card.dataset.name;
  const cartUrl      = card.dataset.url;
  const img          = card.dataset.img;
  const hasDiscount  = card.dataset.hasDiscount === "true";
  const finalPrice   = parseFloat(card.dataset.finalPrice) || 0;
  const sellingPrice = parseFloat(card.dataset.sellingPrice) || 0;
  const discount = parseFloat(card.dataset.discount || 0);
  const unit         = card.dataset.unit;
  const status       = card.dataset.status;
  const category     = card.dataset.category;
  const supplier     = card.dataset.supplier;

  // Name
  document.getElementById("modalProductName").textContent = name;

  // Image
  const imgEl = document.getElementById("modalProductImage");
  imgEl.src = img || "";
  imgEl.style.display = img ? "block" : "none";

  // Category / Supplier
  document.getElementById("modalCategory").textContent = category;
  document.getElementById("modalSupplier").textContent = supplier;
  const sep = document.getElementById("metaSep");
  sep.classList.toggle("d-none", !(category && supplier));

  // Price
  const priceWrapper = document.getElementById("modalPriceWrapper");
  if (hasDiscount) {
    priceWrapper.innerHTML = `
      <span style="color:#e60023;font-weight:bold;font-size:1.3rem;">
        ₱${finalPrice.toFixed(2)}
      </span>
      <span style="text-decoration:line-through;color:gray;margin-left:6px;">
        ₱${sellingPrice.toFixed(2)}
      </span>
      <span style="color:#e60023;font-size:0.85rem;margin-left:6px;">-${discount}%</span>
    `;
  } else {
    priceWrapper.innerHTML = `
      <span style="font-weight:bold;font-size:1.3rem;">₱${sellingPrice.toFixed(2)}</span>
    `;
  }

  // Unit / Status
  document.getElementById("modalUnit1").textContent    = unit;
  document.getElementById("modalUnitPill").textContent = unit;
  document.getElementById("modalStatus").textContent   = status;

  const dot = document.getElementById("modalStatusDot");
  const s = (status || "").toLowerCase();
  dot.style.backgroundColor =
    s === "available" || s === "active" ? "#22c55e" :
    s === "out of stock"                ? "#ef4444" : "#94a3b8";

  // FIX: set the modal "Add to Cart" link href to the correct cart_add URL
  document.getElementById("modalAddToCart").href = cartUrl;

  // Open Bootstrap modal
  const modal = new bootstrap.Modal(document.getElementById("productModal"));
  modal.show();
}