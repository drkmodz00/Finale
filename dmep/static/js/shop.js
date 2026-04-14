function openProductModal(product) {

  console.log("MODAL PRODUCT:", product);

  // image
  document.getElementById('modalProductImage').src = product.img
    ? product.img
    : '/static/images/no-image.png';
    // name
    document.getElementById('modalProductName').textContent = product.name;

    // category & supplier
    document.getElementById('modalCategory').textContent = product.category?.name ?? '';
    document.getElementById('modalSupplier').textContent = product.supplier?.name ?? '';
    document.getElementById('metaSep').classList.toggle(
      'd-none', !product.category || !product.supplier

);

  // sku & barcode
//   const skuEl = document.getElementById('modalSku');
//   const barEl = document.getElementById('modalBarcode');
//   skuEl.textContent = product.sku ? `SKU: ${product.sku}` : '';
//   skuEl.classList.toggle('d-none', !product.sku);
//   barEl.textContent = product.barcode ? `BAR: ${product.barcode}` : '';
//   barEl.classList.toggle('d-none', !product.barcode);

  // prices
// ✅ SALE PRICE LOGIC
const priceWrapper = document.getElementById("modalPriceWrapper");

if (product.has_discount && product.final_price && product.selling_price) {
  priceWrapper.innerHTML = `
          <span style="color:#e60023;font-weight:bold;font-size:1.5rem;">
              ₱${product.final_price.toFixed(2)}
          </span>
          <span style="text-decoration:line-through;color:gray;margin-left:8px;">
              ₱${product.selling_price.toFixed(2)}
          </span>
          <span style="color:#e60023;margin-left:8px;">
              -${product.discount}%
          </span>
      `;
  } else if (product.selling_price) {
      priceWrapper.innerHTML = `
          <span style="font-size:1.5rem;">
              ₱${product.selling_price.toFixed(2)}
          </span>
      `;
  } else {
      priceWrapper.innerHTML = `—`;
  } 
 // stock
//   const unit = product.unit ?? '';
//   document.getElementById('modalStockQty').textContent =
//     product.stock_qty ?? '—';
//   document.getElementById('modalReorderLevel').textContent =
//     product.reorder_level ?? '—';
//   document.getElementById('modalUnit1').textContent = unit;
//   document.getElementById('modalUnit2').textContent = unit;
//   document.getElementById('modalUnitPill').textContent = unit;

  // status dot
  const dotColors = { active: '#4CAF50', inactive: '#9E9E9E', discontinued: '#F44336' };
  const dot = document.getElementById('modalStatusDot');
  dot.style.background = dotColors[product.status] ?? '#9E9E9E';
  document.getElementById('modalStatus').textContent =
    product.status ? product.status.charAt(0).toUpperCase() + product.status.slice(1) : '—';
 
  document.getElementById('modalAddToCart').href = product.url || "#";
  // badges (is_new, is_best)
//   document.getElementById('modalBadgeNew').classList.toggle('d-none', !product.is_new);
//   document.getElementById('modalBadgeBest').classList.toggle('d-none', !product.is_best);

  new bootstrap.Modal(document.getElementById('productModal')).show();
}

window.showProduct = function(el) {

const product = {
  
  name: el.dataset.name,
  img: el.dataset.img,
  url: el.dataset.url,
  category: el.dataset.category ? { name: el.dataset.category } : null,
  supplier: el.dataset.supplier ? { name: el.dataset.supplier } : null,

  selling_price: el.dataset.sellingPrice ? parseFloat(el.dataset.sellingPrice) : null,
  cost_price: el.dataset.costPrice ? parseFloat(el.dataset.costPrice) : null,

  // ✅ FIXED
  final_price: el.dataset.finalPrice ? parseFloat(el.dataset.finalPrice) : null,
  discount: el.dataset.discount ? parseFloat(el.dataset.discount) : null,
  has_discount: el.dataset.hasDiscount === "true",

  status: el.dataset.status,
};

  openProductModal(product);
};

// window.showProduct = function(el) {
//   alert("clicked");
// };

// prices (WITH SALE SUPPORT)
