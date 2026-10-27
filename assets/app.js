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
