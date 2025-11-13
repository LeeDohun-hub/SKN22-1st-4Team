import pandas as pd
import numpy as np
import re
import os

# --- 설정 ---
# 원본 파일 이름
ORIGINAL_FILE = '한국교통안전공단_자동차 리콜대수 및 시정률_20221231.csv'

# 새로 생성될 엑셀 파일 이름
OUTPUT_FILE = '브랜드별_리콜_요약_데이터.xlsx'

# --- 1. 필터링 키워드 (승용차가 아닌 것들) ---
# process_data.py와 동일한 필터링 로직
MANUFACTURER_EXCLUDE_KEYWORDS = [
    '버스', '모터스', '이륜차', '오토바이', '스즈키', '할리데이비슨', '혼다코리아', 
    '대동공업', '엘에스엠트론', '트랙터', '농기계', 'KR모터스', '가와사키', '두카티',
    '브이스트롬', '인디언', '바이크', '모터사이클', '야마하', '다임러트럭', '만트럭',
    '볼보트럭', '스카니아', '특장', '중공업', '상용차', '선롱버스', '자일대우'
]
MODEL_NAME_EXCLUDE_KEYWORDS = [
    '버스', '트럭', '트랙터', '이륜차', '스쿠터', '오토바이', '굴삭기', '지게차',
    'LPGi', '카고', '덤프', '트레일러', '특수', '모터싸이클', '화물', 'CITY'
]

# --- 2. 정제(통합) 함수 ---
def clean_manufacturer_name(name):
    """제작자 이름 정제 (예: '현대자동차(주)' -> '현대')"""
    name_lower = str(name).lower() # 문자열로 변환
    if '현대' in name_lower: return '현대'
    if '기아' in name_lower: return '기아'
    if '한국지엠' in name_lower or '지엠코리아' in name_lower: return 'GM'
    if '르노코리아' in name_lower or '르노삼성' in name_lower: return '르노'
    if '쌍용' in name_lower: return '쌍용(KG모빌리티)'
    if '메르세데스' in name_lower or '벤츠' in name_lower: return '벤츠'
    if '비엠더블유' in name_lower or 'bmw' in name_lower: return 'BMW'
    if '폭스바겐' in name_lower: return '폭스바겐'
    if '아우디' in name_lower: return '아우디'
    if '포르쉐' in name_lower: return '포르쉐'
    name = re.sub(r'\(.*\)', '', str(name)).strip()
    name = name.replace('주식회사', '').replace('(유)', '').replace('(주)', '').strip()
    return name

def clean_model_name(name):
    """차명 정제 (예: '쏘나타(DN8)' -> '쏘나타')"""
    name = str(name)
    # 괄호 및 괄호 안 내용 제거 (정확한 집계를 위해)
    name = re.sub(r'\(.*\)', '', name).strip()
    # 기타 수식어 제거 (필요시)
    # name = name.split(' ')[0] 
    return ' '.join(name.split()) # 연속 공백 제거

# --- 3. 메인 로직 ---
def process_and_aggregate():
    """데이터를 필터링, 정제, '집계'하여 새 Excel 파일로 저장합니다."""
    
    print(f"'{ORIGINAL_FILE}' 파일을 읽는 중입니다...")
    
    # 1. CSV 읽기
    if not os.path.exists(ORIGINAL_FILE):
        print(f"[오류] 원본 파일('{ORIGINAL_FILE}')을 찾을 수 없습니다.")
        return
    try:
        df = pd.read_csv(ORIGINAL_FILE, encoding='cp949')
    except UnicodeDecodeError:
        df = pd.read_csv(ORIGINAL_FILE, encoding='utf-8')
    except Exception as e:
        print(f"파일을 읽는 중 오류 발생: {e}")
        return
            
    original_row_count = len(df)
    print(f"원본 데이터 {original_row_count}건 로드 완료.")

    # 2. [Goal 1] 필터링 (승용차)
    mask_mfg = df['제작자'].str.contains('|'.join(MANUFACTURER_EXCLUDE_KEYWORDS), case=False, na=False)
    mask_model = df['차명'].str.contains('|'.join(MODEL_NAME_EXCLUDE_KEYWORDS), case=False, na=False)
    filtered_df = df[~mask_mfg & ~mask_model].copy()
    print(f"승용차 데이터 {len(filtered_df)}건 필터링 완료.")

    # 3. 데이터 정제 (Grouping 준비)
    filtered_df['제작자'] = filtered_df['제작자'].apply(clean_manufacturer_name)
    filtered_df['차명'] = filtered_df['차명'].apply(clean_model_name)
    
    # 4. [Goal 2] '리콜연도' 컬럼 생성
    # '리콜개시일'을 날짜 타입으로 변환 (오류 무시)
    filtered_df['리콜개시일_dt'] = pd.to_datetime(filtered_df['리콜개시일'], errors='coerce')
    filtered_df['리콜연도'] = filtered_df['리콜개시일_dt'].dt.year
    # 연도 변환 실패한 데이터(NaT)는 집계에서 제외
    filtered_df = filtered_df.dropna(subset=['리콜연도'])
    filtered_df['리콜연도'] = filtered_df['리콜연도'].astype(int)
    print("'리콜연도' 컬럼 생성 완료.")

    # 5. [Goal 3, 4, 5] 데이터 집계 (Aggregation)
    
    # 집계 기준 컬럼들
    GROUP_BY_KEYS = ['제작자', '차명', '리콜사유', '리콜연도']
    
    # 집계 방법 정의
    AGG_RULES = {
        '리콜대수': 'sum',      # [Goal 4] 리콜대수 합산
        '시정대수': 'sum',      # [Goal 4] 시정대수 합산
        '생산기간(부터)': 'min',  # 병합된 항목 중 가장 빠른 생산시작일
        '생산기간(까지)': 'max',  # 병합된 항목 중 가장 늦은 생산종료일
        '리콜개시일': 'max'     # 병합된 항목 중 가장 최근 리콜개시일
    }
    
    print("데이터 집계(Grouping) 시작...")
    aggregated_df = filtered_df.groupby(GROUP_BY_KEYS).agg(AGG_RULES).reset_index()
    print("데이터 집계 완료.")

    # 6. [Goal 5] '시정율' 새로 계산 (합산된 평균)
    # (합산된 시정대수 / 합산된 리콜대수) * 100
    # 분모(리콜대수)가 0인 경우 오류 방지
    aggregated_df['시정율(퍼센트)'] = np.where(
        aggregated_df['리콜대수'] == 0, 
        0,  # 리콜대수가 0이면 시정율도 0
        (aggregated_df['시정대수'] / aggregated_df['리콜대수']) * 100
    )
    # 소수점 2자리까지 반올림
    aggregated_df['시정율(퍼센트)'] = aggregated_df['시정율(퍼센트)'].round(2)
    print("'시정율' 컬럼 새로 계산 완료 (합산 기준 평균).")

    # 7. [Goal 6] Excel 파일로 저장 (시트별 브랜드)
    print(f"'{OUTPUT_FILE}' 엑셀 파일 생성 시작...")
    
    # ExcelWriter 객체 생성
    try:
        with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
            # 정렬 기준 컬럼 (제작자, 차명, 리콜연도 최신순)
            sort_columns = ['제작자', '차명', '리콜연도']
            
            # 최종 데이터 정렬
            final_df = aggregated_df.sort_values(by=sort_columns, ascending=[True, True, False])

            # 브랜드 목록 추출
            unique_brands = final_df['제작자'].unique()
            
            # 각 브랜드를 별도 시트에 저장
            for brand in unique_brands:
                # 시트 이름에 사용 불가능한 문자 제거 (예: / \ * ? [ ])
                safe_sheet_name = re.sub(r'[\\/*?\[\]:]', '', brand)[:30] # 시트명 30자 제한
                
                print(f" -> '{safe_sheet_name}' 시트 저장 중...")
                brand_df = final_df[final_df['제작자'] == brand].copy()
                
                # 브랜드별 시트에서는 '제작자' 컬럼이 불필요하므로 제외 (선택 사항)
                # brand_df = brand_df.drop(columns=['제작자'])
                
                brand_df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
        
        print(f"\n[성공] '{OUTPUT_FILE}' 파일이 성공적으로 생성되었습니다.")
        print(f"({len(unique_brands)}개의 브랜드 시트가 생성됨)")
        
    except ImportError:
        print("\n[오류] 'openpyxl' 라이브러리가 필요합니다.")
        print("엑셀 파일 저장을 위해 터미널에서 'pip install openpyxl'를 실행해주세요.")
    except Exception as e:
        print(f"\n[오류] 엑셀 파일 저장 중 오류 발생: {e}")

# --- 4. 스크립트 실행 ---
if __name__ == "__main__":
    # Pandas, Numpy 설치 확인
    try:
        import pandas
        import numpy
    except ImportError:
        print("[알림] 'pandas'와 'numpy' 라이브러리가 필요합니다.")
        print("터미널에서 'pip install pandas numpy'를 실행해주세요.")
    else:
        process_and_aggregate()