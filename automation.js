/**
 * Automatically splat
 */

/**
 * Use the function splat(x, y, dx, dy, color)
 * to send a splat to the random coordinates with the random color.
 */
function sendSplat(x = undefined, y = undefined) {
    let n, dx, dy, color;

    // Continue n points
    n = Math.random() * 4 + 2;

    if (x === undefined) x = Math.random();
    if (y === undefined) y = Math.random();

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

// Send a splat every 5000 milliseconds
// setInterval(sendSplat, 5000);

let eventSource = null;

// 连接SSE
function connectSSE() {
    if (eventSource) {
        eventSource.close();
    }

    eventSource = new EventSource('http://localhost:8693/sse');

    eventSource.onopen = function () {
        console.log('SSE连接已建立');
    };

    eventSource.onmessage = function (event) {
        try {
            const data = JSON.parse(event.data);
            console.log('收到数据:', data);
            const { x, y } = data;
            sendSplat(x, 1 - y);
        } catch (error) {
            console.error('解析数据时出错:', error);
        }
    };

    eventSource.onerror = function (error) {
        console.error('SSE连接错误:', error);
        if (eventSource.readyState === EventSource.CLOSED) {
            console.error('连接已断开');
        }
    };
}

// 断开SSE连接
function disconnectSSE() {
    if (eventSource) {
        eventSource.close();
        eventSource = null;
        console.log('SSE连接已关闭');
    }
}

connectSSE();