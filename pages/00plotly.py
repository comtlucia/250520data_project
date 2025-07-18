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
st.write("")

if elderly_ratio >= 25:
    st.markdown("""
🧓 **고령 인구 비중이 높은 지역입니다.**  
- 복지관, 실버문화센터, 한방병원 등 고령 친화 시설 확충이 시급합니다.  
- 무장애 보행환경, 건강보조식품점, 전통시장 중심의 상권이 적합합니다.
""")

elif youth_ratio >= 30:
    st.markdown("""
👩‍🎓 **청년층이 많은 지역입니다.**  
- 청년 창업지원, 임대주택, 문화예술 공간과 야간 활동 기반이 중요합니다.  
- 공유 오피스, 감성 카페, 푸드트럭 거리 같은 트렌디한 상권이 적합합니다.
""")

elif under20_ratio >= 25:
    st.markdown("""
👶 **어린이·청소년 비중이 높은 지역입니다.**  
- 학군, 놀이시설, 돌봄센터, 청소년 문화공간 확충이 요구됩니다.  
- 학원가, 키즈카페, 문구점 중심 상권이 발달할 수 있습니다.
""")

elif middle_ratio >= 35:
    st.markdown("""
👨‍💼 **중장년층 중심 지역입니다.**  
- 평생교육시설, 건강관리센터, 재취업센터와 생활편의시설이 필요합니다.  
- 약국, 대형마트, 실속형 생활밀착 상권이 효과적입니다.
""")

else:
    st.markdown("""
🏙️ **세대가 고르게 분포된 균형형 지역입니다.**  
- 세대 간 공존 가능한 복합문화공간, 도서관, 가족공원 등 조화로운 인프라가 적합합니다.  
- 세대 연계를 고려한 복합형 상권 설계가 바람직합니다.
""")
st.write(" " *3)

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
