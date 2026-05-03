const cartIcon = document.querySelector('[href="{% url "cart" %}"]');

function flyToCart(imgSrc, startX, startY, url) {

    const img = document.createElement("img");
    img.src = imgSrc;
    img.className = "fixed w-14 h-14 object-cover rounded-xl z-[9999] transition-all duration-700";

    document.body.appendChild(img);

    const cart = cartIcon.getBoundingClientRect();

    img.style.left = startX + "px";
    img.style.top = startY + "px";

    setTimeout(() => {
        img.style.left = cart.left + "px";
        img.style.top = cart.top + "px";
        img.style.width = "18px";
        img.style.height = "18px";
        img.style.opacity = "0.4";
    }, 30);

    setTimeout(() => {
        img.remove();
        fetch(url).then(() => location.reload());
    }, 700);
}

document.querySelectorAll(".add-to-cart-btn").forEach(btn => {
    btn.addEventListener("click", function(e){
        e.preventDefault();

        const img = this.dataset.img;
        const url = this.dataset.url;
        const rect = this.getBoundingClientRect();

        flyToCart(img, rect.left, rect.top, url);
    });
});

function closeModal(){
    document.getElementById("successModal").style.display = "none";
}
