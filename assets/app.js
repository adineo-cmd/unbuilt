(function () {
  "use strict";

  /* "Pull a random gap" links navigate to a random not-built idea */
  document.querySelectorAll("[data-random-gap]").forEach(function (el) {
    el.addEventListener("click", function (e) {
      var C = window.CENSUS;
      if (!C) return;
      var pool = [];
      C.fields.forEach(function (f) {
        for (var i = 0; i < f.unbuilt.length; i++) pool.push(f.id + "|" + i);
      });
      if (!pool.length) return;
      e.preventDefault();
      var pick = pool[Math.floor(Math.random() * pool.length)].split("|");
      window.location.href = "fields/" + pick[0] + ".html#c-" + pick[0] + "-u" + pick[1];
    });
  });

  /* Search page */
  var input = document.getElementById("q");
  var list = document.getElementById("results");
  var shown = document.getElementById("shown");
  if (!input || !list || !window.CENSUS) return;

  var ITEMS = [];
  CENSUS.fields.forEach(function (f) {
    f.built.forEach(function (b, i) {
      ITEMS.push({ f: f, side: "built", i: i, t: b.t, w: b.w });
    });
    f.half.forEach(function (u, i) {
      ITEMS.push({ f: f, side: "half", i: i, t: u.t, w: u.w, why: u.why });
    });
    f.unbuilt.forEach(function (u, i) {
      ITEMS.push({ f: f, side: "unbuilt", i: i, t: u.t, w: u.w, why: u.why });
    });
  });

  var SIDE_LABEL = { built: "crowded", half: "half-built", unbuilt: "not built" };
  var SIDE_CODE = { built: "b", half: "h", unbuilt: "u" };

  function render() {
    var qy = input.value.trim().toLowerCase();
    var hits = ITEMS.filter(function (it) {
      if (!qy) return true;
      return (it.f.name + " " + it.t + " " + it.w + " " + (it.why || "")).toLowerCase().indexOf(qy) !== -1;
    });
    shown.textContent = hits.length + " of " + ITEMS.length + " ideas";
    list.innerHTML = "";
    if (!hits.length) {
      var empty = document.createElement("p");
      empty.className = "shown-more";
      empty.textContent = "Nothing matches — which might itself be a good sign.";
      list.appendChild(empty);
      return;
    }
    hits.slice(0, 60).forEach(function (it) {
      var a = document.createElement("a");
      a.className = "result";
      a.href = "fields/" + it.f.id + ".html#c-" + it.f.id + "-" + SIDE_CODE[it.side] + it.i;
      var side = document.createElement("span");
      side.className = "r-side " + SIDE_CODE[it.side];
      side.textContent = SIDE_LABEL[it.side];
      var title = document.createElement("span");
      title.className = "r-title";
      title.textContent = it.t;
      var fld = document.createElement("span");
      fld.className = "r-field";
      fld.textContent = it.f.name;
      var what = document.createElement("span");
      what.className = "r-what";
      what.textContent = it.w;
      a.appendChild(side); a.appendChild(title); a.appendChild(fld); a.appendChild(what);
      list.appendChild(a);
    });
    if (hits.length > 60) {
      var more = document.createElement("p");
      more.className = "shown-more";
      more.textContent = "First 60 shown — refine the search to narrow further.";
      list.appendChild(more);
    }
  }
  input.addEventListener("input", render);
  render();
})();

/* Idea Atlas tab — searchable + filterable merged atlas */
(function () {
  "use strict";
  var q = document.getElementById("idea-q");
  var results = document.getElementById("idea-results");
  var shown = document.getElementById("idea-shown");
  if (!q || !results || !shown || !window.IDEAS) return;

  var ALL = window.IDEAS;
  var LABEL = { known: "known", debated: "debated", undiscovered: "undiscovered" };
  var CODE = { known: "b", debated: "h", undiscovered: "u" };
  var CATS = {
    physics: "Physics", software: "Software", math: "Math", bio: "Biology",
    art: "Arts & humanities", vectors: "High-dim vectors", space: "Astronomy & space",
    mind: "Mind & psychology", chemistry: "Chemistry", economics: "Economics & society"
  };
  var activeState = "all";
  var activeCat = "all";

  function chips(host, values, current, label, onPick) {
    values.forEach(function (v) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "chip" + (v === current ? " on" : "");
      b.setAttribute("aria-pressed", String(v === current));
      b.textContent = label(v);
      b.addEventListener("click", function () {
        host.querySelectorAll(".chip").forEach(function (c) {
          c.classList.remove("on");
          c.setAttribute("aria-pressed", "false");
        });
        b.classList.add("on");
        b.setAttribute("aria-pressed", "true");
        onPick(v);
      });
      host.appendChild(b);
    });
  }

  chips(document.getElementById("idea-status"),
    ["all", "known", "debated", "undiscovered"],
    activeState,
    function (v) { return v === "all" ? "All states" : LABEL[v]; },
    function (v) { activeState = v; render(); });

  var catVals = ["all"];
  ALL.forEach(function (it) { if (catVals.indexOf(it.category) === -1) catVals.push(it.category); });
  catVals.sort(function (a, b) {
    if (a === "all") return -1;
    if (b === "all") return 1;
    return (CATS[a] || a).localeCompare(CATS[b] || b);
  });
  chips(document.getElementById("idea-cats"), catVals, activeCat,
    function (v) { return v === "all" ? "All fields" : (CATS[v] || v); },
    function (v) { activeCat = v; render(); });

  function render() {
    var term = q.value.trim().toLowerCase();
    var hits = ALL.filter(function (it) {
      if (activeState !== "all" && it.status !== activeState) return false;
      if (activeCat !== "all" && it.category !== activeCat) return false;
      if (!term) return true;
      return (it.title + " " + it.category + " " + it.source + " " + (it.note || "") + " " + (it.era || ""))
        .toLowerCase().indexOf(term) !== -1;
    });
    shown.textContent = hits.length + " of " + ALL.length + " ideas";
    results.innerHTML = "";
    if (!hits.length) {
      var none = document.createElement("p");
      none.className = "shown-more";
      none.textContent = "Nothing matches those filters — try widening the search.";
      results.appendChild(none);
      return;
    }
    hits.slice(0, 120).forEach(function (it) {
      var a = document.createElement("a");
      a.className = "result";
      a.href = it.url;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      var side = document.createElement("span");
      side.className = "r-side " + CODE[it.status];
      side.textContent = LABEL[it.status];
      var title = document.createElement("span");
      title.className = "r-title";
      title.textContent = it.title;
      var fld = document.createElement("span");
      fld.className = "r-field";
      fld.textContent = CATS[it.category] || it.category;
      var meta = document.createElement("span");
      meta.className = "r-what";
      meta.textContent = "Source: " + it.source + (it.era ? " · " + it.era : "") + (it.note ? " · " + it.note : "");
      a.appendChild(side); a.appendChild(title); a.appendChild(fld); a.appendChild(meta);
      results.appendChild(a);
    });
    if (hits.length > 120) {
      var more = document.createElement("p");
      more.className = "shown-more";
      more.textContent = "First 120 shown — refine the search to narrow further.";
      results.appendChild(more);
    }
  }
  q.addEventListener("input", render);
  render();
})();
