document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('fitnessChart').getContext('2d');

    const data = window.chartData;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.timestamps, // горизонтальні підписи (дати)
            datasets: [
                // Ліва сторона
                {
                    label: 'Calories Burned (kcal)',
                    data: data.calories,
                    borderColor: '#1e40af',
                    yAxisID: 'y-calories',
                    tension: 0.3,
                    pointRadius: 4,
                },
                {
                    label: 'Max Pull-Ups (reps)',
                    data: data.pullups,
                    borderColor: '#d81b60',
                    yAxisID: 'y-pullups',
                    tension: 0.3,
                    pointRadius: 4,
                },
                {
                    label: 'Burpees per Hour (reps)',
                    data: data.burpees,
                    borderColor: '#8b5cf6',
                    yAxisID: 'y-burpees',
                    tension: 0.3,
                    pointRadius: 4,
                },
                {
                    label: 'Cooper Test (km)',
                    data: data.cooper,
                    borderColor: '#f59e0b',
                    yAxisID: 'y-cooper',
                    tension: 0.3,
                    pointRadius: 4,
                },

                // Права сторона
                {
                    label: '1 km Run Time (min)',
                    data: data.run1km,
                    borderColor: '#10b981',
                    yAxisID: 'y-run1km',
                    tension: 0.3,
                    pointRadius: 4,
                },
                {
                    label: '10 km Run Time (min)',
                    data: data.run10km,
                    borderColor: '#ef4444',
                    yAxisID: 'y-run10km',
                    tension: 0.3,
                    pointRadius: 4,
                },
                {
                    label: 'Waist Change (cm)',
                    data: data.waist_ch,
                    borderColor: '#6366f1',
                    yAxisID: 'y-waist',
                    tension: 0.3,
                    pointRadius: 4,
                },
                {
                    label: 'Testosterone (ng/dL)',
                    data: data.testo,
                    borderColor: '#ec4899',
                    yAxisID: 'y-testosterone',
                    tension: 0.3,
                    pointRadius: 4,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { font: { size: 12 } },
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            interaction: { mode: 'index', intersect: false },
            scales: {
                x: {
                    title: { display: true, text: 'Date', font: { size: 14 } },
                    ticks: { font: { size: 10 }, maxRotation: 45, minRotation: 45 }
                },

                // Ліва сторона
                'y-calories': {
                    type: 'linear',
                    position: 'left',
                    title: { display: true, text: 'Calories Burned (kcal)', font: { size: 12 } },
                    grid: { drawOnChartArea: false }
                },
                'y-pullups': {
                    type: 'linear',
                    position: 'left',
                    title: { display: true, text: 'Max Pull-Ups (reps)', font: { size: 12 } },
                    grid: { drawOnChartArea: false }
                },
                'y-burpees': {
                    type: 'linear',
                    position: 'left',
                    title: { display: true, text: 'Burpees per Hour (reps)', font: { size: 12 } },
                    grid: { drawOnChartArea: false }
                },
                'y-cooper': {
                    type: 'linear',
                    position: 'left',
                    title: { display: true, text: 'Cooper Test (km)', font: { size: 12 } },
                    grid: { drawOnChartArea: false }
                },

                // Права сторона
                'y-run1km': {
                    type: 'linear',
                    position: 'right',
                    title: { display: true, text: '1 km Run Time (min)', font: { size: 12 } },
                    grid: { drawOnChartArea: false }
                },
                'y-run10km': {
                    type: 'linear',
                    position: 'right',
                    title: { display: true, text: '10 km Run Time (min)', font: { size: 12 } },
                    grid: { drawOnChartArea: false }
                },
                'y-waist': {
                    type: 'linear',
                    position: 'right',
                    title: { display: true, text: 'Waist Change (cm)', font: { size: 12 } },
                    grid: { drawOnChartArea: false }
                },
                'y-testosterone': {
                    type: 'linear',
                    position: 'right',
                    title: { display: true, text: 'Testosterone (ng/dL)', font: { size: 12 } },
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });
});