
function showProduct(card) {
  const name         = card.dataset.name;
  const cartUrl      = card.dataset.url;
  const img          = card.dataset.img;
  const hasDiscount  = card.dataset.hasDiscount === "true";
  const finalPrice   = parseFloat(card.dataset.finalPrice) || 0;
  const sellingPrice = parseFloat(card.dataset.sellingPrice) || 0;
  const discount     = parseFloat(card.dataset.discount || 0);
  const status       = card.dataset.status;
  const category     = card.dataset.category;
  const supplier     = card.dataset.supplier;

  document.getElementById("modalProductName").textContent = name;

  const imgEl = document.getElementById("modalProductImage");
  imgEl.src = img;

  document.getElementById("modalCategory").textContent = category;
  document.getElementById("modalSupplier").textContent = supplier;

  const sep = document.getElementById("metaSep");
  sep.classList.toggle("d-none", !(category && supplier));

  const priceWrapper = document.getElementById("modalPriceWrapper");

  if (hasDiscount) {
    priceWrapper.innerHTML = `
      <span style="color:#e60023;font-weight:bold;font-size:1.5rem;">
        ₱${finalPrice.toFixed(2)}
      </span>
      <span style="text-decoration:line-through;color:gray;margin-left:8px;">
        ₱${sellingPrice.toFixed(2)}
      </span>
      <span style="color:#e60023;margin-left:6px;">-${discount}%</span>
    `;
  } else {
    priceWrapper.innerHTML = `
      <span style="font-size:1.5rem;font-weight:bold;">
        ₱${sellingPrice.toFixed(2)}
      </span>
    `;
  }

  document.getElementById("modalStatus").textContent = status;

  document.getElementById("modalAddToCart").href = cartUrl;

  const modal = new bootstrap.Modal(document.getElementById("productModal"));
  modal.show();
}