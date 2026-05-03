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

/* 🔥 ENABLE/DISABLE CHECKOUT BUTTON */
function updateCheckoutState() {
    const selectedCount = document.querySelectorAll(".cart-checkbox:checked").length;
    const btn = document.getElementById("checkoutBtn");

    if (!btn) return;

    if (selectedCount > 0) {
        btn.classList.remove("opacity-50", "pointer-events-none");
    } else {
        btn.classList.add("opacity-50", "pointer-events-none");
    }
}

/* CART SELECTION UPDATE */
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

        document.querySelector(".val-subtotal").innerText =
            "₱" + Number(data.subtotal || 0).toFixed(2);

        document.querySelector(".val-discount").innerText =
            data.discount_total > 0
                ? "-₱" + Number(data.discount_total).toFixed(2)
                : "--";

        document.querySelector(".val-total").innerText =
            "₱" + Number(data.total || 0).toFixed(2);

        updateCheckoutState();

    });
}

/* INIT */
document.addEventListener("DOMContentLoaded", updateCheckoutState);

function changeQty(productId, action) {
    fetch(`/cart/update/${productId}/${action}/`)
        .then(() => location.reload());
}

function removeItem(productId) {
    fetch(`/cart/remove/${productId}/`)
        .then(() => location.reload());
}
