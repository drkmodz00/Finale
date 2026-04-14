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

