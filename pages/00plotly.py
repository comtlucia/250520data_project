import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📊 서울특별시 연령별 인구 피라미드 (2025년 4월)")

# 파일 경로 (같은 폴더 내 위치)
file_gender = "202504_202504_연령별인구현황_월간_남녀구분.csv"

# CSV 불러오기
df_gender = pd.read_csv(file_gender, encoding="cp949")

# 행정구역 이름 목록
regions = df_gender["행정구역"].tolist()

# -----------------------------------
# 🏙️ 사용자 지역 선택
# -----------------------------------
selected_region = st.selectbox("🔍 지역을 선택하세요", options=regions)

# 선택한 지역의 행 데이터 추출
region_data = df_gender[df_gender["행정구역"] == selected_region].iloc[0]

# 연령 컬럼 분리
age_columns_male = [col for col in df_gender.columns if "세" in col and "_남_" in col]
age_columns_female = [col for col in df_gender.columns if "세" in col and "_여_" in col]
ages = [col.split("_")[-1] for col in age_columns_male]

# 문자열 → 숫자 변환
population_male = region_data[age_columns_male].str.replace(",", "").fillna("0").astype(int)
population_female = region_data[age_columns_female].str.replace(",", "").fillna("0").astype(int)

# -----------------------------------
# 📊 인구 피라미드 생성 (Plotly)
# -----------------------------------
fig = go.Figure()

fig.add_trace(go.Bar(
    y=ages,
    x=-population_male,
    name="남성",
    orientation='h',
    marker_color='blue'
))

fig.add_trace(go.Bar(
    y=ages,
    x=population_female,
    name="여성",
    orientation='h',
    marker_color='red'
))

fig.update_layout(
    title=f"{selected_region} 연령별 인구 피라미드 (2025년 4월)",
    barmode='overlay',
    xaxis=dict(title='인구 수', tickvals=[-5000, -2500, 0, 2500, 5000],
               ticktext=['5,000', '2,500', '0', '2,500', '5,000']),
    yaxis=dict(title='연령'),
    height=700
)

st.plotly_chart(fig, use_container_width=True)
