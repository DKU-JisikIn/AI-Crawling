import pandas as pd
import json

everytime = pd.read_excel("Everytime.xlsx")

def safe_strip(val):
    return str(val).strip() if pd.notnull(val) else ""

def parse_blank_column_comments(df, output_json, campus="죽전"):
    data = []
    prev_question = ""
    comment_start_idx = df.columns.get_loc('댓글')
    question_id_map = {}  # 질문 -> id 매핑
    id_counter = 1

    for _, row in df.iterrows():
        category = safe_strip(row.get('분류', ''))
        title = safe_strip(row.get('제목', ''))
        content = safe_strip(row.get('내용', ''))
        question = f"{title} - {content}" if title and content else title or content

        if not question or question.strip() == "-":
            question = prev_question
        else:
            prev_question = question

        # 질문 ID 생성 또는 가져오기
        if question not in question_id_map:
            question_id_map[question] = f"everytime_{id_counter:03d}"
            id_counter += 1
        question_id = question_id_map[question]

        # 댓글 열부터 오른쪽 값들 가져오기
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
                "question": question,
                "answer": "",  # 답변 없음
                "source": "Everytime"
            })
        else:
            for thread in threads:
                answer = " - ".join(thread)
                data.append({
                    "id": question_id,
                    "campus": campus,
                    "category": category,
                    "question": question,
                    "answer": answer,
                    "source": "Everytime"
                })

    # JSON 저장
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

parse_blank_column_comments(everytime, 'dku_everytime.json')