import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide")
st.title("📍 우리 동네 인구 구조, 데이터로 읽다")

# 파일 경로
file_gender = "202504_202504_연령별인구현황_월간_남녀구분.csv"

# CSV 불러오기
df_gender = pd.read_csv(file_gender, encoding="cp949")

# 행정구역 이름 정제: 괄호 앞 지역명만 추출
df_gender = df_gender[df_gender["행정구역"].str.contains("(\d+)", regex=True)]
df_gender["지역명"] = df_gender["행정구역"].str.split("(").str[0].str.strip()

# 동 단위만 필터링
df_gender = df_gender[df_gender["지역명"].str.endswith("동")]

# 연령 컬럼 정의
age_columns_male = [col for col in df_gender.columns if "세" in col and "_남_" in col]
age_columns_female = [col for col in df_gender.columns if "세" in col and "_여_" in col]
ages = [col.split("_")[-1] for col in age_columns_male]

# 지역 선택
selected_region = st.selectbox("📍 분석할 지역을 선택하세요:", options=df_gender["지역명"].unique())
region_data = df_gender[df_gender["지역명"] == selected_region].iloc[0]

# 값 처리 및 정수형 변환
population_male = region_data[age_columns_male].str.replace(",", "").fillna("0").astype(int).tolist()
population_female = region_data[age_columns_female].str.replace(",", "").fillna("0").astype(int).tolist()

# 총합 및 비율 계산
total_male = sum(population_male)
total_female = sum(population_female)

male_ratio = [round(p / total_male * 100, 2) for p in population_male]
female_ratio = [round(p / total_female * 100, 2) for p in population_female]

# 🎯 선택 지역 인구 피라미드
fig_pyramid = go.Figure()
fig_pyramid.add_trace(go.Bar(
    y=ages,
    x=[-v for v in male_ratio],
    name="👨 남성 (%)",
    orientation='h',
    marker=dict(color='rgba(54, 162, 235, 0.8)')
))
fig_pyramid.add_trace(go.Bar(
    y=ages,
    x=female_ratio,
    name="👩 여성 (%)",
    orientation='h',
    marker=dict(color='rgba(255, 99, 132, 0.8)')
))

fig_pyramid.update_layout(
    title=dict(text=f"📊 {selected_region} 연령별 인구 피라미드 (비율 기준)", font=dict(size=24)),
    barmode='overlay',
    xaxis=dict(title='인구 비율 (%)', tickvals=[-10, -5, 0, 5, 10], ticktext=['10%', '5%', '0', '5%', '10%']),
    yaxis=dict(title='연령'),
    height=650,
    legend=dict(x=0.02, y=1.05, orientation="h")
)

st.plotly_chart(fig_pyramid, use_container_width=True)

# 📈 전체 인구 흐름 그래프
population_total = [m + f for m, f in zip(population_male, population_female)]
df_all = pd.DataFrame({"연령": ages, "총인구": population_total})

fig_all = go.Figure(go.Bar(
    x=df_all["연령"],
    y=df_all["총인구"],
    marker=dict(color='mediumseagreen'),
    text=df_all["총인구"],
    textposition='outside',
    hovertemplate='연령 %{x}<br>인구수 %{y:,}명<extra></extra>'
))

fig_all.update_layout(
    title=dict(text="📈 전체 연령대별 인구 분포", font=dict(size=24)),
    xaxis_title="연령",
    yaxis_title="인구 수",
    height=500,
    margin=dict(t=60, l=60, r=40, b=40)
)

st.plotly_chart(fig_all, use_container_width=True)

# 🔍 유사한 지역 찾기 (동 단위, 혼합 기준: 비율 + 절댓값 차이 포함)
def hybrid_distance(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    ratio_dist = np.linalg.norm((vec1 / vec1.sum()) - (vec2 / vec2.sum()))
    scale_dist = abs(vec1.sum() - vec2.sum()) / vec1.sum()
    return ratio_dist + scale_dist

current_vector = np.array(population_total)

best_match = None
best_score = float('inf')

for _, row in df_gender.iterrows():
    if row["지역명"] == selected_region:
        continue
    male = row[age_columns_male].str.replace(",", "").fillna("0").astype(int).tolist()
    female = row[age_columns_female].str.replace(",", "").fillna("0").astype(int).tolist()
    total_vec = np.array([m + f for m, f in zip(male, female)])
    if total_vec.sum() == 0:
        continue
    score = hybrid_distance(current_vector, total_vec)
    if score < best_score:
        best_score = score
        best_match = row["지역명"]
        best_total = total_vec.tolist()

# 📊 선택 지역 인구 구조 분석

def extract_age(age_label):
    if '이상' in age_label:
        return 100
    return int(age_label.replace('세', '').strip())

age_ranges = list(range(len(ages)))
under20 = [i for i in age_ranges if extract_age(ages[i]) < 20]
youth = [i for i in age_ranges if 20 <= extract_age(ages[i]) < 40]
middle = [i for i in age_ranges if 40 <= extract_age(ages[i]) < 65]
elderly = [i for i in age_ranges if extract_age(ages[i]) >= 65]

total_population = sum(population_total)
under20_ratio = round(sum(population_total[i] for i in under20) / total_population * 100, 2)
youth_ratio = round(sum(population_total[i] for i in youth) / total_population * 100, 2)
middle_ratio = round(sum(population_total[i] for i in middle) / total_population * 100, 2)
elderly_ratio = round(sum(population_total[i] for i in elderly) / total_population * 100, 2)

st.markdown(f"""
### 🧾 {selected_region} 인구 비율 분석
- 전체 인구: **{total_population:,}명**
- 👶 0~19세 (어린이·청소년): **{under20_ratio}%**
- 👩‍🎓 20~39세 (청년): **{youth_ratio}%**
- 👨‍💼 40~64세 (중장년): **{middle_ratio}%**
- 🧓 65세 이상 (고령): **{elderly_ratio}%**
""")

summary = "📌 인구 분석 요약\n\n"
summary += f"🔢 전체 인구 구성 비율:\n"
summary += f"- 👶 어린이·청소년 (0~19세): {under20_ratio}%\n"
summary += f"- 👩‍🎓 청년 (20~39세): {youth_ratio}%\n"
summary += f"- 👨‍💼 중장년 (40~64세): {middle_ratio}%\n"
summary += f"- 🧓 고령 (65세 이상): {elderly_ratio}%\n\n"

# 고령층 우세
if elderly_ratio >= 25:
    summary += "🔎 고령 인구가 많은 지역입니다. 복지관, 경로당, 실버문화센터 등 고령친화 인프라가 필수이며, 의료 접근성 및 무장애 보행환경 확보가 필요합니다. 전통시장, 한방병원 중심의 상권도 발달하기 좋습니다."

# 청년 중심
elif youth_ratio >= 30:
    summary += "🔎 청년층이 많은 지역입니다. 임대주택, 청년창업지원, 스타트업 허브, 코워킹 스페이스, 문화예술 공간과 야간 카페 상권이 어울립니다."

# 어린이·청소년 중심
elif under20_ratio >= 25:
    summary += "🔎 어린이·청소년 비중이 높은 지역입니다. 학원가, 놀이공원, 방과후 돌봄센터, 학습카페, 청소년 문화센터 상권이 발달할 가능성이 높습니다."

# 중장년 중심
elif middle_ratio >= 35:
    summary += "🔎 중장년 인구 중심 지역입니다. 건강검진센터, 헬스클럽, 평생학습기관, 중년 재취업 프로그램, 생활편의시설 중심의 상권이 유리합니다."

# 균형형
else:
    summary += "🔎 전 세대가 고르게 분포한 균형형 지역입니다. 도서관, 공원, 커뮤니티센터, 복합문화시설 같은 가족 친화형 상권이 적합하며, 모든 세대를 연결하는 복합형 공간 설계가 필요합니다."

st.info(summary)

# 📍 유사 지역 시각화 (겹쳐서 비교)
st.markdown(f"### 🔄 {selected_region} 와(과) 가장 유사한 동: **{best_match}**")

fig_compare = go.Figure()
fig_compare.add_trace(go.Scatter(
    x=ages,
    y=population_total,
    mode='lines+markers',
    name=selected_region,
    line=dict(color='royalblue')
))
fig_compare.add_trace(go.Scatter(
    x=ages,
    y=best_total,
    mode='lines+markers',
    name=best_match,
    line=dict(color='orangered', dash='dot')
))

fig_compare.update_layout(
    title="👥 선택 동과 유사 동의 연령별 인구 구조 비교",
    xaxis_title="연령",
    yaxis_title="인구 수",
    height=500,
    legend=dict(x=0.01, y=1.1, orientation="h")
)

st.plotly_chart(fig_compare, use_container_width=True)
