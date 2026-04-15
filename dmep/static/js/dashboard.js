document.addEventListener("DOMContentLoaded", function () {
    const activeParent = "{{ active_parent_id }}";

    if (activeParent) {
        const el = document.getElementById("cat-" + activeParent);
        if (el) {
            el.classList.remove("hidden");
        }
    }
});

function toggleCat(id) {
    const el = document.getElementById("cat-" + id);
    if (el) {
        el.classList.toggle("hidden");
    }
}