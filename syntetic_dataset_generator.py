import os
import json
from llm.prompt import CodeReviewPromptGenerator
from pprint import pprint

def open_dataset(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    else:
        return "File does not exist."


if __name__ == "__main__":
    code_reivew_prompt = CodeReviewPromptGenerator()
    dataset_files = os.listdir('datasets')
    total_data = 0
    for file in dataset_files:
        if file.endswith('.json'):
            file_path = os.path.join('datasets', file)
            data = open_dataset(file_path)
            # for item in data:
            #     prompt = code_reivew_prompt.generate_style_review_prompt(
            #         added_code=item['added_code'],
            #         deleted_code=item['deleted_code'],
            #         full_function_code=item['full_function_code'],
            #         function_name=item['function_name'],
            #     )
            #     print("Prompt for code review:\n")
            #     print(prompt)
            #     print("============================================")
            # exit(0)
            total_data += len(data)
    print("Total data points:", total_data)