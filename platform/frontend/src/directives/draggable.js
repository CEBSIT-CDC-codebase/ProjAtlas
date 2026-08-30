// drag.js
export default {
  inserted: function(el) {
    const header = el.querySelector(".atlas-draggable-header");
    if (!header) return;
    header.style.cursor = "move";

    header.onmousedown = function(e) {
      // Check whether the click target is the header or one of its children
      // Must not be an icon
      if (["path", "svg", "g"].includes(e.target?.tagName)) return;
      if (!header.contains(e.target)) {
        return (document.onmousemove = document.onmouseup = null);
      }

      // Get the current mouse position within the DOM
      let disx = e.clientX - el.offsetLeft;
      let disy = e.clientY - el.offsetTop;

      document.onmousemove = function(e) {
        // Get the mouse's current distance from the left and top edges after moving
        let x = e.clientX - disx;
        let y = e.clientY - disy;

        // Get the maximum distance the mouse can move horizontally and vertically
        let maxX =
          document.body.clientWidth -
          parseInt(window.getComputedStyle(el).width);
        let maxY =
          document.body.clientHeight -
          parseInt(window.getComputedStyle(el).height) -
          102;

        if (x < 0) {
          x = 0;
        } else if (x > maxX) {
          x = maxX;
        }

        if (y < 0) {
          y = 0;
        } else if (y > maxY) {
          y = maxY;
        }

        el.style.left = x + "px";
        el.style.top = y + "px";
      };

      document.onmouseup = function() {
        document.onmousemove = document.onmouseup = null;
      };

      e.stopPropagation();
    };
  }
};
