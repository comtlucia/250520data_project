import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")
st.title("\U0001F4CA 서울특별시 연령별 인구 분석 및 지역별 피라미드 시각화")

# 파일 경로 (같은 폴더 내 위치)
file_gender = "202504_202504_연령별인구현황_월간_남녀구분.csv"

# CSV 불러오기
df_gender = pd.read_csv(file_gender, encoding="cp949")

# 행정구역 추출 및 시각화용 위경도 설정 (예시값)
df_gender = df_gender[df_gender["행정구역"].str.contains("(\d+)", regex=True)]  # 세부 지역만 필터

region_coords = df_gender["행정구역"].str.extract(r"(?P<시군구>.*)\\(")
df_gender["시군구"] = region_coords["시군구"].str.strip()

# 사용자 선택을 위한 지도 시각화용 임시 위경도 추가 (정식 활용 시 행정구역 중심좌표 활용 필요)
df_gender["lat"] = 37.5665 + (pd.Series(range(len(df_gender))) * 0.005)
df_gender["lon"] = 126.9780 + (pd.Series(range(len(df_gender))) * 0.005)

# 지도 표시
tooltip = ["행정구역"]
st.map(df_gender.rename(columns={"lat": "latitude", "lon": "longitude"}))

selected_region = st.selectbox("\ud83d\udd0d 또는 아래 지도에서 지역을 선택하세요:", options=df_gender["행정구역"])

region_data = df_gender[df_gender["행정구역"] == selected_region].iloc[0]

# 연령 컬럼
age_columns_male = [col for col in df_gender.columns if "세" in col and "_남_" in col]
age_columns_female = [col for col in df_gender.columns if "세" in col and "_여_" in col]
ages = [col.split("_")[-1] for col in age_columns_male]

population_male = region_data[age_columns_male].str.replace(",", "").fillna("0").astype(int)
population_female = region_data[age_columns_female].str.replace(",", "").fillna("0").astype(int)

# 총합 기준 비율 계산
total_male = population_male.sum()
total_female = population_female.sum()

male_ratio = round(population_male / total_male * 100, 2)
female_ratio = round(population_female / total_female * 100, 2)

# Plotly 인구 피라미드 그래프
fig = go.Figure()

fig.add_trace(go.Bar(
    y=ages,
    x=-male_ratio,
    name="남성 (%)",
    orientation='h',
    marker_color='blue'
))

fig.add_trace(go.Bar(
    y=ages,
    x=female_ratio,
    name="여성 (%)",
    orientation='h',
    marker_color='red'
))

fig.update_layout(
    title=f"{selected_region} 연령별 인구 피라미드 (비율 기준)",
    barmode='overlay',
    xaxis=dict(title='인구 비율 (%)', tickvals=[-10, -5, 0, 5, 10],
               ticktext=['10%', '5%', '0', '5%', '10%']),
    yaxis=dict(title='연령'),
    height=700
)

st.plotly_chart(fig, use_container_width=True)
