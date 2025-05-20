import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📊 서울특별시 연령별 인구 시각화 (2025년 4월)")

# CSV 파일 경로 (사용자가 로컬/서버에 미리 다운로드한 상태라고 가정)
file_total = "202504_202504_연령별인구현황_월간_남녀합계.csv"
file_gender = "202504_202504_연령별인구현황_월간_남녀구분.csv"

# CSV 파일 로딩
df_total = pd.read_csv(file_total, encoding="cp949")
df_gender = pd.read_csv(file_gender, encoding="cp949")

# 서울 전체 기준 (첫 번째 행: 총계)
seoul_total = df_total.iloc[0]
seoul_gender = df_gender.iloc[0]

# 연령 컬럼 추출
age_columns_male = [col for col in df_gender.columns if "세" in col and "_남_" in col]
age_columns_female = [col for col in df_gender.columns if "세" in col and "_여_" in col]
ages = [col.split("_")[-1] for col in age_columns_male]

# 문자열 → 숫자 변환
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
