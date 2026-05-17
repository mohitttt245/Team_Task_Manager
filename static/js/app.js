document.addEventListener("DOMContentLoaded", () => {
    initializeToasts();
    initializeBootstrapValidation();
    initializeCharts();
});

function initializeToasts() {
    const toastElements = document.querySelectorAll(".toast");
    toastElements.forEach((element) => {
        const toast = new bootstrap.Toast(element);
        toast.show();
    });
}

function initializeBootstrapValidation() {
    const forms = document.querySelectorAll(".needs-validation");
    forms.forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add("was-validated");
        });
    });
}

function initializeCharts() {
    renderChartFromScript("statusChart", "status-breakdown-data", {
        type: "doughnut",
        backgroundColor: ["#94a3b8", "#f59e0b", "#22c55e"],
    });
    renderChartFromScript("priorityChart", "priority-breakdown-data", {
        type: "bar",
        backgroundColor: ["#0ea5e9", "#fb923c", "#ef4444"],
    });
    renderChartFromScript("memberStatusChart", "member-status-breakdown-data", {
        type: "bar",
        backgroundColor: ["#94a3b8", "#f59e0b", "#22c55e"],
    });
}

function renderChartFromScript(canvasId, scriptId, styleOptions) {
    const canvas = document.getElementById(canvasId);
    const script = document.getElementById(scriptId);
    if (!canvas || !script) {
        return;
    }

    const breakdown = JSON.parse(script.textContent);
    const labels = breakdown.map((item) => humanizeLabel(item.status || item.priority || "Unknown"));
    const values = breakdown.map((item) => item.total);

    new Chart(canvas, {
        type: styleOptions.type,
        data: {
            labels,
            datasets: [
                {
                    label: "Tasks",
                    data: values,
                    backgroundColor: styleOptions.backgroundColor,
                    borderRadius: 12,
                    borderWidth: 0,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: styleOptions.type === "doughnut",
                    position: "bottom",
                },
            },
            scales: styleOptions.type === "bar" ? {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0,
                    },
                    grid: {
                        color: "rgba(148, 163, 184, 0.18)",
                    },
                },
                x: {
                    grid: {
                        display: false,
                    },
                },
            } : {},
        },
    });
}

function humanizeLabel(value) {
    return value
        .toLowerCase()
        .split("_")
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(" ");
}
