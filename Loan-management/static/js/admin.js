document.addEventListener("DOMContentLoaded", () => {
  const toggleNavbar = (toggleId, navId, bodyId, headerId) => {
    const toggleEl  = document.getElementById(toggleId),
          navEl     = document.getElementById(navId),
          bodyEl    = document.getElementById(bodyId),
          headerEl  = document.getElementById(headerId);

    if (toggleEl && navEl && bodyEl && headerEl) {
      toggleEl.addEventListener("click", () => {
        navEl.classList.toggle("show");
        toggleEl.classList.toggle("bx-x");
        bodyEl.classList.toggle("body-pd");
        headerEl.classList.toggle("body-pd");
      });
    }
  };

  toggleNavbar("header-toggle", "nav-bar", "body-pd", "header");

  const navLinks = document.querySelectorAll(".nav_link");
  navLinks.forEach(link => {
    link.addEventListener("click", function() {
      navLinks.forEach(l => l.classList.remove("active"));
      this.classList.add("active");
    });
  });
});
