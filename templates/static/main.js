let cartTotal = 0;
let currentTheme = "light";
let scanner = null;

const SECRET_KEY = "greencoin-demo-key";

/* =========================
   AUTH
========================= */

async function Login() {
    try {
        const u = document.getElementById("loginEmail")?.value;
        const p = document.getElementById("loginPass")?.value;

        const r = await fetch("/Login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: u, password: p })
        });

        const d = await r.json();

        if (r.ok) window.location.href = d.location;
        else alert(d.message);

    } catch (err) {
        alert("Login error");
    }
}

async function SignUp() {
    try {
        const n = document.getElementById("regName")?.value;
        const e = document.getElementById("regEmail")?.value;
        const p = document.getElementById("regPass")?.value;
        const t = document.getElementById("terms")?.checked;

        if (!n || !e || !p || !t) return alert("Check fields and terms");

        const r = await fetch("/Signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username: e,
                password: p,
                full_name: n
            })
        });

        const d = await r.json();

        if (r.ok) window.location.href = d.location;
        else alert(d.message);

    } catch {
        alert("Signup error");
    }
}

/* =========================
   MARKETPLACE
========================= */

async function loadMarketplace() {
    const g = document.getElementById("product-grid");
    if (!g) return;

    try {
        const r = await fetch("/Buy");
        const d = await r.json();

        g.innerHTML = "";

        d.items.forEach(i => {
            const soldOut = i.available <= 0;
            const escapedName = i.name.replace(/'/g, "\\'");

            g.insertAdjacentHTML("beforeend", `
                <div class="product-card">
                    <div class="img-placeholder">
                        <img src="${i.link_image}" class="product-img" loading="lazy">
                    </div>
                    
                    <div class="product-title">${i.name}</div>
                    
                    <div class="stock-info">
                        ${i.available} in stock
                    </div>
                    
                    <div class="price-tag">${i.price} GC</div>
                    
                    <div style="
                        display: flex;
                        flex-direction: row;
                        gap: 10px;
                        margin-top: auto;
                        width: 100%;
                        justify-content: space-evenly;
                    ">
                        <!-- Quantity controls -->
                        <div class="qty-control-skeleton">
                            <button type="button" 
                                class="qty-btn"
                                onclick="updateCounter(this,-1)">−</button>
                            
                            <label class="cartCounterLabel">1</label>
                            
                            <button type="button" 
                                class="qty-btn"
                                onclick="updateCounter(this,1)">+</button>
                        </div>
                        
                        <!-- Add to Cart button -->
                        <button class="buy-btn"
                            ${soldOut ? "disabled" : ""}
                            onclick="addToCart(
                                '${i.id}',
                                '${escapedName}',
                                ${i.price},
                                '${i.link_image}',
                                '${i.seller}',
                                this
                            )">
                            ${soldOut ? "Sold Out" : "Add to Cart"}
                        </button>
                    </div>
                </div>
            `);
        });

        // Add loading animation removal for images
        document.querySelectorAll('.img-placeholder img').forEach(img => {
            img.addEventListener('load', function() {
                this.closest('.img-placeholder').style.background = 'none';
                this.closest('.img-placeholder').style.animation = 'none';
            });
        });

    } catch (err) {
        console.error("Marketplace load failed", err);
        g.innerHTML = `<p style="color: var(--p); text-align: center; padding: 40px;">⚠️ Failed to load products</p>`;
    }
}

function updateCounter(btn, delta) {
    const parent = btn.closest('.qty-control-skeleton');
    const label = parent.querySelector('.cartCounterLabel');
    if (label) {
        let val = parseInt(label.innerText, 10);
        val = Math.max(1, val + delta);
        label.innerText = val;
        
        // Animation effect
        label.style.transform = 'scale(1.1)';
        setTimeout(() => { label.style.transform = 'scale(1)'; }, 100);
    }
}

/* =========================
   ADD TO CART
========================= */

async function addToCart(id, name, price, image, seller, btn) {
    try {
        const qty = parseInt(
            btn.parentElement.querySelector(".cartCounterLabel")?.innerText || "1"
        );

        const r = await fetch("/Add-To-Cart", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                itemId: id,
                name,
                price,
                link_image: image,
                seller,
                quantity: qty
            })
        });

        const d = await r.json().catch(() => ({}));

        if (r.ok) {
            alert("Added to cart");
            loadCart();
        } else {
            alert(d.message || "Failed to add");
        }

    } catch {
        alert("Add to cart error");
    }
}

/* =========================
   CART
========================= */

function reload() {
    const url = new URL(window.location.href);
    url.searchParams.set('t', Date.now()); 
    window.location.href = url.toString();
}

async function loadCart() {
    const list = document.getElementById("cart-list");
    const section = document.getElementById("checkout-section");
    const totalLabel = document.getElementById("cart-total");

    if (!list) return;

    try {
        const r = await fetch("/Get-Cart");
        const d = await r.json();

        if (!d.cart.length) {
            cartTotal = 0;
            list.innerHTML = `<p style="text-align:center;color:#95a5a6">Empty basket</p>`;
            if (totalLabel) totalLabel.innerText = "0.00 GC";
            if (section) section.style.display = "none";
            return;
        }

        list.innerHTML = "";

        cartTotal = d.cart.reduce((sum, i) => sum + (i.price * i.quantity), 0);

        d.cart.forEach(i => {
            list.insertAdjacentHTML("beforeend", `
                <div class="cart-item">

                    <div class="cart-img"
                         style="background-image:url('${i.link_image}')"></div>

                    <div class="cart-details">
                        <div class="cart-title">${i.name}</div>
                        <div class="cart-meta">${i.quantity} units • ${i.price} GC</div>
                    </div>

                    <div class="cart-actions">
                        <button class="btn-small btn-buy"
                            onclick="alert('Buy now logic')">
                            Buy Now
                        </button>

                        <button class="btn-small btn-remove"
                            onclick="removeItem('${i.item_id}')">
                            Remove
                        </button>
                    </div>

                </div>
            `);
        });

        if (totalLabel) totalLabel.innerText = cartTotal.toFixed(2) + " GC";
        if (section) section.style.display = "flex";

    } catch (err) {
        console.error("Cart load error", err);
    }
}

/* =========================
   REMOVE ITEM
========================= */

async function removeItem(id) {
    try {
        const r = await fetch("/Remove-From-Cart", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ itemId: id })
        });

        if (r.ok) loadCart();

    } catch {
        alert("Remove failed");
    }
}

/* =========================
   CHECKOUT
========================= */

async function checkoutAll() {
    try {
        const r = await fetch("/Get_Ballance"); // FIXED endpoint
        const data = await r.json();

        const userBalance = parseFloat(data.bal);

        if (cartTotal <= 0) return alert("Your cart is empty.");

        if (cartTotal > userBalance) {
            return alert(
                `Not enough balance. Need ${cartTotal.toFixed(2)} GC but have ${userBalance.toFixed(2)} GC`
            );
        }

        alert("Checkout not implemented yet.");

    } catch (err) {
        alert(err.message);
    }
}

/* =========================
   THEME
========================= */

async function Toggle() {
    try {
        const r = await fetch("/togglePreference", {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });

        const d = await r.json();

        if (d.preference) {
            currentTheme = d.preference;
            applyTheme(currentTheme);
            updateThemeIcons(currentTheme);
        }

    } catch {
        currentTheme = currentTheme === "light" ? "dark" : "light";
        applyTheme(currentTheme);
        updateThemeIcons(currentTheme);
    }
}

function updateThemeIcons(theme) {
    const sun = document.getElementById("sun-icon");
    const moon = document.getElementById("moon-icon");

    if (!sun || !moon) return;

    if (theme === "dark") {
        sun.style.display = "block";
        moon.style.display = "none";
    } else {
        sun.style.display = "none";
        moon.style.display = "block";
    }
}
function applyTheme(theme) {
    document.body.className = theme;
    localStorage.setItem("theme", theme);
}

/* =========================
   INIT
========================= */

let visible = false;

function visibilityToggle() {
  const cont = document.getElementById("balance");
  const wallID = document.getElementById("walletID");

  if (visible) {
    cont.classList.remove("amt");
    cont.classList.add("amtBlurry");
    wallID.classList.remove("walletID");
    wallID.classList.add("amtBlurry");
  } else {
    cont.classList.remove("amtBlurry");
    cont.classList.add("amt");
    wallID.classList.remove("amtBlurry");
    wallID.classList.add("walletID");
  }

  visible = !visible;
}
document.addEventListener("DOMContentLoaded", () => {
    currentTheme = localStorage.getItem("theme") || "light";
    applyTheme(currentTheme);

    loadMarketplace();
    loadCart();
});

const imagekit = new ImageKit({
  publicKey: "public_EqxvibXcdPomqMQkfO3NaE2Gwuc=",
  urlEndpoint: "https://ik.imagekit.io/75wdreowf"
});

async function updateAvatar(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
        alert("Please select an image");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch("/updateProfilePic", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (res.ok) {
            const imgElement = document.getElementById("picha");
            if (imgElement) {
                imgElement.src = data.url + "?t=" + Date.now();
            }
        } else {
            alert(data.message || "Upload failed");
        }
    } catch (err) {
        console.error(err);
        alert("Connection error");
    }
}


function init(){
    currentTheme = localStorage.getItem("theme") || "light";
    applyTheme(currentTheme);
    updateThemeIcons(currentTheme);
    loadMarketplace();
    loadCart();
}

function processPayment(){
    alert("Payment processing not implemented yet.");
}