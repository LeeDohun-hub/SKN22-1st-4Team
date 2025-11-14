import streamlit as st
import pandas as pd
import altair as alt
from wordcloud import WordCloud 
import matplotlib.pyplot as plt 
import os 
import datetime 

from backend.search_queries import (
    get_all_brands, 
    get_models_by_brand, 
    get_recall_comparison, 
    get_model_profile_data
)
from backend.stats_queries import get_summary_stats, get_brand_rankings

# --- 헤더 함수 임포트 ---
try:
    from Home import display_custom_header 
except ImportError:
    def display_custom_header():
        pass
# --------------------------------

# --- [0] 페이지 기본 설정 ---
st.set_page_config(
    page_title="레몬 스캐너 - 분석 리포트", 
    page_icon="📊", 
    layout="wide"
)

display_custom_header()

# --- [1] 제목 ---
st.title("📊 분석 리포트") 
st.info("차량 비교, 브랜드 랭킹, 개별 모델 분석 기능을 제공합니다.")
st.markdown("---")


# --- [2] 탭(Tabs) 생성 ---
tab_compare, tab_brand, tab_model = st.tabs([
    "📊 차량 비교", 
    "🏆 브랜드 리포트", 
    "🔍 모델 프로필"
])


# ==============================================================================
# --- [ 탭 1: 차량 비교 ] ---
# ==============================================================================
with tab_compare:
    st.header("차량 비교")
    st.info("비교하고 싶은 두 차량을 선택하고 '비교하기' 버튼을 눌러주세요.")

    # --- 차량 선택 UI ---
    try:
        brand_list_for_compare = ["전체"] + get_all_brands()
    except Exception as e:
        st.error(f"브랜드 목록 로딩 실패: {e}")
        brand_list_for_compare = ["전체"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("차량 1 (비교 대상)")
        brand1 = st.selectbox("브랜드 선택", brand_list_for_compare, key="brand1", index=0)
        if brand1 != "전체":
            model_list1 = ["전체"] + get_models_by_brand(brand1)
        else:
            model_list1 = ["전체"]
        model1 = st.selectbox("차종 선택", model_list1, key="model1", index=0)
    with col2:
        st.subheader("차량 2 (비교 대상)")
        brand2 = st.selectbox("브랜드 선택", brand_list_for_compare, key="brand2", index=0)
        if brand2 != "전체":
            model_list2 = ["전체"] + get_models_by_brand(brand2)
        else:
            model_list2 = ["전체"]
        model2 = st.selectbox("차종 선택", model_list2, key="model2", index=0)

    st.markdown("---")

    # --- 비교 결과 표시 ---
    if st.button("비교하기", use_container_width=True, key="compare_button"):
        if (brand1 == "전체" or model1 == "전체") or (brand2 == "전체" or model2 == "전체"):
            st.error("오류: 2대의 차량(브랜드와 차종)을 모두 정확히 선택해야 합니다.")
        else:
            st.subheader(f"📊 {brand1} {model1}  vs  {brand2} {model2}  비교 결과")
            
            with st.spinner("두 차량의 리콜 데이터를 분석 중입니다..."):
                stats1, keywords_df1 = get_recall_comparison(brand1, model1)
                stats2, keywords_df2 = get_recall_comparison(brand2, model2)

            res_col1, res_col2 = st.columns(2)
            
            with res_col1:
                st.markdown(f"#### 🚗 **{brand1} {model1}**")
                if stats1 and stats1['total_recalls'] > 0:
                    metric_cols1 = st.columns(2)
                    metric_cols1[0].metric("총 리콜 건수", f"{stats1['total_recalls']} 건")
                    metric_cols1[1].metric("평균 시정률", f"{stats1['avg_correction_rate']} %")
                    st.markdown("**주요 리콜 키워드 (Top 10)**")
                    if not keywords_df1.empty:
                        chart1 = alt.Chart(keywords_df1).mark_bar().encode(
                            x=alt.X('keyword_text', title='리콜 키워드', sort=None, axis=alt.Axis(labelAngle=-45)),
                            y=alt.Y('keyword_count', title='키워드 빈도'),
                            tooltip=[
                                alt.Tooltip('keyword_text', title='키워드'),
                                alt.Tooltip('keyword_count', title='빈도수'),
                                alt.Tooltip('keyword_desc', title='설명')
                            ]
                        ).properties(height=350).interactive()
                        st.altair_chart(chart1, use_container_width=True)
                    else:
                        st.info("분석된 키워드 데이터가 없습니다.")
                else:
                    st.warning("해당 차종의 리콜 데이터가 없습니다.")
            
            with res_col2:
                st.markdown(f"#### 🚙 **{brand2} {model2}**")
                if stats2 and stats2['total_recalls'] > 0:
                    metric_cols2 = st.columns(2)
                    metric_cols2[0].metric("총 리콜 건수", f"{stats2['total_recalls']} 건")
                    metric_cols2[1].metric("평균 시정률", f"{stats2['avg_correction_rate']} %")
                    st.markdown("**주요 리콜 키워드 (Top 10)**")
                    if not keywords_df2.empty:
                        chart2 = alt.Chart(keywords_df2).mark_bar().encode(
                            x=alt.X('keyword_text', title='리콜 키워드', sort=None, axis=alt.Axis(labelAngle=-45)),
                            y=alt.Y('keyword_count', title='키워드 빈도'),
                            tooltip=[
                                alt.Tooltip('keyword_text', title='키워드'),
                                alt.Tooltip('keyword_count', title='빈도수'),
                                alt.Tooltip('keyword_desc', title='설명')
                            ]
                        ).properties(height=350).interactive()
                        st.altair_chart(chart2, use_container_width=True)
                    else:
                        st.info("분석된 키워드 데이터가 없습니다.")
                else:
                    st.warning("해당 차종의 리콜 데이터가 없습니다.")


# ==============================================================================
# --- [ 탭 2: 브랜드 리포트 ] ---
# ==============================================================================
with tab_brand:
    st.header("브랜드 리포트")
    st.info("DB에 저장된 전체 브랜드를 대상으로 '리콜 건수'와 '평균 시정률' 순위를 분석합니다.")
    
    # --- 데이터 로드 ---
    try:
        with st.spinner("브랜드 랭킹 데이터를 분석 중입니다..."):
            df_recall_rank, df_rate_rank = get_brand_rankings()
    except Exception as e:
        st.error(f"브랜드 리포트 데이터 로딩 중 오류 발생: {e}")
        df_recall_rank = pd.DataFrame()
        df_rate_rank = pd.DataFrame()

    # --- 리포트 표시 (2단 컬럼) ---
    col_rank1, col_rank2 = st.columns(2)
    with col_rank1:
        st.subheader("🍋 리콜 건수 순위 (많은 순)")
        st.markdown("리콜이 **많이** 발생한 브랜드 순위입니다. (DB 내 전체 기간)")
        if not df_recall_rank.empty:
            chart_recall = alt.Chart(df_recall_rank.head(15)).mark_bar().encode(
                x=alt.X('총 리콜 건수', title='총 리콜 건수'),
                y=alt.Y('브랜드', title='브랜드', sort='-x'),
                tooltip=['브랜드', '총 리콜 건수']
            ).properties(title='리콜 건수 상위 15개 브랜드', height=500).interactive()
            st.altair_chart(chart_recall, use_container_width=True)
            with st.expander("전체 브랜드 리콜 건수 순위 보기 (표)"):
                st.dataframe(df_recall_rank, use_container_width=True)
        else:
            st.warning("리콜 건수 데이터를 찾을 수 없습니다.")
    with col_rank2:
        st.subheader("🛠️ 평균 시정률 순위 (높은 순)")
        st.markdown("리콜 발생 시 **시정 조치**가 잘 이루어진 브랜드 순위입니다. (리콜 5건 이상 대상)")
        if not df_rate_rank.empty:
            chart_rate = alt.Chart(df_rate_rank.head(15)).mark_bar(color="green").encode(
                x=alt.X('평균 시정률 (%)', title='평균 시정률 (%)', scale=alt.Scale(domain=[0, 100])),
                y=alt.Y('브랜드', title='브랜드', sort='-x'),
                tooltip=['브랜드', '평균 시정률 (%)', '리콜 건수']
            ).properties(title='평균 시정률 상위 15개 브랜드', height=500).interactive()
            st.altair_chart(chart_rate, use_container_width=True)
            with st.expander("전체 브랜드 시정률 순위 보기 (표)"):
                st.dataframe(df_rate_rank, use_container_width=True)
        else:
            st.warning("시정률 데이터를 찾을 수 없습니다.")


# ==============================================================================
# --- [ 탭 3: 모델 프로필 ] ---
# ==============================================================================
with tab_model:
    st.header("모델 상세 프로필")
    st.info("관심 있는 차량의 종합 리콜 리포트를 확인해 보세요.")
    
    # --- [★ 수정] 'st.sidebar' 컨텍스트 제거, 탭 내부로 이동 ---
    st.subheader("🚗 차량 선택")
    try:
        brand_list_profile = ["전체"] + get_all_brands()
    except Exception as e:
        st.error(f"브랜드 목록 로딩 실패: {e}")
        brand_list_profile = ["전체"]
    
    selected_brand_profile = st.selectbox(
        "1. 브랜드 선택", brand_list_profile, key="profile_brand", index=0
    )
    
    if selected_brand_profile != "전체":
        try:
            model_list_profile = ["전체"] + get_models_by_brand(selected_brand_profile)
        except Exception as e:
            st.error(f"차종 목록 로딩 실패: {e}")
            model_list_profile = ["전체"]
    else:
        model_list_profile = ["전체"] 
    
    selected_model_profile = st.selectbox(
        "2. 차종 선택", model_list_profile, key="profile_model", index=0
    )
    st.markdown("---") # 구분선 추가
    # --- [★ 수정] 차량 선택 로직 끝 ---

    # --- 리포트 생성 (메인 화면) ---
    if selected_brand_profile != "전체" and selected_model_profile != "전체":
        st.subheader(f"🚗 {selected_brand_profile} {selected_model_profile} 리포트")
        
        with st.spinner(f"'{selected_model_profile}' 모델의 데이터를 분석 중입니다..."):
            stats, keywords_df = get_recall_comparison(selected_brand_profile, selected_model_profile)
            history_df, all_reasons_string = get_model_profile_data(selected_brand_profile, selected_model_profile)

        if stats is None or history_df.empty:
            st.warning("해당 모델의 리콜 데이터를 찾을 수 없습니다.")
        else:
            st.markdown("#### 📊 종합 통계")
            metric_cols = st.columns(2)
            metric_cols[0].metric("총 리콜 건수", f"{stats['total_recalls']} 건")
            metric_cols[1].metric("평균 시정률", f"{stats['avg_correction_rate']} %")
            st.markdown("---")

            viz_col1, viz_col2 = st.columns(2)
            with viz_col1:
                st.markdown("#### ☁️ 리콜 사유 워드 클라우드")
                if all_reasons_string:
                    try:
                        font_path = None
                        if os.path.exists("c:/Windows/Fonts/malgun.ttf"):
                            font_path = "c:/Windows/Fonts/malgun.ttf"
                        wordcloud = WordCloud(
                            font_path=font_path, width=800, height=400, 
                            background_color='white'
                        ).generate(all_reasons_string)
                        fig, ax = plt.subplots()
                        ax.imshow(wordcloud, interpolation='bilinear')
                        ax.axis("off")
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"워드 클라우드 생성 오류: {e}")
                        st.info("한글 폰트(malgun.ttf)를 찾을 수 없거나, wordcloud 라이브러리 문제입니다.")
                else:
                    st.info("워드 클라우드를 생성할 리콜 사유 데이터가 없습니다.")

            with viz_col2:
                st.markdown("#### 📉 핵심 결함 키워드 TOP 10")
                if not keywords_df.empty:
                    chart = alt.Chart(keywords_df).mark_bar().encode(
                        x=alt.X('keyword_text', title='리콜 키워드', sort=None, axis=alt.Axis(labelAngle=-45)),
                        y=alt.Y('keyword_count', title='키워드 빈도'),
                        tooltip=[
                            alt.Tooltip('keyword_text', title='키워드'),
                            alt.Tooltip('keyword_count', title='빈도수'),
                            alt.Tooltip('keyword_desc', title='설명')
                        ]
                    ).properties(height=380).interactive()
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("분석된 키워드 데이터가 없습니다.")
            st.markdown("---")
            
            st.markdown("#### 📋 상세 리콜 이력 검색")
            st.info("특정 연도 또는 키워드로 전체 리콜 이력을 필터링할 수 있습니다.")

            search_col1, search_col2 = st.columns(2)
            with search_col1:
                current_year = datetime.date.today().year
                year_list = ["전체"] + list(range(current_year, 2014, -1))
                selected_year = st.selectbox("연도 선택", year_list, key="model_year_filter")
            with search_col2:
                try:
                    keyword_list = ["전체"] + sorted(list(keywords_df['keyword_text'].unique()))
                except:
                    keyword_list = ["전체"]
                selected_keyword = st.selectbox("키워드 선택", keyword_list, key="model_keyword_filter")
            
            filtered_history_df = history_df.copy()
            if selected_year != "전체":
                filtered_history_df = filtered_history_df[
                    pd.to_datetime(filtered_history_df['리콜개시일']).dt.year == selected_year
                ]
            if selected_keyword != "전체":
                filtered_history_df = filtered_history_df[
                    filtered_history_df['리콜사유'].str.contains(selected_keyword, na=False)
                ]

            st.dataframe(filtered_history_df, use_container_width=True, height=400)
    else:
        # --- [★ 수정] 안내 문구 수정 ---
        st.info("☝️ 위에서 분석할 브랜드와 차종을 선택해 주세요.")


# ==============================================================================
# --- [ 공통 하단 ] ---
# ==============================================================================
try:
    summary_stats = get_summary_stats()
    min_date, max_date = summary_stats['data_period']
    st.markdown("---")
    if min_date != 'N/A':
        st.caption(f"ℹ️ (데이터 기준 기간: {min_date} ~ {max_date})")
except Exception:
    pass