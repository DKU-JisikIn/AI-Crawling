import json

def merge_json_files(input_paths, output_path):
    merged_data = []

    for path in input_paths:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                merged_data.extend(data)
            else:
                print(f"Skipping non-list content in {path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)

# 데이터 병합
merge_json_files(['dku_faq_juk.json', 'dku_qna_juk.json', 'dku_everytime.json'], 'DKU.json')