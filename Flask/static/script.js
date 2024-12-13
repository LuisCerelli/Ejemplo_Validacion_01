let metricsChart;

// Función principal para validar textos y generar métricas
function validateAndMetrics() {
    const texts = document.getElementById('generated-texts').value.split('\n').map(t => t.trim()).filter(t => t);

    if (texts.length === 0) {
        alert('Por favor, introduce al menos un texto.');
        return;
    }

    fetch('/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texts: texts }),
    })
    .then(response => response.json())
    .then(data => {
        const predictedLabels = data.predicted_labels;

        document.getElementById('validation-result').textContent = `Resultados de Validación: ${predictedLabels.join(', ')}`;

        return fetch('/metrics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ predicted_labels: predictedLabels }),
        });
    })
    .then(response => response.json())
    .then(metricsData => renderChart(metricsData))
    .catch(error => console.error('Error:', error));
}

// Renderizar métricas como gráfico
function renderChart(metricsData) {
    const labels = Object.keys(metricsData).filter(key => key !== 'accuracy' && key !== 'macro avg' && key !== 'weighted avg');
    const precision = labels.map(label => metricsData[label].precision);
    const recall = labels.map(label => metricsData[label].recall);
    const f1Score = labels.map(label => metricsData[label]['f1-score']);

    // Ordenar las etiquetas en el mismo orden que la validación
    const orderedLabels = ['valido', 'no-valido']; // Cambia según el orden deseado
    const orderedPrecision = orderedLabels.map(label => precision[labels.indexOf(label)]);
    const orderedRecall = orderedLabels.map(label => recall[labels.indexOf(label)]);
    const orderedF1Score = orderedLabels.map(label => f1Score[labels.indexOf(label)]);

    const ctx = document.getElementById('metricsChart').getContext('2d');

    if (metricsChart) metricsChart.destroy();

    metricsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: orderedLabels,
            datasets: [
                { label: 'Precisión', data: orderedPrecision, backgroundColor: 'rgba(54, 162, 235, 0.6)' },
                { label: 'Recall', data: orderedRecall, backgroundColor: 'rgba(75, 192, 192, 0.6)' },
                { label: 'F1-Score', data: orderedF1Score, backgroundColor: 'rgba(255, 99, 132, 0.6)' },
            ],
        },
        options: {
            scales: {
                y: { beginAtZero: true },
            },
        },
    });
}

