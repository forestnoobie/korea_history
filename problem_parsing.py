# Standard library imports
import os
import ssl
import urllib.request
import json
# Third-party imports
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytesseract
from PIL import Image
from scipy.spatial.distance import cdist
import fitz  # PyMuPDF

from utils.parsing import pdf_to_images, draw_rect

# 1. Split pdf to pages
# 2. OCR each page
# 3. Parse the OCR result to get the problems
# 4. Save the problems to a csv file


exam_no = 74
load_path = "data/raw/history_exam/{}/{}_workbook.pdf".format(exam_no, exam_no)
proceesed_path = "data/processed/history_exam/{}/".format(exam_no)
tesseract_dir = "./utils/"

# Create output directories if they don't exist
os.makedirs(proceesed_path, exist_ok=True)
os.makedirs(os.path.join(proceesed_path, "split_pages"), exist_ok=True)
os.makedirs(os.path.join(proceesed_path, "box_outputs"), exist_ok=True)
os.makedirs(os.path.join(proceesed_path, "problem_image"), exist_ok=True)

# Convert PDF to images
images = pdf_to_images(load_path, output_dir=os.path.join(proceesed_path, "split_pages"))

fnames = os.listdir(os.path.join(proceesed_path, "split_pages"))
fnames.sort(key = lambda x: int(x.split('_')[3].split('.')[0]))

# Create tessdata directory in the current folder if it doesn't exist
tessdata_dir = os.path.join(os.path.dirname(__file__), "tessdata")
os.makedirs(tessdata_dir, exist_ok=True)

# Download Korean language data if not exists
kor_traineddata = os.path.join(tessdata_dir, "kor.traineddata")
if not os.path.exists(kor_traineddata):
    print("Downloading Korean language data...")
    # Disable SSL verification for the download
    ssl._create_default_https_context = ssl._create_unverified_context
    url = "https://github.com/tesseract-ocr/tessdata/raw/main/kor.traineddata"
    urllib.request.urlretrieve(url, kor_traineddata)
    print("Download complete!")

os.environ['TESSDATA_PREFIX'] = tessdata_dir

q_cnt = 1
workbook_info = []
for fname in fnames:
    print(f"Processing image: {fname}")
    ## Insert metadata
    workbook_info.append({
        "image_path": os.path.join(proceesed_path, "split_pages", fname),
        "page": fname,
        "artifact_type": "splited_page"
    })
    image = Image.open(os.path.join(proceesed_path, "split_pages", fname))
       # Perform OCR with Korean language support and get bounding boxes
    custom_config = r'--oem 3 --psm 6 -l kor'  # Use Korean language pack
    data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DATAFRAME)

    # Filter out empty text and low confidence results
    data = data[data.conf >= 70]  # Remove rows with confidence -1
    data = data.dropna(subset=['text'])  # Remove rows with empty text
    data = data[data['text'].str.strip() != '']  # Remove rows with only whitespace
    data = data[data['text'].str.contains(r'[\?\]]', regex=True)]  # text containing ? or ]

    # Plot the image with bounding boxes
    plt.figure(figsize=(15,15))
    plt.imshow(image)
    
    # # # Draw rectangles for each detected text area
    for index, row in data.iterrows():
        x, y = row['left'], row['top']
        w, h = row['width'], row['height']
        
        # Create a Rectangle patch
        rect = patches.Rectangle((x,y), w, h, linewidth=2, edgecolor='r', facecolor='none')
        
        # Add the rectangle to the plot
        plt.gca().add_patch(rect)
        
        # Add text annotation
        plt.text(x, y-5, row['text'] + "+ " + str(round(row['top'], 2)), color='red', fontsize=8)

    ## Classfiy questions
    total_w, total_h = image.size            
    q_data = data[data['text'].str.contains(r'^\?', regex=True)]  # text starting with ?

    ## sort by y (top) first, then by x (left)
    q_data = q_data.sort_values(by=['top', 'left'], ascending=[True, True])

    # 왼쪽 문제 찾기
    q_data['left_side'] = q_data['left'].apply(lambda x: True if x < total_w * 0.5  else False)
    q_data = q_data[((q_data.left_side == True) & (q_data.left > total_w * 0.3)) | ((q_data.left_side == False) & (q_data.left > total_w * 0.75))]
    
    # 문제 갯수로 추가 전처리    ## 문제 수 너무 작으면 "]" 문제 추가
    
    if len(q_data) < 4:
        candidate_data = data[data['text'].str.contains(r'^\]', regex=True)]  #  [
        candidate_data = candidate_data.sort_values(by=['top', 'left'], ascending=[True, True]).reset_index(drop=True)
        candidate_data['left_side'] = candidate_data['left'].apply(lambda x: True if x < total_w * 0.5 and x > total_w * 0.4 else False)
        candidate_data = candidate_data[(candidate_data.left_side == True) | ((candidate_data.left_side == False) & (candidate_data.left > total_w * 0.75)) ]
        # 1. Find the closest q_data according to top, left in candidate_data
        def find_closest_q(row):
            if len(q_data) == 0:
                return False
            # Calculate distances to all q_data points
            distances = []
            for _, q_row in q_data.iterrows():
                if row['left_side'] == q_row['left_side']:
                    dist = abs(row['top'] - q_row['top'])
                    distances.append(dist)
            # Return True if minimum distance is within threshold (e.g. 100 pixels)

            return min(distances) < 120
        candidate_data['close_to_q'] = candidate_data.apply(find_closest_q, axis=1)
        # 가까운 q_data가 없는 Candidate_data merge
        candidate_data = candidate_data[candidate_data['close_to_q'] == False]
        candidate_data.drop(columns=['close_to_q'], inplace=True)
        q_data = pd.concat([q_data, candidate_data])
        q_data = q_data.sort_values(by=['top', 'left'], ascending=[True, True])

    left_q_data = q_data[q_data['left_side'] == True]
    # ? Strong Left condition : total_w * 0.25 < x
    left_q_data = left_q_data[left_q_data['left'] > total_w * 0.25]
    left_q_data = left_q_data.sort_values(by='top', ascending=True).reset_index(drop=True)


    # ? Strong Right condition : total_w * 0.75 > x
    right_q_data = q_data[q_data['left_side'] == False]
    right_q_data = right_q_data[right_q_data['left'] > total_w * 0.75]
    right_q_data = right_q_data.sort_values(by='top', ascending=True).reset_index(drop=True)  

    q_wh = (left_q_data.iloc[0]['left'], left_q_data.iloc[0]['top'])
    left_margin = 170
    for idx, left_q in left_q_data.iterrows():
        if idx == 0: 
            continue
        q_prev = q_wh
        q_wh = (left_q['left'], left_q['top'])
        (x,y,w,h) = (left_margin, q_prev[1], total_w/2 - left_margin, q_wh[1] - q_prev[1])
        draw_rect(x,y,w,h, f"No.{q_cnt}", q_cnt)
        cropped_image = image.crop((x,y,x+w,y+h))
        cropped_image_path = f'{proceesed_path}/problem_image/{fname.split(".")[0]}_q{q_cnt}.png'
        cropped_image.save(cropped_image_path)
        ## Insert metadata
        workbook_info.append({
            "image_path": cropped_image_path,
            "page": fname,
            "question_no": q_cnt,
            "bounding_box": [int(x), int(y), int(w), int(h)],
            "artifact_type": "question",
            "left": int(x),
            "top": int(y),
            "width": int(w),
            "height": int(h)
        })
        q_cnt += 1

    (x,y,w,h) = (left_margin, q_wh[1], total_w/2 - left_margin, total_h - q_wh[1])
    draw_rect(left_margin, q_wh[1], total_w/2 - left_margin, total_h - q_wh[1], f"No.{q_cnt}", q_cnt)
    cropped_image = image.crop((x,y,x+w,y+h))
    cropped_image_path = f'{proceesed_path}/problem_image/{fname.split(".")[0]}_q{q_cnt}.png'
    cropped_image.save(cropped_image_path)    
    ## Insert metadata  
    workbook_info.append({
        "image_path": cropped_image_path,
        "page": fname,
        "question_no": q_cnt,
        "bounding_box": [int(x), int(y), int(w), int(h)],
        "artifact_type": "question",
        "left": int(x),
        "top": int(y),
        "width": int(w),
        "height": int(h)
    })
    q_cnt += 1

    right_margin = 20

    q_wh = (right_q_data.iloc[0]['left'], right_q_data.iloc[0]['top'])

    for idx, right_q in right_q_data.iterrows():
        if idx == 0: 
            continue
        q_prev = q_wh
        q_wh = (right_q['left'], right_q['top'])
        x,y,w,h = (total_w/2 + right_margin, q_prev[1], total_w/2 - 170, q_wh[1] - q_prev[1])
        draw_rect(x,y,w,h, f"No.{q_cnt}", q_cnt)
        # Crop image and save
        cropped_image = image.crop((x,y,x+w,y+h))
        cropped_image_path = f'{proceesed_path}/problem_image/{fname.split(".")[0]}_q{q_cnt}.png'
        cropped_image.save(cropped_image_path)
        ## Insert metadata
        workbook_info.append({
            "image_path": cropped_image_path,   
            "page": fname,
            "question_no": q_cnt,
            "bounding_box": [int(x), int(y), int(w), int(h)],
            "artifact_type": "question",
            "left": int(x),
            "top": int(y),
            "width": int(w),
            "height": int(h)
        })
        q_cnt += 1
    x,y,w,h = (total_w/2 + right_margin, q_wh[1], total_w/2 - 170, total_h - q_wh[1])
    draw_rect(x,y,w,h, f"No.{q_cnt}", q_cnt)
    cropped_image = image.crop((x,y,x+w,y+h))
    cropped_image_path = f'{proceesed_path}/problem_image/{fname.split(".")[0]}_q{q_cnt}.png'
    cropped_image.save(cropped_image_path)
    ## Insert metadata
    workbook_info.append({
        "image_path": cropped_image_path,
        "page": fname,
        "question_no": q_cnt,
        "bounding_box": [int(x), int(y), int(w), int(h)],
        "artifact_type": "question",
        "left": int(x),
        "top": int(y),
        "width": int(w),
        "height": int(h)
    })
    q_cnt += 1

    plt.axis('off')
    plt.savefig(f'{proceesed_path}/box_outputs/{fname.split(".")[0]}_boxes.png', bbox_inches='tight', dpi=300)
    plt.close()
        
    # Method 2: Save as text file (one JSON object per line)
    with open(f'{proceesed_path}/{exam_no}_bbox_info.txt', 'w', encoding='utf-8') as f:
        for item in workbook_info:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


# Method 4: Save as CSV file
workbook_info_df = pd.DataFrame(workbook_info)
workbook_info_df.to_csv(f'{proceesed_path}/{exam_no}_bbox_info.csv', index=False, encoding='utf-8')
