
document.addEventListener('DOMContentLoaded', function () {
    const slider = document.getElementById('probability-slider');
    const valueSpan = document.getElementById('probability-value');
    const vapan = document.getElementById('threshold-display');
    slider.addEventListener('input', function () {
        valueSpan.textContent = slider.value + '%';
        vapan.textContent = slider.value + '%';
    });
});
