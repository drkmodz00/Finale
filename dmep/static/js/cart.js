function changeQty(productId, action) {
    fetch(`/cart/update/${productId}/${action}/`)
        .then(() => location.reload());
}

function removeItem(productId) {
    fetch(`/cart/remove/${productId}/`)
        .then(() => location.reload());
}

function getSelectedItems() {
    const selected = [];
    document.querySelectorAll('.cart-checkbox:checked').forEach(cb => {
        selected.push(cb.dataset.key);
    });
    return selected;
}

function updateSelectedCart() {
    const selected = getSelectedItems();
    console.log("Selected items:", selected);

    // optional: store in localStorage
    localStorage.setItem("selectedCartItems", JSON.stringify(selected));

    updateSummary(selected);
}

function updateSummary(selectedKeys) {
    let total = 0;

    selectedKeys.forEach(key => {
        const row = document.querySelector(`[data-key="${key}"]`).closest('.cart-item');
        const price = parseFloat(row.querySelector('.price-cell').innerText.replace('₱',''));
        const qty = parseInt(row.querySelector('.qty-val').innerText);

        total += price * qty;
    });

    document.querySelector('.grand-row__value').innerText =
        "₱" + total.toFixed(2);
}