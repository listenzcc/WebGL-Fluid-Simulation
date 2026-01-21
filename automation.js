/**
 * Automatically splat
 */

/**
 * Use the function splat(x, y, dx, dy, color)
 * to send a splat to the random coordinates with the random color.
 */
function sendSplat() {
    let n, x, y, dx, dy, color;

    // Continue n points
    n = Math.random() * 4 + 2;

    x = Math.random();
    y = Math.random();
    for (let i = 0; i < n; i++) {
        x += (Math.random() - 0.5) * 0.1;
        y += (Math.random() - 0.5) * 0.1;

        // I want dx, dy at larger scale
        dx = (Math.random() - 0.5) * 1000;
        dy = (Math.random() - 0.5) * 1000;

        color = { r: Math.random(), g: Math.random(), b: Math.random() };
        splat(x, y, dx, dy, color);
    }
}

// Send a splat every 1000 milliseconds
setInterval(sendSplat, 1000);