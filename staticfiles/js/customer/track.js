function getCSRFToken() {
  return document.cookie
    .split(';')
    .find(row => row.trim().startsWith('csrftoken='))
    ?.split('=')[1];
}

const cancelBtn = document.getElementById("cancelBtn");

if (cancelBtn) {
  cancelBtn.addEventListener("click", async function () {

    const orderCode = this.dataset.order;

    if (!confirm("Are you sure you want to cancel this order?")) return;

    try {
      const res = await fetch(`/cancel-order/${orderCode}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCSRFToken(),
          "Content-Type": "application/json"
        }
      });

      const data = await res.json();

      if (data.success) {
        alert("Order cancelled successfully");
        location.reload();
      } else {
        alert(data.error || "Failed to cancel order");
      }

    } catch (err) {
      alert("Something went wrong. Please try again.");
    }
  });
}
