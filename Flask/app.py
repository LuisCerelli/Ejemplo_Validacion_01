from flask import Flask, render_template, request, jsonify
import wikipedia
from sklearn.metrics import classification_report

app = Flask(__name__)

# Configura el idioma en español para Wikipedia
wikipedia.set_lang("es")

# Simulación de etiquetas verdaderas
TRUE_LABELS = ["valido", "no-valido"]

# Función para validar texto con Wikipedia
def validate_text(text):
    try:
        search_results = wikipedia.search(text[:100])
        if not search_results:
            return {"valid": False, "source": "No se encontraron resultados en Wikipedia."}

        summary = wikipedia.summary(search_results[0])

        # Detectar resultados ambiguos
        if "may refer to" in summary.lower() or "puede referirse a" in summary.lower():
            return {"valid": False, "source": summary}

        # Dividimos el texto en palabras y verificamos cuántas están en el resumen
        words = text.lower().split()
        matched_words = [word for word in words if word in summary.lower()]
        match_ratio = len(matched_words) / len(words)

        # Considera válido si al menos el 70% de las palabras coinciden
        valid = match_ratio >= 0.7
        return {"valid": valid, "source": summary}
    except Exception as e:
        return {"valid": False, "source": f"Error al consultar Wikipedia: {str(e)}"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate():
    data = request.json
    generated_texts = data.get('texts', [])

    if not generated_texts:
        return jsonify({"error": "No se proporcionaron textos para validar."}), 400

    predicted_labels = []
    for text in generated_texts:
        validation_result = validate_text(text)
        print(f"Texto: {text}")
        print(f"Resultado: {validation_result}")
        predicted_labels.append("valido" if validation_result["valid"] else "no-valido")

    print("Etiquetas predichas:", predicted_labels)
    return jsonify({"predicted_labels": predicted_labels})

@app.route('/metrics', methods=['POST'])
def metrics():
    data = request.json
    predicted_labels = data.get('predicted_labels', [])

    # Ajusta las etiquetas verdaderas para que coincidan con el número de textos ingresados
    adjusted_true_labels = TRUE_LABELS[:len(predicted_labels)]

    print("Etiquetas Verdaderas:", adjusted_true_labels)
    print("Etiquetas Predichas:", predicted_labels)

    if len(predicted_labels) != len(adjusted_true_labels):
        return jsonify({"error": "El número de etiquetas predichas no coincide con el número de etiquetas verdaderas."}), 400

    try:
        # Calcula el reporte de métricas
        report = classification_report(adjusted_true_labels, predicted_labels, output_dict=True, zero_division=0)
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
