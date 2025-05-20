import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("🌍 지역별 남녀 인구 피라미드 및 인구 구조 분석")

# 파일 경로
file_gender = "202504_202504_연령별인구현황_월간_남녀구분.csv"

# CSV 불러오기
df_gender = pd.read_csv(file_gender, encoding="cp949")

# 행정구역 이름 정제: 괄호 앞 지역명만 추출
df_gender = df_gender[df_gender["행정구역"].str.contains("(\d+)", regex=True)]
df_gender["시군구"] = df_gender["행정구역"].str.split("(").str[0].str.strip()

# 지역 선택
selected_region = st.selectbox("📍 분석할 지역을 선택하세요:", options=df_gender["행정구역"])
region_data = df_gender[df_gender["행정구역"] == selected_region].iloc[0]

# 연령 컬럼 정의
age_columns_male = [col for col in df_gender.columns if "세" in col and "_남_" in col]
age_columns_female = [col for col in df_gender.columns if "세" in col and "_여_" in col]
ages = [col.split("_")[-1] for col in age_columns_male]

# 값 처리 및 정수형 변환
population_male = region_data[age_columns_male].str.replace(",", "").fillna("0").astype(int).tolist()
population_female = region_data[age_columns_female].str.replace(",", "").fillna("0").astype(int).tolist()

# 총합 및 비율 계산
total_male = sum(population_male)
total_female = sum(population_female)

male_ratio = [round(p / total_male * 100, 2) for p in population_male]
female_ratio = [round(p / total_female * 100, 2) for p in population_female]

# 🎯 인구 피라미드 시각화
fig_pyramid = go.Figure()
fig_pyramid.add_trace(go.Bar(
    y=ages,
    x=[-v for v in male_ratio],
    name="👨 남성 (%)",
    orientation='h',
    marker=dict(color='rgba(54, 162, 235, 0.7)', line=dict(color='rgba(54, 162, 235, 1.0)', width=1))
))
fig_pyramid.add_trace(go.Bar(
    y=ages,
    x=female_ratio,
    name="👩 여성 (%)",
    orientation='h',
    marker=dict(color='rgba(255, 99, 132, 0.7)', line=dict(color='rgba(255, 99, 132, 1.0)', width=1))
))

fig_pyramid.update_layout(
    title=f"📊 {selected_region} 연령별 인구 피라미드 (비율 기준)",
    barmode='overlay',
    xaxis=dict(title='인구 비율 (%)', tickvals=[-10, -5, 0, 5, 10], ticktext=['10%', '5%', '0', '5%', '10%']),
    yaxis=dict(title='연령'),
    plot_bgcolor='white',
    height=650,
    legend=dict(x=0.02, y=1.05, orientation="h")
)

st.plotly_chart(fig_pyramid, use_container_width=True)

# 📈 전체 인구 그래프 (남+여 합계 기준 상위 연령 10개)
population_total = [m + f for m, f in zip(population_male, population_female)]
df_top10 = pd.DataFrame({"연령": ages, "총인구": population_total})
df_top10 = df_top10.sort_values(by="총인구", ascending=False).head(10).sort_values(by="총인구")

fig_top10 = go.Figure(go.Bar(
    x=df_top10["총인구"],
    y=df_top10["연령"],
    orientation='h',
    marker=dict(color='mediumseagreen'),
    text=df_top10["총인구"],
    textposition='outside',
    hovertemplate='연령 %{y}<br>인구수 %{x:,}명<extra></extra>'
))

fig_top10.update_layout(
    title="🏆 인구 수 기준 상위 10개 연령대",
    xaxis_title="인구 수",
    yaxis_title="연령",
    plot_bgcolor='white',
    height=500,
    margin=dict(t=60, l=60, r=40, b=40)
)

st.plotly_chart(fig_top10, use_container_width=True)
