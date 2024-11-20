document.getElementById('predictionForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const feature1 = document.getElementById('feature1').value;
    const feature2 = document.getElementById('feature2').value;

    const response = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ features: [feature1, feature2] })
    });

    const result = await response.json();
    document.getElementById('result').textContent = `Prediction: ${result.prediction}`;
});
