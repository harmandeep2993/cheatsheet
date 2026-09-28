/* === Diagrams: start scrolled to the middle on narrow screens === */

// Diagrams keep a readable minimum width on phones and scroll sideways (see extra.css).
// Scrolled all the way left, the first view shows boxes cut in half, so centre each one
// once the diagram has been drawn, unless the reader has already scrolled it.
(function () {
  function centre(box) {
    if (box.dataset.pgTouched === "true") {
      return;
    }
    var overflow = box.scrollWidth - box.clientWidth;
    if (overflow > 0) {
      box.scrollLeft = overflow / 2;
    }
  }

  function watch(box) {
    if (box.dataset.pgWatched === "true") {
      return;
    }
    box.dataset.pgWatched = "true";
    box.addEventListener("pointerdown", function () {
      box.dataset.pgTouched = "true";
    });
    box.addEventListener("touchstart", function () {
      box.dataset.pgTouched = "true";
    }, { passive: true });
    // Mermaid draws after page load: the theme swaps the code block for a new element, whose size
    // then changes when the drawing appears. Watch both, and re-centre after each change.
    var resized = new ResizeObserver(function () {
      centre(box);
    });
    function observeChildren() {
      Array.prototype.forEach.call(box.children, function (child) {
        resized.observe(child);
      });
      centre(box);
    }
    new MutationObserver(observeChildren).observe(box, { childList: true, subtree: true });
    observeChildren();
  }

  function setup() {
    document.querySelectorAll(".pg-diagram").forEach(watch);
  }

  if (typeof document$ !== "undefined") {
    // Material for MkDocs publishes every page load (including instant navigation) on document$
    document$.subscribe(setup);
  } else {
    document.addEventListener("DOMContentLoaded", setup);
  }
})();
