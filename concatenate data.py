import json
import pandas as pd

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

data = pd.read_json('DKU.json')

# 데이터 구조 일반화
ordered_keys = ["id", "campus", "category", "subcategory", "question", "answer", "source"]
data = data[ordered_keys]

# id 컬럼을 1부터 순차적으로 할당
data['id'] = range(1, len(data) + 1)

## category 및 subcategory 값 변경
# source가 'VOC'인 행만 category 값을 subcategory로 변경 및 category 비움
data.loc[data['source'] == 'VOC', 'subcategory'] = data.loc[data['source'] == 'VOC', 'category']
data.loc[data['source'] == 'VOC', 'category'] = None

def get_unique_categories(df):
    """
    데이터프레임에서 'subcategory' 컬럼의 고유값(종류)을 리스트로 반환합니다.
    
    Args:
        df (pd.DataFrame): 데이터프레임
        
    Returns:
        List: category 컬럼의 고유값 리스트
    """
    return df['subcategory'].unique().tolist()

unique_categories = get_unique_categories(data)
print(unique_categories)

# 세부 카테고리 수정
category_map = {
    '교환학생': '국제교류(교환학생,어학연수)',
    '어학연수': '국제교류(교환학생,어학연수)',
    '모바일App': 'IT서비스',
    'it서비스': 'IT서비스',
    'Gmail': 'IT서비스',
    '생활관': '기숙사',
    '수업(이러닝)': '수업',
    '졸업': '학사',
    '평생교육사': '기타',
    '수업시설(전자교탁)': '기타',
    '일반시설': '기타',
    'VOC': '기타',
    '복합질문': '기타',
    '학생(교직원)식당': '복지시설'
}
data['subcategory'] = data['subcategory'].replace(category_map)

print(data['subcategory'].unique())

category_to_main = {
    # 학사
    '학적': '학사',
    '성적': '학사',
    '수업': '학사',
    '교직': '학사',

    # 일반
    '복지시설': '일반',
    '예비군': '일반',
    '등록': '일반',
    'IT서비스': '일반',
    '도서관': '일반',
    '기타': '일반',
    '기숙사': '일반',
    '제증명/학생증': '일반',
    '학생지원/교통': '일반',

    # 장학
    '장학': '장학',

    # 국제
    '국제(외국인유학생,한국어연수)': '국제',
    '국제교류(교환학생,어학연수)': '국제',

    # 진로
    '취업': '진로',
    '대학원': '진로',
    '자격증': '진로',

    # 동아리
    '동아리': '동아리'
}
data['category'] = data['subcategory'].map(category_to_main)

data.to_json('DKU_fin.json', force_ascii=False, orient='records', indent=2)