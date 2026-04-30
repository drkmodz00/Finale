function getCSRFToken() {
    let cookieValue = null;
    const cookies = document.cookie.split(';');

    cookies.forEach(cookie => {
        const trimmed = cookie.trim();
        if (trimmed.startsWith('csrftoken=')) {
            cookieValue = trimmed.substring('csrftoken='.length);
        }
    });

    return cookieValue;
}
const cancelBtn = document.getElementById("cancelBtn");

if (cancelBtn) {
    cancelBtn.addEventListener("click", function () {

        const orderCode = this.dataset.order;

        if (!confirm("Are you sure you want to cancel this order?")) return;

        fetch(`/cancel-order/${orderCode}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/json"
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert("Order cancelled successfully");
                location.reload();
            } else {
                alert(data.error || "Failed to cancel");
            }
        })
        .catch(err => {
            console.error(err);
            alert("Something went wrong");
        });
    });
}