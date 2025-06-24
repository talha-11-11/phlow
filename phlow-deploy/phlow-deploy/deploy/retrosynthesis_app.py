import streamlit as st
from rdkit import Chem
import openai
import requests
import os
import sqlite3
from datetime import datetime
import time


from dotenv import load_dotenv

load_dotenv()


openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key is None:
    raise ValueError("No OpenAI API key found in .env file")

openai.api_key = openai_api_key


conn = sqlite3.connect("retrosynthesis.db")
c = conn.cursor()


c.execute("""CREATE TABLE IF NOT EXISTS registered_users
             (username TEXT, password TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS login_records
             (username TEXT, login_time TEXT, status TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS input_output_records
             (username TEXT, input_text TEXT, output_text TEXT, timestamp TEXT)""")

conn.commit()


def extract_reactant_from_response(response):
    try:
        reactant = response.choices[0].message["content"]
        return reactant.strip()
    except (KeyError, IndexError) as e:
        print("Error extracting reactant from response:", e)
        return None


def is_valid(smiles):
    try:
        mol = Chem.MolFromSmiles(smiles)
        return mol is not None
    except Exception as e:
        print(f"Error validating SMILES: {e}")
        return False


def is_commercially_known(reactant):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{reactant}/cids/JSON"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "IdentifierList" in data:
                cids = data["IdentifierList"]["CID"]
                if cids:
                    return True
        return False
    except Exception as e:
        print(f"Error checking in PubChem for SMILES '{reactant}': {e}")
        return False


def generate_prediction(product, reaction_class, username):
    with st.spinner("Predicting..."):
        time.sleep(3)
        prompt = f"Given the product '{product}' and the Class '{reaction_class}', predict the reactant in SMILES format."
        reactants = []
        while True:
            response = openai.ChatCompletion.create(
                model="ft:gpt-3.5-turbo-0613:prixite::9308x6tq",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {
                        "role": "user",
                        "content": f"product: {product}, Class: {reaction_class}",
                    },
                ],
            )
            reactant = extract_reactant_from_response(response)
            if not reactant:
                print("Failed to extract reactant from response.")
                break
            if is_valid(reactant):
                reactants.append(reactant)
                if is_commercially_known(reactant):
                    print(f"Reactant '{reactant}' is commercially known in PubChem.")
                    break
                else:
                    print(
                        f"Reactant '{reactant}' not commercially known in PubChem. Predicting again..."
                    )
                    product = reactant
            else:
                print(f"Invalid reactant '{reactant}'. Predicting again...")
        log_input_output(
            username,
            f"product: {product}, Class: {reaction_class}",
            ", ".join(reactants),
        )
        return reactants


def authenticate():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):

        if verify_credentials(username, password):
            st.sidebar.success("Logged In as: {}".format(username))
            st.session_state.logged_in = True
            st.session_state.username = username

            log_login_time(username, "Success")
        else:
            st.sidebar.error("Invalid Username or Password")
            st.session_state.logged_in = False

    st.sidebar.title("Register")
    new_username = st.sidebar.text_input("New Username")
    new_password = st.sidebar.text_input("New Password", type="password")

    if st.sidebar.button("Register"):
        if register_user(new_username, new_password):
            st.sidebar.success("Registration Successful. You can now login.")
        else:
            st.sidebar.error("Registration Failed. Please try a different username.")


def verify_credentials(username, password):

    c.execute(
        "SELECT * FROM registered_users WHERE username = ? AND password = ?",
        (username, password),
    )
    result = c.fetchone()
    if result:
        return True
    else:
        return False


def register_user(username, password):

    c.execute("SELECT * FROM registered_users WHERE username = ?", (username,))
    result = c.fetchone()
    if result:
        return False
    c.execute(
        "INSERT INTO registered_users (username, password) VALUES (?, ?)",
        (username, password),
    )
    conn.commit()
    return True


def log_login_time(username, status):

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        "INSERT INTO login_records (username, login_time, status) VALUES (?, ?, ?)",
        (username, current_time, status),
    )
    conn.commit()


def log_input_output(username, input_text, output_text):

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        "INSERT INTO input_output_records (username, input_text, output_text, timestamp) VALUES (?, ?, ?, ?)",
        (username, input_text, output_text, current_time),
    )
    conn.commit()


def main():
    st.title("Retrosynthesis Pharma LLM")

    authenticate()

    if not st.session_state.get("logged_in"):
        st.warning("Please login to use the app.")
        return

    st.subheader("Predict Reactants from Products")

    product = st.text_input("Enter Product SMILES (e.g., C1=CC=CC=C1)")
    reaction_class = st.text_input("Enter Reaction Class (e.g., Hydrogenation)")

    if st.button("Predict"):
        if not product or not reaction_class:
            st.warning("Please enter both Product SMILES and Reaction Class.")
        elif not is_valid(product):
            st.error("Invalid Product SMILES. Please enter a valid SMILES.")
        else:
            reactants = generate_prediction(
                product, reaction_class, st.session_state.username
            )
            if reactants:
                st.success("Predicted Reactants:")
                for i, reactant in enumerate(reactants[:-1], 1):
                    if i == len(reactants) - 1 and is_commercially_known(reactant):
                        st.write(f"Reactant {i}: {reactant} (Commercially Known)")
                    else:
                        st.write(f"Reactant {i}: {reactant} (Not Commercially Known)")

                last_reactant = reactants[-1]
                if is_commercially_known(last_reactant):
                    st.write(
                        f"Reactant {len(reactants)}: {last_reactant} (Commercially Known)"
                    )
                else:
                    st.write(
                        f"Reactant {len(reactants)}: {last_reactant} (Not Commercially Known)"
                    )
            else:
                st.error("Failed to predict reactants.")


if __name__ == "__main__":
    main()
