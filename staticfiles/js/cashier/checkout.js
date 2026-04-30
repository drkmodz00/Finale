const cashInput = document.getElementById("cashInput");
const changeAmount = document.getElementById("changeAmount");
const total = parseFloat("{{ total|default:0 }}");

cashInput.addEventListener("input", function () {
    const cash = parseFloat(this.value);

        if (isNaN(cash)) {
            changeAmount.innerText = "₱0.00";
            return;
        }

        const change = cash - total;

        if (change < 0) {
            changeAmount.innerText = "Insufficient";
            changeAmount.classList.remove("text-emerald-600");
            changeAmount.classList.add("text-red-500");
        } else {
            changeAmount.innerText = "₱" + change.toFixed(2);
            changeAmount.classList.remove("text-red-500");
            changeAmount.classList.add("text-emerald-600");
        }
    });
