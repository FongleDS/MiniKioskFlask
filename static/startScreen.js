
function maintainAspectRatio() {
    const desiredRatio = 10 / 16;
    const currentWidth = window.innerWidth;
    const calculatedHeight = currentWidth * desiredRatio;
    
    document.body.style.height = calculatedHeight + "px";
}

window.addEventListener("resize", maintainAspectRatio);
maintainAspectRatio();
