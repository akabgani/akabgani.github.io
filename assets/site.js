<script>
document.addEventListener("DOMContentLoaded", () => {
  const search = document.getElementById("pub-search");
  const year = document.getElementById("pub-year");
  if (!search || !year) return;
  const cards = Array.from(document.querySelectorAll(".pub-card[data-year]"));
  [...new Set(cards.map(c => c.dataset.year))].sort((a,b) => b.localeCompare(a)).forEach(y => {
    const opt = document.createElement("option");
    opt.value = y;
    opt.textContent = y;
    year.appendChild(opt);
  });
  function filter() {
    const q = search.value.trim().toLowerCase();
    const y = year.value;
    let visible = 0;
    cards.forEach(card => {
      const show = (!q || card.dataset.search.includes(q)) && (y === "all" || card.dataset.year === y);
      card.hidden = !show;
      if (show) visible++;
    });
    ["published-section","preprints-section"].forEach(id => {
      const section = document.getElementById(id);
      if (section) section.hidden = !Array.from(section.querySelectorAll(".pub-card")).some(c => !c.hidden);
    });
    const empty = document.getElementById("pub-empty");
    if (empty) empty.hidden = visible !== 0;
  }
  search.addEventListener("input", filter);
  year.addEventListener("change", filter);
});
</script>
