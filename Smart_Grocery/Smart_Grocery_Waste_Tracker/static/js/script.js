function validateLogin() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    const usernamePattern = /^[A-Za-z]+$/;
    const passwordPattern = /^(?=.*[@$!%*#?&])[A-Za-z0-9@$!%*#?&]+$/;

    if (!usernamePattern.test(username)) {
        alert("Invalid username");
        return;
        
    }

    if (!passwordPattern.test(password)) {
        alert("Invalid password");
        return;
    }

    window.location.href = "profile.html";

    /*alert("Success");*/

    // ✅ Clear fields after success
    document.getElementById("username").value = "";
    document.getElementById("password").value = "";
}

/*add item*/
document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");

  form.addEventListener("submit", function (e) {
    const name = form.name.value.trim();
    const category = form.category.value.trim();
    const supplier = form.supplier.value.trim();
    const quantity = parseInt(form.quantity.value);
    const purchase = new Date(form.purchase.value);
    const expiry = new Date(form.expiry.value);

    const charOnly = /^[A-Za-z\s]+$/;

    if (!charOnly.test(name)) {
      alert("❌ Product Name must contain only letters.");
      e.preventDefault();
      return;
    }

    if (!charOnly.test(category)) {
      alert("❌ Category must contain only letters.");
      e.preventDefault();
      return;
    }

    if (supplier && !charOnly.test(supplier)) {
      alert("❌ Supplier must contain only letters.");
      e.preventDefault();
      return;
    }

    if (expiry < purchase) {
      alert("⚠️ Expiry date cannot be before purchase date.");
      e.preventDefault();
      return;
    }

    if (quantity <= 0) {
      alert("⚠️ Quantity must be greater than 0.");
      e.preventDefault();
      return;
    }

    // Confirm submission
    const confirmAdd = confirm("Are you sure you want to add this item?");
    if (!confirmAdd) {
      e.preventDefault();
    } else {
      alert("✅ Item successfully added!");
    }
  });
});

//notify badge
document.addEventListener("DOMContentLoaded", function () {
    const badge = document.getElementById("badge");

    // ✅ Calculate total expiring items
    const totalExpiring = (expiringToday || 0) + (expiringTomorrow || 0) + (expiringLater || 0);

    if (totalExpiring > 0) {
        badge.textContent = totalExpiring;
        badge.classList.remove("d-none");
        badge.classList.add("blink"); // optional effect
    } else {
        badge.classList.add("d-none");
    }
});

//How it works

// How it works

//notify badge
document.addEventListener("DOMContentLoaded", function () {
    const badge = document.getElementById("badge");

    // ✅ Calculate total expiring items
    const totalExpiring = (expiringToday || 0) + (expiringTomorrow || 0) + (expiringLater || 0);

    if (totalExpiring > 0) {
        badge.textContent = totalExpiring;
        badge.classList.remove("d-none");
        badge.classList.add("blink"); // optional effect
    } else {
        badge.classList.add("d-none");
    }
});

// Reveal step cards with animation on scroll
document.addEventListener("scroll", () => {
  const cards = document.querySelectorAll(".step-card");
  cards.forEach(card => {
    const rect = card.getBoundingClientRect();
    if (rect.top < window.innerHeight - 50) {
      card.classList.add("show");
    }
  });
});


