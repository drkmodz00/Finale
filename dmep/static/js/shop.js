function toggleCat(id) {
  const el = document.getElementById("cat-" + id);
  if (!el) return;

  const isHidden = el.classList.contains("hidden");

  el.classList.toggle("hidden", !isHidden);

  // save state
  localStorage.setItem("cat-" + id, isHidden ? "open" : "closed");
}

// restore open categories on page load
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('[id^="cat-"]').forEach(el => {
    const state = localStorage.getItem(el.id);
    if (state === "open") {
      el.classList.remove("hidden");
    }
  });
});

// keep parent open when clicking subcategory
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".subcat-link").forEach(link => {
    link.addEventListener("click", function () {
      const parentId = this.dataset.parent;
      if (parentId) {
        localStorage.setItem("cat-" + parentId, "open");
      }
    });
  });
});