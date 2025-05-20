import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📊 서울특별시 연령별 인구 시각화 (2025년 4월)")

# GitHub 경로 입력받기
st.markdown("#### 🔗 GitHub의 CSV 파일 주소를 아래에 입력하세요.")
url_total = st.text_input("남녀 합계 파일 (ex. https://raw.githubusercontent.com/사용자명/저장소/파일경로.csv)")
url_gender = st.text_input("남녀 구분 파일 (ex. https://raw.githubusercontent.com/사용자명/저장소/파일경로.csv)")

if url_total and url_gender:
    try:
        # CSV 파일 불러오기
        df_total = pd.read_csv(url_total, encoding="cp949")
        df_gender = pd.read_csv(url_gender, encoding="cp949")

        # 서울 전체 기준 (첫 번째 행)
        seoul_total = df_total.iloc[0]
        seoul_gender = df_gender.iloc[0]

        # 연령별 컬럼 추출
        age_columns_male = [col for col in df_gender.columns if "세" in col and "_남_" in col]
        age_columns_female = [col for col in df_gender.columns if "세" in col and "_여_" in col]
        ages = [col.split("_")[-1] for col in age_columns_male]

        # 숫자 변환 (콤마 제거 + NaN 처리)
        population_male = seoul_gender[age_columns_male].str.replace(",", "").fillna("0").astype(int)
        population_female = seoul_gender[age_columns_female].str.replace(",", "").fillna("0").astype(int)

        # Plotly 시각화
        fig = go.Figure()
        fig.add_trace(go.Bar(x=ages, y=population_male, name="남성", marker_color='blue'))
        fig.add_trace(go.Bar(x=ages, y=population_female, name="여성", marker_color='red'))

        fig.update_layout(
            title="서울특별시 연령별 인구 (2025년 4월)",
            xaxis_title="연령",
            yaxis_title="인구 수",
            barmode='stack',
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ 파일을 불러오는 중 오류가 발생했습니다: {e}")
else:
    st.info("👆 위에 GitHub의 CSV 파일 URL을 입력하세요.")
