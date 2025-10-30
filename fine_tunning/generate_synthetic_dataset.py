import os
import time
from groq import Groq
from dotenv import load_dotenv
from llm.prompt import CodeReviewPromptGenerator


load_dotenv()

def get_seed_dataset():
    for file in os.listdir("seed_datasets"):
        if file.endswith(".json"):
            yield os.path.join("seed_datasets", file)

def hit_inference_model(prompt: str) -> str:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    MODEL_NAME = "llama-3.3-70b-versatile"
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.85,
    )
    return response.choices[0].message.content.strip()

def generate_synthetic_dataset():
    import json

    prompt_generator = CodeReviewPromptGenerator()

    for seed_file in get_seed_dataset():
        synthetic_data = []
        with open(seed_file, 'r') as f:
            data = json.load(f)
            n_data  = len(data)
            for counter, entry in enumerate(data):
                print("Processing {}/{} entries.".format(counter+1, n_data))
                prompt = prompt_generator.generate_style_review_prompt(
                    added_code=entry['added_code'],
                    deleted_code=entry['deleted_code'],
                    full_function_code=entry['full_function_code'],
                    function_name=entry['function_name']
                )
                model_response = hit_inference_model(prompt)
                synthetic_entry = {
                    "function_name": entry['function_name'],
                    "added_code": entry['added_code'],
                    "deleted_code": entry['deleted_code'],
                    "full_function_code": entry['full_function_code'],
                    "code_review_suggestion": model_response
                }
                synthetic_data.append(synthetic_entry)
                time.sleep(1)  # To avoid hitting rate limits

        output_file = f"synthetic_datasets/synthetic_{os.path.basename(seed_file)}"
        with open(output_file, 'w') as out_f:
            json.dump(synthetic_data, out_f, indent=4)
        print(f"Synthetic dataset saved to {output_file}")