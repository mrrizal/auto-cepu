import code
import json
from llm.prompt import CodeReviewPromptGenerator

def load_dataset(filename):
    with open(filename, 'r') as f:
        dataset = json.loads(f.read())
        return dataset

    return None

def sanitize_code(codes):
    if isinstance(codes, list):
        result = []
        for code in codes:
            code["code"] = code["code"].strip().replace("\\n", "\n")
            result.append(code)
        return result
    elif isinstance(codes, str):
        return codes.strip().replace("\\n", "\n")
    return codes

if __name__ == "__main__":
    svc = CodeReviewPromptGenerator()
    filename = "datasets/syntetic_dataset.json"
    for dataset in load_dataset(filename):
        added_code = sanitize_code(dataset["added_code"])
        deleted_code = sanitize_code(dataset["deleted_code"])
        full_function_code = sanitize_code(dataset["full_function_code"])
        function_name = dataset["function_name"]
        prompt = svc.generate_style_review_prompt(
            function_name=function_name,
            full_function_code=full_function_code,
            added_code=added_code,
            deleted_code=deleted_code
        )
        print(prompt)
        print("=======================================")

