/* ================================================
   HENDOSHI - COUNT UP
   ================================================
   
   Purpose: JavaScript functionality for count up
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
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
