(function () {
  var head = document.querySelector(".ruler .head");
  if (!head) return;

  var ruler = head.parentElement;
  var queued = false;

  function update() {
    queued = false;
    var max = document.documentElement.scrollHeight - window.innerHeight;
    var p = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
    head.style.transform = "translateY(" + p * (ruler.clientHeight - 2) + "px)";
  }

  window.addEventListener("scroll", function () {
    if (!queued) {
      queued = true;
      requestAnimationFrame(update);
    }
  }, { passive: true });

  window.addEventListener("resize", update);
  update();
})();
