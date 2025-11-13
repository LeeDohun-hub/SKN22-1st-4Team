import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

# 페이지 설정
st.set_page_config(
    page_title="중고차 리콜 사유 분석",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# [데이터 정의]
# -------------------------------------------------------------------

# 제조사 데이터
BRANDS = [
    {'brand_id': 1, 'brand_name': '현대'},
    {'brand_id': 2, 'brand_name': '기아'},
    {'brand_id': 3, 'brand_name': 'GM'},
    {'brand_id': 4, 'brand_name': '르노'},
    {'brand_id': 5, 'brand_name': '벤츠'},
    {'brand_id': 6, 'brand_name': 'BMW'},
    {'brand_id': 7, 'brand_name': '볼보'},
    {'brand_id': 8, 'brand_name': '테슬라'},
    {'brand_id': 9, 'brand_name': '혼다'},
]

# 모델 데이터
MODELS = {
    1: [  # 현대
        {'model_id': 101, 'model_name': '쏘나타 (DN8)'},
        {'model_id': 102, 'model_name': '아반떼 (CN7)'},
        {'model_id': 103, 'model_name': '그랜저 (IG)'},
        {'model_id': 104, 'model_name': '베라크루즈'},
    ],
    2: [  # 기아
        {'model_id': 201, 'model_name': 'K5 (DL3)'},
        {'model_id': 202, 'model_name': 'K8 (GL3)'},
        {'model_id': 203, 'model_name': '스포티지 (NQ5)'},
        {'model_id': 204, 'model_name': 'K7'},
    ],
    6: [  # BMW
        {'model_id': 601, 'model_name': '520d'},
        {'model_id': 602, 'model_name': '530i'},
        {'model_id': 603, 'model_name': 'X5 351'},
    ],
    7: [  # 볼보
        {'model_id': 701, 'model_name': 'S90'},
        {'model_id': 702, 'model_name': 'XC60'},
    ],
    8: [  # 테슬라
        {'model_id': 801, 'model_name': 'Model 3'},
        {'model_id': 802, 'model_name': 'Model S'},
    ],
    9: [  # 혼다
        {'model_id': 901, 'model_name': '아코드'},
        {'model_id': 902, 'model_name': 'CR-V'},
    ],
}

# 리콜 사유 카테고리
RECALL_REASONS = ['엔진', '전자장치', '제동', '조향', '안전장치', '소프트웨어', '배터리', '화재', '누유']

# 리콜 데이터
RECALL_DATA = [
    # 현대 쏘나타
    {
        'recall_id': 'R2023-001',
        'brand_name': '현대',
        'model_name': '쏘나타 (DN8)',
        'model_id': 101,
        'recall_date': '2023-01-05',
        'reason': '엔진 관련 부품(커넥팅 로드)의 결함으로 주행 중 시동이 꺼질 가능성',
        'reason_category': '엔진',
        'keywords': ['엔진', '시동'],
        'correction_rate': 30.5,
        'status': '조치중',
        'production_start': '2021-01',
        'production_end': '2022-12',
        'recall_code': 'R2023-001',
        'action_method': '무상점검 및 부품 교체',
        'contact': '1588-2000',
        'target_count': 12500,
        'corrected_count': 3812,
    },
    {
        'recall_id': 'R2022-045',
        'brand_name': '현대',
        'model_name': '쏘나타 (DN8)',
        'model_id': 101,
        'recall_date': '2022-06-15',
        'reason': '브레이크 잠김 방지(ABS) 시스템의 소프트웨어 오류로 제동 거리가 길어짐',
        'reason_category': '제동',
        'keywords': ['브레이크', '소프트웨어'],
        'correction_rate': 95.8,
        'status': '완료',
        'production_start': '2020-06',
        'production_end': '2022-05',
        'recall_code': 'R2022-045',
        'action_method': '소프트웨어 업데이트',
        'contact': '1588-2000',
        'target_count': 8500,
        'corrected_count': 8143,
    },
    {
        'recall_id': 'R2021-089',
        'brand_name': '현대',
        'model_name': '쏘나타 (DN8)',
        'model_id': 101,
        'recall_date': '2021-11-10',
        'reason': '에어백 제어 장치(ACU) 결함으로 충돌 시 에어백이 전개되지 않을 위험',
        'reason_category': '안전장치',
        'keywords': ['에어백'],
        'correction_rate': 45.2,
        'status': '진행중',
        'production_start': '2019-11',
        'production_end': '2021-10',
        'recall_code': 'R2021-089',
        'action_method': 'ACU 부품 교체',
        'contact': '1588-2000',
        'target_count': 10200,
        'corrected_count': 4610,
    },
    # 기아 K5
    {
        'recall_id': 'R2023-078',
        'brand_name': '기아',
        'model_name': 'K5 (DL3)',
        'model_id': 201,
        'recall_date': '2023-05-20',
        'reason': '연료 펌프 내부 부품 마모로 인한 연료 공급 불량 및 시동 꺼짐 가능성',
        'reason_category': '엔진',
        'keywords': ['엔진', '누유', '시동'],
        'correction_rate': 75.5,
        'status': '조치중',
        'production_start': '2021-05',
        'production_end': '2023-04',
        'recall_code': 'R2023-078',
        'action_method': '연료 펌프 교체',
        'contact': '1588-5000',
        'target_count': 15200,
        'corrected_count': 11476,
    },
    {
        'recall_id': 'R2022-112',
        'brand_name': '기아',
        'model_name': 'K5 (DL3)',
        'model_id': 201,
        'recall_date': '2022-08-10',
        'reason': '전자식 변속 제어장치(SCU) 소프트웨어 오류로 주차 시 차량 밀림 현상',
        'reason_category': '전자장치',
        'keywords': ['소프트웨어'],
        'correction_rate': 98.0,
        'status': '완료',
        'production_start': '2020-08',
        'production_end': '2022-07',
        'recall_code': 'R2022-112',
        'action_method': '소프트웨어 업데이트',
        'contact': '1588-5000',
        'target_count': 9800,
        'corrected_count': 9604,
    },
    {
        'recall_id': 'R2021-056',
        'brand_name': '기아',
        'model_name': 'K5 (DL3)',
        'model_id': 201,
        'recall_date': '2021-05-03',
        'reason': '연료 누유 가능성',
        'reason_category': '엔진',
        'keywords': ['누유'],
        'correction_rate': 85.0,
        'status': '완료',
        'production_start': '2019-05',
        'production_end': '2021-04',
        'recall_code': 'R2021-056',
        'action_method': '연료 라인 점검 및 교체',
        'contact': '1588-5000',
        'target_count': 11200,
        'corrected_count': 9520,
    },
    # 현대 그랜저
    {
        'recall_id': 'R2022-023',
        'brand_name': '현대',
        'model_name': '그랜저 (IG)',
        'model_id': 103,
        'recall_date': '2022-01-01',
        'reason': '배터리 관리 시스템(BMS) 오류로 화재 발생 가능성',
        'reason_category': '전자장치',
        'keywords': ['배터리', '화재'],
        'correction_rate': 100.0,
        'status': '완료',
        'production_start': '2020-01',
        'production_end': '2021-12',
        'recall_code': 'R2022-023',
        'action_method': 'BMS 소프트웨어 업데이트 및 배터리 점검',
        'contact': '1588-2000',
        'target_count': 6800,
        'corrected_count': 6800,
    },
    # 기아 K7
    {
        'recall_id': 'R2024-012',
        'brand_name': '기아',
        'model_name': 'K7',
        'model_id': 204,
        'recall_date': '2024-03-15',
        'reason': '제동장치 결함(ABS 내부 누유)',
        'reason_category': '제동',
        'keywords': ['제동', '누유'],
        'correction_rate': 65.3,
        'status': '조치중',
        'production_start': '2022-03',
        'production_end': '2024-02',
        'recall_code': 'R2024-012',
        'action_method': 'ABS 모듈 교체',
        'contact': '1588-5000',
        'target_count': 9200,
        'corrected_count': 6008,
    },
    {
        'recall_id': 'R2023-067',
        'brand_name': '기아',
        'model_name': 'K7',
        'model_id': 204,
        'recall_date': '2023-08-20',
        'reason': '전자제어 유압장치(HECU) 화재 가능성',
        'reason_category': '전자장치',
        'keywords': ['전자장치', '화재'],
        'correction_rate': 88.5,
        'status': '완료',
        'production_start': '2021-08',
        'production_end': '2023-07',
        'recall_code': 'R2023-067',
        'action_method': 'HECU 부품 교체',
        'contact': '1588-5000',
        'target_count': 7500,
        'corrected_count': 6638,
    },
    # BMW 520d
    {
        'recall_id': 'R2024-034',
        'brand_name': 'BMW',
        'model_name': '520d',
        'model_id': 601,
        'recall_date': '2024-02-10',
        'reason': '연료펌프 내구성 불량',
        'reason_category': '엔진',
        'keywords': ['엔진', '누유'],
        'correction_rate': 42.1,
        'status': '진행중',
        'production_start': '2022-02',
        'production_end': '2024-01',
        'recall_code': 'R2024-034',
        'action_method': '연료펌프 교체',
        'contact': '1588-5252',
        'target_count': 11200,
        'corrected_count': 4715,
    },
    # 볼보 S90
    {
        'recall_id': 'R2023-091',
        'brand_name': '볼보',
        'model_name': 'S90',
        'model_id': 701,
        'recall_date': '2023-11-05',
        'reason': '조향장치 전자제어 시스템 오류',
        'reason_category': '조향',
        'keywords': ['조향', '전자장치'],
        'correction_rate': 92.3,
        'status': '완료',
        'production_start': '2021-11',
        'production_end': '2023-10',
        'recall_code': 'R2023-091',
        'action_method': '소프트웨어 업데이트',
        'contact': '1588-0000',
        'target_count': 5800,
        'corrected_count': 5353,
    },
    # 테슬라 Model 3
    {
        'recall_id': 'R2024-056',
        'brand_name': '테슬라',
        'model_name': 'Model 3',
        'model_id': 801,
        'recall_date': '2024-01-20',
        'reason': '배터리 셀 결함으로 인한 화재 위험',
        'reason_category': '배터리',
        'keywords': ['배터리', '화재'],
        'correction_rate': 78.9,
        'status': '조치중',
        'production_start': '2022-01',
        'production_end': '2024-01',
        'recall_code': 'R2024-056',
        'action_method': '배터리 모듈 교체',
        'contact': '1588-0001',
        'target_count': 15200,
        'corrected_count': 11993,
    },
]

# 데이터프레임으로 변환
df_recalls = pd.DataFrame(RECALL_DATA)


# -------------------------------------------------------------------
# [유틸리티 함수]
# -------------------------------------------------------------------

@st.cache_data
def get_filtered_recalls(
    brand_filter: Optional[str] = None,
    model_filter: Optional[str] = None,
    year_filter: Optional[List[int]] = None,
    reason_filter: Optional[List[str]] = None,
    search_query: Optional[str] = None
) -> pd.DataFrame:
    """필터 조건에 맞는 리콜 데이터 반환"""
    filtered = df_recalls.copy()
    
    # 제조사 필터
    if brand_filter and brand_filter != '전체':
        filtered = filtered[filtered['brand_name'] == brand_filter]
    
    # 차종 필터
    if model_filter and model_filter != '전체':
        filtered = filtered[filtered['model_name'] == model_filter]
    
    # 연도 필터
    if year_filter:
        filtered['recall_year'] = pd.to_datetime(filtered['recall_date']).dt.year
        filtered = filtered[filtered['recall_year'].isin(year_filter)]
    
    # 리콜 사유 필터
    if reason_filter:
        filtered = filtered[filtered['reason_category'].isin(reason_filter)]
    
    # 검색어 필터
    if search_query:
        mask = (
            filtered['brand_name'].str.contains(search_query, na=False) |
            filtered['model_name'].str.contains(search_query, na=False) |
            filtered['reason'].str.contains(search_query, na=False)
        )
        filtered = filtered[mask]
    
    return filtered


def get_summary_stats(df: pd.DataFrame) -> Dict:
    """요약 통계 계산"""
    if len(df) == 0:
        return {
            'total_recalls': 0,
            'by_reason': {},
            'by_status': {},
            'avg_correction_rate': 0,
            'low_correction_count': 0,
        }
    
    by_reason = df['reason_category'].value_counts().to_dict()
    by_status = df['status'].value_counts().to_dict()
    avg_correction_rate = df['correction_rate'].mean()
    low_correction_count = len(df[df['correction_rate'] < 50])
    
    return {
        'total_recalls': len(df),
        'by_reason': by_reason,
        'by_status': by_status,
        'avg_correction_rate': avg_correction_rate,
        'low_correction_count': low_correction_count,
    }


# -------------------------------------------------------------------
# [메인 UI]
# -------------------------------------------------------------------

def main():
    # 헤더
    st.markdown("""
    <div style="background-color: #1E3A8A; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; color: white;">
            <h1 style="margin: 0; font-size: 1.5rem;">4조</h1>
            <p style="margin: 0; font-size: 0.9rem;">SK NETWORKS - 최민호, 장완식, 문승준, 박준성, 이도훈</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.title("🚗 중고차 리콜 사유 분석")
    st.markdown("---")
    
    # -------------------------------------------------------------------
    # [1. 상단 요약바 영역]
    # -------------------------------------------------------------------
    st.header("📊 리콜 현황 요약 및 필터")
    
    # 필터 컬럼
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    
    with col1:
        # 검색창
        search_query = st.text_input("🔍 검색 (차명/제조사)", placeholder="차량명 또는 제조사 검색")
    
    with col2:
        # 제조사 필터
        brand_options = ['전체'] + [b['brand_name'] for b in BRANDS]
        selected_brand = st.selectbox("제조사", brand_options)
    
    with col3:
        # 차종 필터
        model_options = ['전체']
        if selected_brand and selected_brand != '전체':
            brand_id = next((b['brand_id'] for b in BRANDS if b['brand_name'] == selected_brand), None)
            if brand_id and brand_id in MODELS:
                model_options.extend([m['model_name'] for m in MODELS[brand_id]])
        selected_model = st.selectbox("차종", model_options)
    
    with col4:
        # 연도 필터
        current_year = datetime.now().year
        year_options = list(range(2020, current_year + 2))
        selected_years = st.multiselect("리콜 연도", year_options, default=[current_year, current_year - 1])
    
    # 리콜 사유 필터
    st.markdown("### 리콜 사유 필터")
    reason_cols = st.columns(5)
    selected_reasons = []
    for i, reason in enumerate(RECALL_REASONS[:5]):
        with reason_cols[i]:
            if st.checkbox(reason, key=f"reason_{i}"):
                selected_reasons.append(reason)
    
    reason_cols2 = st.columns(4)
    for i, reason in enumerate(RECALL_REASONS[5:]):
        with reason_cols2[i]:
            if st.checkbox(reason, key=f"reason_{i+5}"):
                selected_reasons.append(reason)
    
    # 필터 적용
    filtered_df = get_filtered_recalls(
        brand_filter=selected_brand if selected_brand != '전체' else None,
        model_filter=selected_model if selected_model != '전체' else None,
        year_filter=selected_years if selected_years else None,
        reason_filter=selected_reasons if selected_reasons else None,
        search_query=search_query if search_query else None
    )
    
    # 요약 통계
    stats = get_summary_stats(filtered_df)
    
    st.markdown("---")
    st.markdown("### 📈 요약 통계")
    
    stat_cols = st.columns(5)
    with stat_cols[0]:
        st.metric("총 리콜 건수", f"{stats['total_recalls']}건")
    with stat_cols[1]:
        st.metric("평균 시정률", f"{stats['avg_correction_rate']:.1f}%")
    with stat_cols[2]:
        st.metric("시정률 50%↓", f"{stats['low_correction_count']}건", 
                 delta=f"{stats['low_correction_count']}건 주의" if stats['low_correction_count'] > 0 else None)
    
    # 사유별 통계
    if stats['by_reason']:
        with stat_cols[3]:
            top_reason = max(stats['by_reason'], key=stats['by_reason'].get)
            st.metric("최다 사유", top_reason, delta=f"{stats['by_reason'][top_reason]}건")
    
    # 상태별 통계
    if stats['by_status']:
        with stat_cols[4]:
            status_counts = sum(stats['by_status'].values())
            st.metric("진행 상태", f"총 {status_counts}건")
    
    st.markdown("---")
    
    # -------------------------------------------------------------------
    # [2. 중단 영역: 리콜 목록 (카드/테이블)]
    # -------------------------------------------------------------------
    st.header(f"📋 리콜 목록 (총 {len(filtered_df)}건)")
    
    # 표시 방식 선택
    view_mode = st.radio("표시 방식", ["카드형", "표형"], horizontal=True)
    
    if len(filtered_df) == 0:
        st.warning("조건에 맞는 리콜 내역이 없습니다.")
    else:
        if view_mode == "카드형":
            # 카드형 표시
            display_cards(filtered_df)
        else:
            # 표형 표시
            display_table(filtered_df)
    
    # -------------------------------------------------------------------
    # [3. 하단 상세 정보 영역]
    # -------------------------------------------------------------------
    st.markdown("---")
    st.header("📄 상세 리콜 정보")
    
    # 상세 정보를 보여줄 리콜 선택
    if len(filtered_df) > 0:
        recall_options = [
            f"{row['brand_name']} {row['model_name']} - {row['reason'][:30]}... ({row['recall_date']})"
            for _, row in filtered_df.iterrows()
        ]
        selected_recall_idx = st.selectbox("리콜 선택", range(len(recall_options)), format_func=lambda x: recall_options[x])
        
        if selected_recall_idx is not None:
            selected_recall = filtered_df.iloc[selected_recall_idx]
            display_detail(selected_recall)


def display_cards(df: pd.DataFrame):
    """카드형으로 리콜 목록 표시"""
    for idx, row in df.iterrows():
        # 상태에 따른 색상
        status_colors = {
            '완료': '🟢',
            '조치중': '🟡',
            '진행중': '🔴',
        }
        status_icon = status_colors.get(row['status'], '⚪')
        
        # 시정률에 따른 색상
        if row['correction_rate'] < 50:
            rate_color = "🔴"
            rate_style = "color: red; font-weight: bold;"
        elif row['correction_rate'] < 80:
            rate_color = "🟡"
            rate_style = "color: orange; font-weight: bold;"
        else:
            rate_color = "🟢"
            rate_style = "color: green; font-weight: bold;"
        
        with st.container():
            st.markdown(f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; background-color: #f9fafb;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h3 style="margin: 0; color: #1E3A8A;">{row['brand_name']} {row['model_name']}</h3>
                        <p style="margin: 0.5rem 0; color: #666;">{row['reason']}</p>
                    </div>
                    <div style="text-align: right;">
                        <p style="margin: 0; font-size: 0.9rem;">{status_icon} {row['status']}</p>
                        <p style="margin: 0; font-size: 0.9rem; {rate_style}">{rate_color} 시정률: {row['correction_rate']}%</p>
                    </div>
                </div>
                <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid #eee;">
                    <span style="font-size: 0.85rem; color: #888;">리콜 개시일: {row['recall_date']}</span>
                    <span style="font-size: 0.85rem; color: #888; margin-left: 1rem;">리콜 코드: {row['recall_code']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


def display_table(df: pd.DataFrame):
    """표형으로 리콜 목록 표시"""
    # 표시용 데이터프레임 생성
    display_df = df[['brand_name', 'model_name', 'reason', 'reason_category', 'status', 'recall_date', 'correction_rate']].copy()
    display_df.columns = ['제조사', '모델명', '리콜사유', '리콜유형', '조치상태', '날짜', '시정률']
    
    # 시정률에 따른 스타일링
    def style_rate(val):
        if val < 50:
            return 'background-color: #fee2e2; color: #991b1b; font-weight: bold;'
        elif val < 80:
            return 'background-color: #fef3c7; color: #92400e; font-weight: bold;'
        else:
            return 'background-color: #d1fae5; color: #065f46;'
    
    styled_df = display_df.style.applymap(style_rate, subset=['시정률'])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)


def display_detail(recall: pd.Series):
    """상세 리콜 정보 표시"""
    st.markdown(f"""
    <div style="border: 2px solid #1E3A8A; border-radius: 8px; padding: 1.5rem; background-color: #f0f9ff;">
        <h2 style="color: #1E3A8A; margin-top: 0;">{recall['brand_name']} {recall['model_name']}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    detail_cols = st.columns(2)
    
    with detail_cols[0]:
        st.markdown("### 기본 정보")
        st.write(f"**리콜 번호:** {recall['recall_code']}")
        st.write(f"**발표일자:** {recall['recall_date']}")
        st.write(f"**제조사:** {recall['brand_name']}")
        st.write(f"**모델명:** {recall['model_name']}")
        st.write(f"**리콜 유형:** {recall['reason_category']}")
        st.write(f"**조치 상태:** {recall['status']}")
    
    with detail_cols[1]:
        st.markdown("### 상세 사유")
        st.write(recall['reason'])
        st.markdown("### 키워드")
        keywords_html = " ".join([f"<span style='background-color: #dbeafe; padding: 0.25rem 0.5rem; border-radius: 0.25rem; margin-right: 0.5rem;'>#{k}</span>" for k in recall['keywords']])
        st.markdown(keywords_html, unsafe_allow_html=True)
    
    st.markdown("### 대상 차량 정보")
    info_cols = st.columns(3)
    with info_cols[0]:
        st.write(f"**생산 기간:** {recall['production_start']} ~ {recall['production_end']}")
    with info_cols[1]:
        st.write(f"**대상 차량 수:** {recall['target_count']:,}대")
    with info_cols[2]:
        st.write(f"**시정 완료 수:** {recall['corrected_count']:,}대")
    
    st.markdown("### 조치 방법")
    st.info(f"**{recall['action_method']}**")
    
    st.markdown("### 시정률")
    progress_value = recall['correction_rate'] / 100
    st.progress(progress_value)
    st.write(f"**{recall['correction_rate']}%** ({recall['corrected_count']:,}대 / {recall['target_count']:,}대)")
    
    st.markdown("### 연락처")
    st.write(f"**리콜 센터:** {recall['contact']}")
    st.write(f"제조사 고객센터로 문의하시면 무상 점검 및 수리를 받으실 수 있습니다.")


if __name__ == "__main__":
    main()

