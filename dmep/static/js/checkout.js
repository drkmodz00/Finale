document.addEventListener('DOMContentLoaded', function() {
    const paymentCards = document.querySelectorAll('.payment-card');

    paymentCards.forEach(card => {
        card.addEventListener('click', function() {
            // 1. Remove active class from all
            paymentCards.forEach(c => c.classList.remove('active'));
            
            // 2. Add to clicked
            this.classList.add('active');
            
            // 3. Check the internal radio button
            const radio = this.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
        });
    });
});

document.getElementById("checkout-form").addEventListener("submit", function(e) {
    e.preventDefault(); // stop immediate submit

    // show modal
    document.getElementById("successModal").style.display = "flex";

    // OPTIONAL: auto-submit after 2 seconds
    setTimeout(() => {
        e.target.submit();
    }, 2000);
});

function closeModal() {
    document.getElementById("successModal").style.display = "none";
}