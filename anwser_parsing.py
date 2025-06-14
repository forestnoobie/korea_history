from PyPDF2 import PdfReader
import re
import pandas as pd
import os

# 1. PDF 파일 읽기
pdf_path = "./data/74회 심화 정답표.pdf"
reader = PdfReader(pdf_path)
page = reader.pages[0]          # 정답표가 있는 페이지 인덱스
text = page.extract_text()      # 전체 텍스트 추출

# 2. 텍스트를 줄 단위로 분리
lines = text.splitlines()

# 3. 숫자로 시작하고 '①'~'⑤' 패턴이 포함된 데이터 라인만 필터링
data_lines = [line[:20] for line in lines if re.match(r'^\d+[①-⑤]', line)]

# 4. 원하는 블록(여기서는 첫 10줄)만 선택
raw = "\n".join(data_lines[:10])

# 5. 원형숫자를 일반 숫자로 매핑
num_map = {"①": 1, "②": 2, "③": 3, "④": 4, "⑤": 5}

# 6. 정규표현식으로 (문항번호, 원형 정답, 배점) 추출
pattern = re.compile(r"(\d+)([①-⑤])(\d)")
matches = pattern.findall(raw)

# 7. DataFrame용 리스트 생성
data = []
for num_str, circled, score_str in matches:
    data.append({
        "문항번호": int(num_str),
        "정답": num_map[circled],
        "배점": int(score_str)
    })

# 8. DataFrame 생성 및 정렬
df = pd.DataFrame(data)
df = df.sort_values("문항번호").reset_index(drop=True)

# 9. CSV로 저장 (파일명은 원본 PDF와 동일, 확장자만 .csv)
base_name = os.path.splitext(os.path.basename(pdf_path))[0]
csv_path = os.path.join(os.path.dirname(pdf_path), f"{base_name}.csv")

df.to_csv(csv_path, index=False, encoding="utf-8-sig")
print(f"Saved CSV file: {csv_path}")