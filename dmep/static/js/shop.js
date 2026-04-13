function openProductModal(product) {
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
  document.getElementById('modalSellingPrice').textContent =
    product.selling_price != null ? `₱${product.selling_price.toFixed(2)}` : '—';
  document.getElementById('modalCostPrice').textContent =
    product.cost_price != null ? `₱${product.cost_price.toFixed(2)}` : '—';

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

  // badges (is_new, is_best)
//   document.getElementById('modalBadgeNew').classList.toggle('d-none', !product.is_new);
//   document.getElementById('modalBadgeBest').classList.toggle('d-none', !product.is_best);

  new bootstrap.Modal(document.getElementById('productModal')).show();
}

window.showProduct = function(el) {

  const product = {
    name: el.dataset.name,
    img: el.dataset.img,
    category: el.dataset.category ? { name: el.dataset.category } : null,
    supplier: el.dataset.supplier ? { name: el.dataset.supplier } : null,
    sku: el.dataset.sku,
    barcode: el.dataset.barcode,
    selling_price: el.dataset.sellingPrice ? parseFloat(el.dataset.sellingPrice) : null,
    cost_price: el.dataset.costPrice ? parseFloat(el.dataset.costPrice) : null,
    stock_qty: el.dataset.stockQty ? parseInt(el.dataset.stockQty) : null,
    reorder_level: el.dataset.reorderLevel ? parseInt(el.dataset.reorderLevel) : null,
    unit: el.dataset.unit,
    status: el.dataset.status,
    // is_new: el.dataset.isNew === "true",
    // is_best: el.dataset.isBest === "true"
  };

  openProductModal(product);
};

// window.showProduct = function(el) {
//   alert("clicked");
// };