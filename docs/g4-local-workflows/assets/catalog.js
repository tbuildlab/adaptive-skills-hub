"use strict";
// Shared consumers: index.html and workflows.html. No network or persistence.
const search = document.querySelector("#workflow-search");
const entries = [...document.querySelectorAll("[data-workflow]")];
const count = document.querySelector("#result-count");
const empty = document.querySelector("#no-results");
function filter() {
  const query = search.value.trim().toLocaleLowerCase();
  let visible = 0;
  for (const entry of entries) {
    const match = entry.textContent.toLocaleLowerCase().includes(query);
    entry.hidden = !match;
    visible += Number(match);
  }
  count.textContent = `${visible} of ${entries.length} workflows shown`;
  empty.hidden = visible !== 0;
}
search.addEventListener("input", filter);
document.querySelector("#clear-search").addEventListener("click", () => {
  search.value = ""; filter(); search.focus();
});
filter();
