let cartIcon;

// ─────────────────────────────────────────────
// INIT (SAFE DOM READY)
// ─────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {

    cartIcon = document.getElementById("cartIcon");

    // MODAL OUTSIDE CLICK CLOSE
    const modal = document.getElementById("productModal");

    if (modal) {
        modal.addEventListener("click", (e) => {
            if (e.target.id === "productModal") {
                closeModal();
            }
        });
    }

    // MODAL BUTTON BIND (SAFE)
    const modalBtn = document.getElementById("modalAddToCart");

    if (modalBtn) {
        modalBtn.addEventListener("click", function (e) {
            e.preventDefault();

            const url = this.dataset.url;
            if (!url) return;

            const img = document.getElementById("modalProductImage");
            const rect = img.getBoundingClientRect();

            addToCart(url, img.src, rect.left, rect.top);
        });
    }

});


// ─────────────────────────────────────────────
// CATEGORY TOGGLE
// ─────────────────────────────────────────────
function toggleCat(id) {
    const el = document.getElementById(`cat-${id}`);
    if (!el) return;

    document.querySelectorAll('[id^="cat-"]').forEach(item => {
        if (item.id !== `cat-${id}`) {
            item.classList.add('hidden');
        }
    });

    el.classList.toggle('hidden');
}


// ─────────────────────────────────────────────
// ADD TO CART (UNIFIED SYSTEM)
// ─────────────────────────────────────────────
async function addToCart(url, imgSrc, x, y) {

    if (!url) return;

    flyToCart(imgSrc, x, y);

    try {
        const res = await fetch(url, {
            method: "GET",
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        });

        const data = await res.json();

        if (!cartIcon) return;

        let badge = cartIcon.querySelector("span");

        if (!badge) {
            badge = document.createElement("span");
            badge.className =
                "absolute -top-2 -right-2 bg-red-500 text-white text-[10px] w-4 h-4 flex items-center justify-center rounded-full";
            cartIcon.appendChild(badge);
        }

        badge.innerText = data.cart_count;

    } catch (err) {
        console.error("Cart error:", err);
    }
}


// ─────────────────────────────────────────────
// FLY TO CART ANIMATION
// ─────────────────────────────────────────────
function flyToCart(imgSrc, x, y) {

    if (!imgSrc) return;

    const img = document.createElement("img");
    img.src = imgSrc;
    document.body.appendChild(img);

    const cart = cartIcon?.getBoundingClientRect();
    if (!cart) return;

    img.style.position = "fixed";
    img.style.left = x + "px";
    img.style.top = y + "px";
    img.style.width = "60px";
    img.style.height = "60px";
    img.style.transition = "all 0.8s ease-in-out";
    img.style.zIndex = "9999";

    setTimeout(() => {
        img.style.left = cart.left + "px";
        img.style.top = cart.top + "px";
        img.style.width = "20px";
        img.style.height = "20px";
        img.style.opacity = "0.3";
    }, 10);

    setTimeout(() => img.remove(), 850);
}


// ─────────────────────────────────────────────
// PRODUCT CARD ADD TO CART
// ─────────────────────────────────────────────
document.querySelectorAll(".add-to-cart-btn").forEach(btn => {

    btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();

        const url = this.dataset.url;
        const card = this.closest("[data-img]");
        const imgSrc = card?.dataset.img;

        const rect = this.getBoundingClientRect();

        addToCart(url, imgSrc, rect.left, rect.top);
    });

});


// ─────────────────────────────────────────────
// SHOW PRODUCT MODAL
// ─────────────────────────────────────────────
function showProduct(card) {

    const modal = document.getElementById("productModal");

    modal.classList.remove("hidden");
    modal.classList.add("flex");

    document.getElementById("modalProductName").textContent = card.dataset.name || "";
    document.getElementById("modalProductImage").src = card.dataset.img || "";

    document.getElementById("modalCategory").textContent = card.dataset.category || "";
    document.getElementById("modalSupplier").textContent = card.dataset.supplier || "";
    document.getElementById("modalStockQty").textContent = card.dataset.stock || 0;
    document.getElementById("modalUnit1").textContent = card.dataset.unit || "";
    document.getElementById("modalStatus").textContent = card.dataset.status || "";

    const priceWrapper = document.getElementById("modalPriceWrapper");

    const finalPrice = parseFloat(card.dataset.finalPrice || 0);
    const sellingPrice = parseFloat(card.dataset.sellingPrice || 0);
    const discount = parseFloat(card.dataset.discount || 0);

    if (discount > 0) {
        priceWrapper.innerHTML = `
            <span class="text-red-600 font-bold">₱${finalPrice.toFixed(2)}</span>
            <span class="line-through text-gray-400 ml-2">₱${sellingPrice.toFixed(2)}</span>
            <span class="text-red-500 text-xs ml-2">-${discount}%</span>
        `;
    } else {
        priceWrapper.innerHTML = `
            <span class="font-bold">₱${sellingPrice.toFixed(2)}</span>
        `;
    }

    document.getElementById("modalAddToCart").dataset.url = card.dataset.url;
}


// ─────────────────────────────────────────────
// CLOSE MODAL
// ─────────────────────────────────────────────
function closeModal() {
    const modal = document.getElementById("productModal");
    modal.classList.add("hidden");
    modal.classList.remove("flex");
}