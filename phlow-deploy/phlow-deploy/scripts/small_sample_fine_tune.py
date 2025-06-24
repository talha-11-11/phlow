import csv
import json
import openai
from dotenv import load_dotenv
import os


load_dotenv()

# Loading variables from .env file
csv_file_path = os.getenv("CSV_FILE_PATH", "default_csv_path.csv")
output_file_path = os.getenv("OUTPUT_FILE_PATH", "default_output.jsonl")

with open(csv_file_path, "r", newline="", encoding="utf-8") as csv_file, open(
    output_file_path, "w", encoding="utf-8"
) as jsonl_file:

    csv_reader = csv.DictReader(csv_file)

    for i, row in enumerate(csv_reader):
        if i >= 5000:
            break

        reactants = row["reactant"]
        reaction_class = row["classes"]
        product = row["product"]

        user_message = {"role": "system", "content": "You are a helpful assistant."}

        input_message = {
            "role": "user",
            "content": f"product: {product}, Class: {reaction_class}",
        }

        assistant_message = {
            "role": "assistant",
            "content": f"The predicted reactant is: {reactants}",
        }

        conversation = [user_message, input_message, assistant_message]

        json.dump({"messages": conversation}, jsonl_file)
        jsonl_file.write("\n")


openai.api_key = os.getenv("OPENAI_API_KEY")
response = openai.File.create(file=open(output_file_path, "rb"), purpose="fine-tune")


file_id = response["id"]


print(f"File ID: {file_id}")


response = openai.FineTuningJob.create(
    training_file=file_id, model="gpt-3.5-turbo-0613"
)


print(response)