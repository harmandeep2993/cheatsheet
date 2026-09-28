/* === Show / hide the left navigation on wide screens === */

// Adds a button to the header that collapses the guide list, giving the page the full width.
// The choice is remembered in this browser. Phones never see the button: the theme already
// hides the guide list behind its menu icon there.
(function () {
  var HIDDEN_CLASS = "pg-nav-hidden";
  var STORAGE_KEY = "pg-nav-hidden";
  var ICON =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">' +
    '<path d="M3 4h18a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1m1 2v12h5V6zm7 0v12h9V6z"/>' +
    "</svg>";

  // Storage can be blocked (private windows, strict privacy settings); the button still works without it
  function readSaved() {
    try {
      return window.localStorage.getItem(STORAGE_KEY) === "true";
    } catch (error) {
      return false;
    }
  }

  function save(hidden) {
    try {
      window.localStorage.setItem(STORAGE_KEY, hidden ? "true" : "false");
    } catch (error) {
      /* not saved; the setting lasts until the page is left */
    }
  }

  function apply(hidden, button) {
    document.body.classList.toggle(HIDDEN_CLASS, hidden);
    if (button) {
      var label = hidden ? "Show the guide list" : "Hide the guide list";
      button.setAttribute("title", label);
      button.setAttribute("aria-label", label);
      button.setAttribute("aria-pressed", hidden ? "true" : "false");
    }
  }

  function setup() {
    var header = document.querySelector(".md-header__inner");
    var button = document.querySelector(".pg-nav-toggle");
    if (header && !button) {
      button = document.createElement("button");
      button.type = "button";
      button.className = "md-header__button md-icon pg-nav-toggle";
      button.innerHTML = ICON;
      button.addEventListener("click", function () {
        var hidden = !document.body.classList.contains(HIDDEN_CLASS);
        apply(hidden, button);
        save(hidden);
      });
      var logo = header.querySelector(".md-logo");
      header.insertBefore(button, logo ? logo.nextSibling : header.firstChild);
    }
    apply(readSaved(), button);
  }

  if (typeof document$ !== "undefined") {
    // Material for MkDocs publishes every page load (including instant navigation) on document$
    document$.subscribe(setup);
  } else {
    document.addEventListener("DOMContentLoaded", setup);
  }
})();
