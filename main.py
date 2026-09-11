import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
)

# 앱 제목
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.markdown(
    "박스오피스 일별 데이터를 바탕으로 **시간에 따른 영화 시장의 변화와 관객 추이**를 시각화합니다."
)
st.markdown("---")


# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
  url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
  # 날짜 열을 문자열로 읽어옴
  df = pd.read_csv(url, dtype={"날짜": str})

  # 날짜 열을 datetime 형식으로 변환 (YYYYMMDD -> YYYY-MM-DD)
  df["날짜"] = pd.to_datetime(df["날짜"], format="%Y%m%d")

  # 숫자형 컬럼 정형화
  num_cols = ["순위", "일관객", "누적관객", "스크린수", "상영횟수"]
  for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

  return df


try:
  df = load_data()
except Exception as e:
  st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
  st.stop()

# ----------------------------------------------------
# Section 1: 영화별 일관객 변화
# ----------------------------------------------------
st.header("📌 Section 1. 영화별 일관객 변화 추이")
st.caption(
    "선택한 영화의 상영 기간 동안 일일 관객수가 어떻게 변화했는지 추적합니다."
)

# 영화 선택 드롭다운 (일관객 수 합계 기준 내림차순)
movie_list = (
    df.groupby("영화명")["일관객"].sum().sort_values(ascending=False).index.tolist()
)
selected_movie = st.selectbox("📊 분석할 영화를 선택하세요:", movie_list)

if selected_movie:
  movie_df = df[df["영화명"] == selected_movie].sort_values("날짜")

  # Plotly 선 그래프 생성
  fig1 = px.line(
      movie_df,
      x="날짜",
      y="일관객",
      title=f"<b>[{selected_movie}]</b> 날짜별 일관객수 변화",
      labels={"날짜": "날짜", "일관객": "일일 관객수(명)"},
      markers=True,
  )

  fig1.update_traces(
      hovertemplate=(
          "<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>"
      ),
      line=dict(width=2.5),
  )
  fig1.update_layout(
      hovermode="x unified",
      xaxis_title="날짜",
      yaxis_title="일일 관객수(명)",
      template="plotly_white",
      margin=dict(l=40, r=40, t=60, b=40),
  )

  st.plotly_chart(fig1, use_container_width=True)

  # 알 수 있는 것 문구 안내 박스
  st.info(
      f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 개봉 초기"
      " 관객 집중도, 주말/평일 간의 관객 수 변동 폭, 그리고 흥행 유효"
      " 기간(상승·하강 곡선)을 확인할 수 있습니다."
  )

st.markdown("---")

# ----------------------------------------------------
# Section 2: 관객수 상위 5개 영화의 일관객 추이 비교 (새로 추가됨)
# ----------------------------------------------------
st.header("📌 Section 2. 관객수 상위 5개 영화의 일관객 추이 비교")
st.caption(
    "전체 기간 동안 일관객 합계가 가장 높은 상위 5개 영화의 날짜별 관객"
    " 변화를 비교합니다."
)

# 전체 기간 일관객 합계 기준 상위 5개 영화 추출
top5_movies = df.groupby("영화명")["일관객"].sum().nlargest(5).index.tolist()
top5_df = df[df["영화명"].isin(top5_movies)].sort_values("날짜")

# Plotly 선 그래프 생성 (color='영화명'으로 5개 선을 다른 색상으로 구분)
fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    title="<b>[TOP 5 흥행작]</b> 날짜별 일관객수 비교",
    labels={"날짜": "날짜", "일관객": "일일 관객수(명)", "영화명": "영화 제목"},
    markers=True,
)

fig2.update_traces(
    hovertemplate=(
        "<b>영화:</b>"
        " %{fullData.name}<br><b>날짜:</b>"
        " %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>"
    ),
    line=dict(width=2),
)

fig2.update_layout(
    xaxis_title="날짜",
    yaxis_title="일일 관객수(명)",
    template="plotly_white",
    legend=dict(
        title="영화 제목 (범례 클릭 시 켜기/끄기)",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
    margin=dict(l=40, r=40, t=80, b=40),
)

# 그래프 출력
st.plotly_chart(fig2, use_container_width=True)

# 알 수 있는 것 문구 안내 박스
top5_names_str = ", ".join([f"'{m}'" for m in top5_movies])
st.info(
    f"💡 **이 그래프로 알 수 있는 것:** 해당 기간 최고 흥행작 TOP"
    f" 5({top5_names_str})의 개봉 시기 차이, 흥행 정점(피크)에서의 관객 수"
    " 차이, 그리고 동일 시기 개봉작 간의 관객 점유율 경쟁 양상을 한눈에"
    " 비교할 수 있습니다."
)

st.markdown("---")

# ----------------------------------------------------
# Section 3: 추후 추가될 그래프 구역 (확장용 레이아웃)
# ----------------------------------------------------
st.header("📌 Section 3. [추가 예정] 요일별 / 월별 관객 패턴 분석")
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 평일 대비 주말 관객 수의 증가율과"
    " 관객이 집중되는 주요 요일을 비교해 볼 수 있습니다."
)
