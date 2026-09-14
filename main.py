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
    "박스오피스 일별 데이터를 바탕으로 **시간에 따른 영화 시장의 변화와 관객"
    " 추이**를 시각화합니다."
)
st.markdown("---")


# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
  url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
  df = pd.read_csv(url, dtype={"날짜": str})
  df["날짜"] = pd.to_datetime(df["날짜"], format="%Y%m%d")
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

movie_list = (
    df.groupby("영화명")["일관객"].sum().sort_values(ascending=False).index.tolist()
)
selected_movie = st.selectbox("📊 분석할 영화를 선택하세요:", movie_list)

if selected_movie:
  movie_df = df[df["영화명"] == selected_movie].sort_values("날짜")

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

st.markdown("---")

# ----------------------------------------------------
# Section 2: 관객수 상위 5개 영화의 일관객 추이 비교
# ----------------------------------------------------
st.header("📌 Section 2. 관객수 상위 5개 영화의 일관객 추이 비교")
st.caption(
    "전체 기간 동안 일관객 합계가 가장 높은 상위 5개 영화의 날짜별 관객"
    " 변화를 비교합니다."
)

top5_movies = df.groupby("영화명")["일관객"].sum().nlargest(5).index.tolist()
top5_df = df[df["영화명"].isin(top5_movies)].sort_values("날짜")

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

st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ----------------------------------------------------
# Section 3: 날짜별 10위권 일관객 합계 (영역 그래프)
# ----------------------------------------------------
st.header("📌 Section 3. 날짜별 전체(10위권) 일관객 합계 추이")
st.caption(
    "매일 박스오피스 10위권 영화들의 일관객 수를 합산하여 일별 극장가 총"
    " 관객수의 변화 흐름을 영역 그래프로 보여줍니다."
)

daily_total = df.groupby("날짜")["일관객"].sum().reset_index()

fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="<b>[전체 극장가]</b> 날짜별 10위권 일관객 합계 추이",
    labels={"날짜": "날짜", "일관객": "총 일관객수(명)"},
)

fig3.update_traces(
    hovertemplate=(
        "<b>날짜:</b> %{x|%Y-%m-%d}<br><b>합계 관객수:</b>"
        " %{y:,}명<extra></extra>"
    ),
    fillcolor="rgba(31, 119, 180, 0.3)",
    line=dict(color="rgba(31, 119, 180, 1)", width=2),
)

top3_days = daily_total.nlargest(3, "일관객").reset_index(drop=True)

for idx, row in top3_days.iterrows():
  rank = idx + 1
  date_str = row["날짜"].strftime("%Y-%m-%d")
  audience_cnt = row["일관객"]

  fig3.add_annotation(
      x=row["날짜"],
      y=audience_cnt,
      text=f"<b>TOP {rank}</b><br>{date_str}<br>({audience_cnt:,}명)",
      showarrow=True,
      arrowhead=2,
      arrowsize=1,
      arrowwidth=2,
      arrowcolor="#d62728",
      ax=0,
      ay=-45,
      bgcolor="white",
      bordercolor="#d62728",
      borderwidth=1.5,
      font=dict(size=11, color="#d62728"),
  )

fig3.update_layout(
    xaxis_title="날짜",
    yaxis_title="총 일관객수(명)",
    template="plotly_white",
    hovermode="x unified",
    margin=dict(l=40, r=40, t=60, b=40),
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ----------------------------------------------------
# Section 4: 기간 내 관객수 TOP 10 영화 가로 막대그래프
# ----------------------------------------------------
st.header("📌 Section 4. 기간 내 일관객 합계 TOP 10 영화")
st.caption(
    "해당 기간 동안 박스오피스 10위권 내에서 동원한 일관객 합계 기준 TOP 10"
    " 영화를 가로 막대그래프로 비교합니다."
)

top10_summary = (
    df.groupby("영화명")
    .agg(관객수합계=("일관객", "sum"), 차트인일수=("날짜", "nunique"))
    .reset_index()
)

top10_summary = top10_summary.nlargest(10, "관객수합계")
top10_summary_sorted = top10_summary.sort_values("관객수합계", ascending=True)

fig4 = px.bar(
    top10_summary_sorted,
    x="관객수합계",
    y="영화명",
    orientation="h",
    title="<b>[TOP 10 영화]</b> 기간 내 일관객 합계 및 10위권 유지 일수",
    labels={
        "관객수합계": "기간 내 관객수 합계(명)",
        "영화명": "영화 제목",
        "차트인일수": "10위권 진입 일수",
    },
    color="관객수합계",
    color_continuous_scale="Blues",
    custom_data=["차트인일수"],
)

fig4.update_traces(
    hovertemplate=(
        "<b>영화명:</b> %{y}<br><b>관객수 합계:</b> %{x:,}명<br><b>10위권 진입"
        " 일수:</b> %{customdata[0]}일<extra></extra>"
    )
)

fig4.update_layout(
    xaxis_title="기간 내 관객수 합계(명)",
    yaxis_title="영화 제목",
    template="plotly_white",
    coloraxis_showscale=False,
    margin=dict(l=40, r=40, t=60, b=40),
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ----------------------------------------------------
# Section 5: 월×요일별 일관객 합계 히트맵
# ----------------------------------------------------
st.header("📌 Section 5. 월×요일별 관객 분포 패턴 (히트맵)")
st.caption(
    "월(1월~12월)과 요일(월요일~일요일)의 조합별로 일관객 합계를 계산하여 관객이"
    " 몰리는 시기를 색상의 짙기로 표현합니다."
)

df_heatmap = df.copy()
df_heatmap["월"] = df_heatmap["날짜"].dt.month.astype(str) + "월"

weekday_map = {
    0: "월요일",
    1: "화요일",
    2: "수요일",
    3: "목요일",
    4: "금요일",
    5: "토요일",
    6: "일요일",
}
df_heatmap["요일"] = df_heatmap["날짜"].dt.weekday.map(weekday_map)

heatmap_pivot = df_heatmap.groupby(["월", "요일"])["일관객"].sum().reset_index()

weekday_order = [
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일",
]
month_order = [f"{m}월" for m in sorted(df_heatmap["날짜"].dt.month.unique())]

pivot_table = heatmap_pivot.pivot(index="요일", columns="월", values="일관객")
pivot_table = pivot_table.reindex(index=weekday_order, columns=month_order).fillna(
    0
)

fig5 = px.imshow(
    pivot_table,
    labels=dict(x="월", y="요일", color="일관객 합계(명)"),
    x=pivot_table.columns,
    y=pivot_table.index,
    color_continuous_scale="YlOrRd",
    title="<b>[월×요일별]</b> 총 관객수 분포 히트맵",
    aspect="auto",
)

fig5.update_traces(
    hovertemplate=(
        "<b>월:</b> %{x}<br><b>요일:</b> %{y}<br><b>일관객 합계:</b>"
        " %{z:,}명<extra></extra>"
    )
)

fig5.update_layout(
    xaxis_title="월",
    yaxis_title="요일",
    template="plotly_white",
    margin=dict(l=40, r=40, t=60, b=40),
)

st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# ----------------------------------------------------
# Section 6: 추후 추가될 그래프 구역 (확장용 레이아웃)
# ----------------------------------------------------
st.header("📌 Section 6. [추가 예정] 다음 분석 그래프 구역")
