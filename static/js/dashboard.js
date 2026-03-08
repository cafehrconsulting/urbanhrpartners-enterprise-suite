document.addEventListener("DOMContentLoaded", function () {
    const dashboardData = window.dashboardData || {};

    const clientCountEl = document.getElementById("clientCount");
    const employeeCountEl = document.getElementById("employeeCount");
    const revenueEl = document.getElementById("revenue");
    const incidentCountEl = document.getElementById("incidentCount");
    const revenueChartCanvas = document.getElementById("revenueChart");
    const xiomyWidget = document.getElementById("xiomyWidget");

    const clientCount = toNumber(dashboardData.clientCount, 0);
    const employeeCount = toNumber(dashboardData.employeeCount, 0);
    const revenueTotal = toNumber(dashboardData.revenueTotal, 0);
    const incidentCount = toNumber(dashboardData.incidentCount, 0);

    const revenueLabels = Array.isArray(dashboardData.revenueLabels)
        ? dashboardData.revenueLabels
        : ["Jan", "Feb", "Mar", "Apr", "May", "Jun"];

    const revenueValues = Array.isArray(dashboardData.revenueValues)
        ? dashboardData.revenueValues.map(function (value) {
              return toNumber(value, 0);
          })
        : [0, 0, 0, 0, 0, 0];

    animateMetric(clientCountEl, clientCount, false);
    animateMetric(employeeCountEl, employeeCount, false);
    animateMetric(incidentCountEl, incidentCount, false);
    animateMetric(revenueEl, revenueTotal, true);

    initializeRevenueChart(revenueChartCanvas, revenueLabels, revenueValues);
    initializeModuleButtons();
    initializeXiomyWidget(xiomyWidget);
    initializeSectionAnimations();
});

function toNumber(value, fallback) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
}

function formatCurrency(value) {
    try {
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    } catch (error) {
        return "$" + Number(value || 0).toFixed(2);
    }
}

function animateMetric(element, targetValue, isCurrency) {
    if (!element) {
        return;
    }

    const duration = 1200;
    const frameRate = 30;
    const totalFrames = Math.max(1, Math.round(duration / frameRate));
    const increment = targetValue / totalFrames;

    let currentValue = 0;
    let frame = 0;

    const timer = setInterval(function () {
        frame += 1;
        currentValue += increment;

        if (frame >= totalFrames) {
            currentValue = targetValue;
            clearInterval(timer);
        }

        if (isCurrency) {
            element.textContent = formatCurrency(currentValue);
        } else {
            element.textContent = Math.round(currentValue).toLocaleString("en-US");
        }
    }, frameRate);
}

function initializeRevenueChart(canvas, labels, values) {
    if (!canvas) {
        return;
    }

    if (typeof Chart === "undefined") {
        console.warn("Chart.js is not loaded.");
        return;
    }

    const ctx = canvas.getContext("2d");

    new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Revenue",
                    data: values,
                    borderColor: "#d4af37",
                    backgroundColor: "rgba(212, 175, 55, 0.15)",
                    borderWidth: 3,
                    fill: true,
                    tension: 0.35,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: "#1e3a5f",
                    pointBorderColor: "#d4af37",
                    pointBorderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: "index"
            },
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: "#e5e7eb",
                        font: {
                            size: 13,
                            weight: "600"
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const value = context.parsed.y || 0;
                            return " Revenue: " + formatCurrency(value);
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: "#cbd5e1"
                    },
                    grid: {
                        color: "rgba(255,255,255,0.08)"
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: "#cbd5e1",
                        callback: function (value) {
                            return formatCurrency(value);
                        }
                    },
                    grid: {
                        color: "rgba(255,255,255,0.08)"
                    }
                }
            }
        }
    });
}

function initializeModuleButtons() {
    const moduleButtons = document.querySelectorAll(".module-button");

    moduleButtons.forEach(function (button, index) {
        button.style.opacity = "0";
        button.style.transform = "translateY(18px)";
        button.style.transition =
            "opacity 0.45s ease, transform 0.45s ease, box-shadow 0.25s ease, transform 0.25s ease";

        setTimeout(function () {
            button.style.opacity = "1";
            button.style.transform = "translateY(0)";
        }, 120 + index * 70);

        button.addEventListener("mouseenter", function () {
            button.style.transform = "translateY(-4px) scale(1.01)";
            button.style.boxShadow = "0 12px 24px rgba(0, 0, 0, 0.25)";
        });

        button.addEventListener("mouseleave", function () {
            button.style.transform = "translateY(0) scale(1)";
            button.style.boxShadow = "";
        });
    });
}

function initializeXiomyWidget(widget) {
    if (!widget) {
        return;
    }

    widget.style.cursor = "pointer";
    widget.style.transition = "transform 0.25s ease, box-shadow 0.25s ease, opacity 0.25s ease";

    widget.addEventListener("mouseenter", function () {
        widget.style.transform = "scale(1.06)";
        widget.style.boxShadow = "0 0 24px rgba(212, 175, 55, 0.35)";
        widget.style.opacity = "1";
    });

    widget.addEventListener("mouseleave", function () {
        widget.style.transform = "scale(1)";
        widget.style.boxShadow = "";
        widget.style.opacity = "";
    });

    widget.addEventListener("click", function () {
        triggerXiomyPulse(widget);

        if (typeof xiomySpeak === "function") {
            xiomySpeak("Opening XIOMY executive interface.");
        }
    });

    widget.addEventListener("keypress", function (event) {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            triggerXiomyPulse(widget);

            if (typeof xiomySpeak === "function") {
                xiomySpeak("Opening XIOMY executive interface.");
            }

            widget.click();
        }
    });
}

function triggerXiomyPulse(widget) {
    if (!widget) {
        return;
    }

    widget.style.transform = "scale(0.96)";

    setTimeout(function () {
        widget.style.transform = "scale(1.08)";
    }, 120);

    setTimeout(function () {
        widget.style.transform = "scale(1)";
    }, 260);
}

function initializeSectionAnimations() {
    const sections = document.querySelectorAll(
        ".hero-panel, .metrics-section, .modules-section, .analytics-section, .xiomy-panel"
    );

    if (!("IntersectionObserver" in window)) {
        sections.forEach(function (section) {
            section.classList.add("visible");
        });
        return;
    }

    const observer = new IntersectionObserver(
        function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("visible");
                    observer.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.15
        }
    );

    sections.forEach(function (section) {
        observer.observe(section);
    });
}