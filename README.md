# Retrosynthesis Route Prediction Tool

This project is a Proof of Concept (POC) application designed to predict retrosynthesis routes for chemical compounds using generative AI. It leverages **OpenAI's GPT-3.5 Turbo** model to generate multi-step synthesis pathways starting from the final product and tracing back to commercially available reactants. The tool is equipped with a simple and intuitive **Streamlit frontend** (`retrosynthesis-app.py`), accessible via a web browser.

## 🚀 Features

- 🔁 Recursive single-step retrosynthesis to build complete synthesis routes.
- 🤖 Predictions powered by **OpenAI GPT-3.5 Turbo**.
- 🌐 Web-based interface built with **Streamlit**.
- 🧪 Outputs valid **SMILES** strings for each reaction step.
- 📦 Routes terminate at valid, commercially available reactants.

## 🧠 How It Works

1. **Input** a target product's SMILES string in the web app.
2. The app queries **GPT-3.5 Turbo** to predict possible retrosynthesis steps.
3. Each prediction step is validated and used recursively until starting reactants are reached.
4. The complete synthesis path is displayed in the browser.
