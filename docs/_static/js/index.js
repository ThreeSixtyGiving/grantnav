/* Top bar */
document.querySelectorAll('.top-bar__menu-trigger, .off-canvas-menu__trigger').forEach(function (el) {
    el.onclick = function () {
        const offCanvasMenu = document.querySelector('.off-canvas-menu');
        offCanvasMenu.classList.toggle('off-canvas-menu--expanded');
        if (offCanvasMenu.hasAttribute('aria-hidden')) {
            offCanvasMenu.removeAttribute('aria-hidden')
        } else {
            offCanvasMenu.setAttribute('aria-hidden', '')
        }
    };
});

/* sidebar list */
document.querySelectorAll('.sidebar-list__trigger').forEach(function (el) {
    el.onclick = function () {
        
        var target = this.parentNode;
        console.log(target);
        target.classList.toggle('sidebar-list--expanded');
        if (target.hasAttribute('aria-hidden')) {
            target.removeAttribute('aria-hidden')
        } else {
            target.setAttribute('aria-hidden', '')
        }
    };
});