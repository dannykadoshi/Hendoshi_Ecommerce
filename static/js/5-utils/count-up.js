/* ================================================
   HENDOSHI - COUNT UP
   ================================================

   Purpose: Animates stat numbers on the About page from 0 to their target value
            using an easeOutCubic curve via requestAnimationFrame

   Contains:
   - easeOutCubic() — easing function for smooth deceleration
   - animateTo() — requestAnimationFrame loop that increments a DOM element's text
   - init() — queries all .about-stat-card .stat-number elements and kicks off animation
   - Handles compact units (K, M) and arbitrary trailing text (%, +, etc.)

   Dependencies: None (vanilla JS, no external libraries)
   Load Order: Load on About page only
   ================================================ */

// Small count-up utility for about page stats
(function(){
    function easeOutCubic(t){ return 1 - Math.pow(1 - t, 3); }
    function formatNumber(n){ return n.toLocaleString(); }

    function animateTo(el, endVal, duration, formatter){
        const startVal = 0;
        const startTime = performance.now();
        function frame(now){
            const progress = Math.min((now - startTime) / duration, 1);
            const eased = easeOutCubic(progress);
            const curr = Math.floor(startVal + (endVal - startVal) * eased);
            el.textContent = formatter(curr);
            if (progress < 1) requestAnimationFrame(frame);
        }
        requestAnimationFrame(frame);
    }

    function init(){
        const nodes = document.querySelectorAll('.about-stat-card .stat-number');
        nodes.forEach(el => {
            const raw = el.textContent.trim();
            // capture number, optional unit (K/M), and any trailing text (plus, percent, dash text)
            const m = raw.match(/^([0-9.,]+)([KkMm]?)(.*)$/);
            if (!m) return;
            const num = parseFloat(m[1].replace(/,/g, '')) || 0;
            const unit = (m[2] || '');
            const rest = (m[3] || '');

            if (unit.toLowerCase() === 'k' || unit.toLowerCase() === 'm') {
                // animate the compact unit (e.g. 10K -> animate 0..10 then append K and any suffix)
                const unitTarget = Math.round(num);
                el.textContent = '0' + unit + rest;
                animateTo(el, unitTarget, 1400, v => v + unit + rest);
            } else {
                const target = Math.round(num);
                el.textContent = '0' + rest;
                animateTo(el, target, 1400, v => formatNumber(v) + rest);
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
