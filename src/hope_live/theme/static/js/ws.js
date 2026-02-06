document.addEventListener("DOMContentLoaded", () => {
    const address = "ws://" + window.location.host + "/ws/listener/";
    let interval = null;
    let connectionError = 0;

    function init() {
        if (connectionError >= 6) {
            clearInterval(interval);
            console.log("Connection Error: Aborted");
            return;
        }

        let chatSocket = new WebSocket(address);

        chatSocket.onclose = function () {
            document.body.classList.add("offline");
            interval = setInterval(init, 10000);
            connectionError++;
        };

        chatSocket.onerror = function () {
            document.body.classList.add("offline");
            chatSocket.close();
        };

        chatSocket.onopen = function () {
            document.body.classList.remove("offline");
            if (interval) {
                clearInterval(interval);
                interval = null;
            }
        };

        chatSocket.onmessage = function (e) {
            const payload = JSON.parse(e.data);
            console.log(payload);

            // Check if it's the dataset we are interested in
            if (!payload.domain || payload.domain.indexOf("hcr.dataset.save") === -1) {
                return;
            }

            const container = document.getElementById('live-data-container');
            if (!container) {
                console.error('live-data-container not found!');
                return;
            }

            try {
                const records = JSON.parse(payload.message.data);
                if (!records || records.length === 0) {
                    container.innerHTML = '<p>Received empty dataset.</p>';
                    return;
                }

                const headers = Object.keys(records[0]);
                let tableHTML = '<table class="table table-zebra w-full"><thead><tr>';
                headers.forEach(h => tableHTML += `<th>${h}</th>`);
                tableHTML += '</tr></thead><tbody>';

                records.forEach(row => {
                    tableHTML += '<tr>';
                    headers.forEach(h => tableHTML += `<td>${row[h]}</td>`);
                    tableHTML += '</tr>';
                });

                tableHTML += '</tbody></table>';
                container.innerHTML = tableHTML;

            } catch (error) {
                console.error("Failed to parse or render dataset", error);
                container.innerHTML = '<p class="text-error">Error processing received data.</p>';
            }
        };
        console.log(`Channel initialised at ${address}`)
    }

    init();
});
