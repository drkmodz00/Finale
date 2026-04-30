document.getElementById("menuBtn").onclick = () =>
  document.getElementById("mobileMenu").classList.toggle("hidden");

document.getElementById("userBtn").onclick = () =>
  document.getElementById("userMenu").classList.toggle("hidden");

// shadow on scroll
window.addEventListener("scroll", () => {
  document.getElementById("navbar").classList.toggle("shadow",
    window.scrollY > 10);
});

document.getElementById("menuBtn").onclick = () =>
  document.getElementById("mobileMenu").classList.toggle("hidden");

document.getElementById("userBtn").onclick = () =>
  document.getElementById("userMenu").classList.toggle("hidden");

// shadow on scroll
window.addEventListener("scroll", () => {
  document.getElementById("navbar").classList.toggle("shadow",
    window.scrollY > 10);
});
