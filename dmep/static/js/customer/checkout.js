document.getElementById("phone").addEventListener("blur", function () {

    const phone = this.value;
    if (!phone) return;

    fetch(`/ajax/customer-by-phone/?phone=${phone}`)
        .then(res => res.json())
        .then(data => {

            if (data.exists) {
                document.getElementById("customer_id").value = data.id;
                document.getElementById("full_name").value = data.full_name;
                document.getElementById("email").value = data.email;
                document.getElementById("address").value = data.address;
            } else {
                document.getElementById("customer_id").value = "";
            }

        });

});

