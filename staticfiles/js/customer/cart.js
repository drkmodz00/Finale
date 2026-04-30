function getCookie(name) {
    let cookieValue = null;
    if (document.cookie) {
        document.cookie.split(';').forEach(c => {
            c = c.trim();
            if (c.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(c.slice(name.length + 1));
            }
        });
    }
    return cookieValue;
}

function updateSelectedCart() {
    let selected = [];

    document.querySelectorAll(".cart-checkbox:checked").forEach(cb => {
        selected.push(cb.dataset.key);
    });

    fetch("/cart/selected/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ selected })
    })
    .then(res => res.json())
    .then(data => {

    const subtotalEl = document.querySelector(".val-subtotal");
    const discountEl = document.querySelector(".val-discount");
    const totalEl = document.querySelector(".val-total");

    if (subtotalEl) {
        subtotalEl.innerText = "₱" + Number(data.subtotal || 0).toFixed(2);
    }

    if (discountEl) {
        discountEl.innerText =
            data.discount_total > 0
                ? "-₱" + Number(data.discount_total).toFixed(2)
                : "--";
    }

    if (totalEl) {
        totalEl.innerText = "₱" + Number(data.total || 0).toFixed(2);
    }
    })
    .catch(err => console.error("Cart update failed:", err));
}
function changeQty(productId, action) {
    fetch(`/cart/update/${productId}/${action}/`)
        .then(() => location.reload());
}

function removeItem(productId) {
    fetch(`/cart/remove/${productId}/`)
        .then(() => location.reload());
}