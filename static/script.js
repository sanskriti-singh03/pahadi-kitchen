/* Pahadi Kitchen — Frontend JS */

// ── qty controls on menu cards ──────────────────────────
document.addEventListener("DOMContentLoaded", () => {

  // ++ / -- buttons on menu cards
  document.querySelectorAll(".qty-wrap").forEach(wrap => {
    const input = wrap.querySelector(".qty-input");
    wrap.querySelector(".qty-dec")?.addEventListener("click", () => {
      const v = parseInt(input.value, 10);
      if (v > 1) input.value = v - 1;
    });
    wrap.querySelector(".qty-inc")?.addEventListener("click", () => {
      const v = parseInt(input.value, 10);
      if (v < 99) input.value = v + 1;
    });
  });

  // ── auto-dismiss flash messages after 3.5 s ──────────
  document.querySelectorAll(".flash").forEach(el => {
    setTimeout(() => {
      el.style.transition = "opacity .4s ease, transform .4s ease";
      el.style.opacity = "0";
      el.style.transform = "translateX(20px)";
      setTimeout(() => el.remove(), 400);
    }, 3500);
  });

  // ── admin tab navigation ──────────────────────────────
  const tabBtns   = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  function activateTab(id) {
    tabBtns.forEach(b   => b.classList.toggle("active",   b.dataset.tab === id));
    tabPanels.forEach(p => p.classList.toggle("active",   p.id === id));
    history.replaceState(null, "", "#" + id);
  }

  tabBtns.forEach(btn => btn.addEventListener("click", () => activateTab(btn.dataset.tab)));

  // restore tab from URL hash on load
  const hash = location.hash.replace("#", "");
  if (hash && document.getElementById(hash)) {
    activateTab(hash);
  } else if (tabBtns.length > 0) {
    activateTab(tabBtns[0].dataset.tab);
  }

  // ── cart quantity inline update ───────────────────────
  document.querySelectorAll(".cart-inc").forEach(btn => {
    btn.addEventListener("click", () => {
      const inp = btn.closest(".qty-form").querySelector("input");
      inp.value = parseInt(inp.value, 10) + 1;
      inp.closest("form").submit();
    });
  });
  document.querySelectorAll(".cart-dec").forEach(btn => {
    btn.addEventListener("click", () => {
      const inp = btn.closest(".qty-form").querySelector("input");
      const v   = parseInt(inp.value, 10);
      inp.value = Math.max(0, v - 1);
      inp.closest("form").submit();
    });
  });
});
