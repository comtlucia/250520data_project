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
)",
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

# 📊 선택 지역 인구 분석 지표
def extract_age(age_label):
    if '이상' in age_label:
        return 100
    return int(age_label.replace('세', '').strip())
age_ranges = list(range(0, len(ages)))
child_indexes = [i for i in age_ranges if extract_age(ages[i]) < 10]
teen_indexes = [i for i in age_ranges if 10 <= extract_age(ages[i]) < 20]
young_adult_indexes = [i for i in age_ranges if 20 <= extract_age(ages[i]) < 40]
middle_aged_indexes = [i for i in age_ranges if 40 <= extract_age(ages[i]) < 65]
elderly_indexes = [i for i in age_ranges if extract_age(ages[i]) >= 65]

child_total = sum([population_total[i] for i in child_indexes])
teen_total = sum([population_total[i] for i in teen_indexes])
young_adult_total = sum([population_total[i] for i in young_adult_indexes])
middle_aged_total = sum([population_total[i] for i in middle_aged_indexes])
middle_aged_total = sum([population_total[i] for i in middle_aged_indexes])
elderly_total = sum([population_total[i] for i in elderly_indexes])
total_population = sum(population_total)

child_ratio = round(child_total / total_population * 100, 2) if total_population > 0 else 0
teen_ratio = round(teen_total / total_population * 100, 2) if total_population > 0 else 0
young_adult_ratio = round(young_adult_total / total_population * 100, 2) if total_population > 0 else 0
middle_aged_ratio = round(middle_aged_total / total_population * 100, 2) if total_population > 0 else 0
elderly_ratio = round(elderly_total / total_population * 100, 2) if total_population > 0 else 0

st.markdown(f"""
### 🧾 {selected_region} 인구 구조 분석 결과
- 전체 인구: **{total_population:,}명**
- 🧒 어린이 비율 (0~9세): **{child_ratio}%**
- 🧑 청소년 비율 (10~19세): **{teen_ratio}%**
- 👩‍🎓 청년 비율 (20~39세): **{young_adult_ratio}%**
- 👨‍💼 중장년층 비율 (40~64세): **{middle_aged_ratio}%**
- 🧓 고령화 비율 (65세 이상): **{elderly_ratio}%**
""")

if elderly_ratio >= 20:
    st.info("🏥 고령화가 매우 높습니다. 복지센터, 건강관리시설, 노인 대상 여가 공간이 필요합니다.")
elif young_adult_ratio >= 25:
    st.info("🏫 청년 인구가 많습니다. 청년 주택, 창업 지원, 문화 공간이 유리합니다.")
elif child_ratio + teen_ratio >= 25:
    st.info("🧸 어린이와 청소년 인구가 많습니다. 놀이터, 교육시설, 학습지원 공간이 적합합니다.")
elif middle_aged_ratio >= 30:
    st.info("🏢 중장년층 비중이 높습니다. 건강관리센터, 직장인 평생교육, 중장년 커뮤니티 공간이 필요합니다.")
else:
    st.info("🏙️ 전 세대가 고르게 분포되어 있습니다. 주민센터, 도서관, 복합문화공간 등이 적절합니다.")

st.write("
" * 3)

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
