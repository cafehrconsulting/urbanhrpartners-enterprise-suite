fetch('/api/analytics')
    .then(res => res.json())
    .then(data => {
        document.getElementById('clientCount').innerText = data.clients;
        document.getElementById('employeeCount').innerText = data.employees;
        document.getElementById('revenue').innerText = '$' + data.revenue;
        document.getElementById('incidentCount').innerText = data.incidents;

        const ctx = document.getElementById('revenueChart');

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Revenue', 'Invoices'],
                datasets: [{
                    label: 'Financial Overview',
                    data: [data.revenue, data.invoices],
                    backgroundColor: ['gold', 'orange']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            color: 'white'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: 'white' }
                    },
                    y: {
                        ticks: { color: 'white' }
                    }
                }
            }
        });
    })
    .catch(error => {
        console.error('Dashboard analytics error:', error);
    });