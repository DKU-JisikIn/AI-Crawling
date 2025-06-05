import pandas as pd
import json

everytime = pd.read_excel("Everytime.xlsx")

def safe_strip(val):
    return str(val).strip() if pd.notnull(val) else ""

# 소분류 -> 대분류 매핑 딕셔너리
subcategory_to_category = {
    '학적': '학사', '성적': '학사', '수업': '학사', '교양': '학사', '교직': '학사',
    '복지시설': '일반', '예비군': '일반', '등록': '일반', 'it서비스': '일반', '도서관': '일반',
    '기타': '일반', '기숙사': '일반', '제증명/학생증': '일반', '학생지원/교통': '일반',
    '장학': '장학',
    '외국인유학생': '국제', '한국어연수': '국제', '교환학생': '국제', '어학연수': '국제',
    '취업': '진로', '대학원': '진로', '자격증': '진로',
    '동아리': '동아리'
}

# 교양/수업은 소분류를 '수업'으로 통일
def normalize_subcategory(subcategory):
    if subcategory in ['교양', '수업']:
        return '수업'
    return subcategory

def parse_blank_column_comments(df, output_json, campus="죽전"):
    data = []
    prev_question = ""
    prev_subcategory = ""
    comment_start_idx = df.columns.get_loc('댓글')
    question_id_map = {}
    id_counter = 1

    for _, row in df.iterrows():
        raw_subcategory = safe_strip(row.get('소분류', ''))
        subcategory = normalize_subcategory(raw_subcategory)
        title = safe_strip(row.get('제목', ''))
        content = safe_strip(row.get('내용', ''))
        question = f"{title} - {content}" if title and content else title or content

        # 질문, 소분류 아래로 내리기
        if not question or question.strip() == "-":
            question = prev_question
        else:
            prev_question = question

        if not subcategory or subcategory.strip() == "-":
            subcategory = prev_subcategory
        else:
            prev_subcategory = subcategory

        # 대분류 매핑
        category = subcategory_to_category.get(subcategory, "")

        # ID 생성
        if question not in question_id_map:
            question_id_map[question] = f"customid_{id_counter:03d}"
            id_counter += 1
        question_id = question_id_map[question]

        # 댓글 열부터 오른쪽 끝까지 데이터 가져오기
        comment_cells = [safe_strip(row[col]) for col in df.columns[comment_start_idx:]]

        # 빈 셀로 스레드 그룹 구분
        threads = []
        current = []
        for cell in comment_cells:
            if cell:
                current.append(cell)
            elif current:
                threads.append(current)
                current = []
        if current:
            threads.append(current)

        # 스레드가 없으면 빈 답변 포함
        if not threads:
            data.append({
                "id": question_id,
                "campus": campus,
                "category": category,
                "subcategory": subcategory,
                "question": question,
                "answer": "",
                "source": "Everytime"
            })
        else:
            for thread in threads:
                answer = " - ".join(thread)
                data.append({
                    "id": question_id,
                    "campus": campus,
                    "category": category,
                    "subcategory": subcategory,
                    "question": question,
                    "answer": answer,
                    "source": "Everytime"
                })

    # JSON 저장
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

parse_blank_column_comments(everytime, 'dku_everytime.json')