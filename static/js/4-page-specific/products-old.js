/**
 * Products Old Page Scripts
 * Sort selector redirect
 */

document.getElementById('sort-selector').addEventListener('change', function() {
    window.location.href = this.value;
});
