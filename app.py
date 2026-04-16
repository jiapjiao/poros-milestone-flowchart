import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

st.set_page_config(page_title="Poros Milestone 流程图", layout="wide")
st.title("🚀 Poros 产品 Milestone 流程图")
st.markdown("**流程图美化版**：小圆点节点 + 日期显示 + 横线连接")

# 加载数据（保持不变）
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx", sheet_name="产品信息与Milestone", engine="openpyxl")
    df = df.dropna(subset=['产品名称']).copy()
    df['产品名称'] = df['产品名称'].astype(str).str.strip()
    df = df[df['产品名称'] != '']
   
    if '父记录' in df.columns:
        df['父记录'] = df['父记录'].astype(str).str.strip().replace(['nan', 'None', ''], None)
    return df

df = load_data()

st.sidebar.header("选择产品")
selected = st.sidebar.selectbox("选择产品", sorted(df['产品名称'].unique()))

# 主产品 + 子产品
main_df = df[df['产品名称'] == selected].copy()
child_df = df[df['父记录'] == selected].copy() if '父记录' in df.columns else pd.DataFrame()
combined = pd.concat([main_df, child_df])

# 构建数据
data = []
for _, row in combined.iterrows():
    name = row['产品名称']
    display = f"→ {name}" if row.get('父记录') == selected else name
   
    for i in [1, 2, 3]:
        date = row.get(f"Milestone {i} 目标日期")
        desc = str(row.get(f"Milestone {i} 描述", "")).strip()
       
        if pd.notna(date):
            short = (desc[:40] + "...") if len(desc) > 40 else desc
            short = short if short else "无描述"
           
            data.append({
                "产品": display,
                "阶段": f"MS{i}",
                "开始": date - timedelta(days=3),
                "结束": date + timedelta(days=3),
                "描述": short,
                "完整描述": desc or "无描述",
                "日期": date.strftime("%m.%d")
            })

gantt_df = pd.DataFrame(data)

if gantt_df.empty:
    st.error(f"{selected} 暂无有效的 Milestone 日期")
    st.stop()

st.success(f"当前显示：**{selected}**")

# 画图（简化版，避免报错）
fig = px.timeline(
    gantt_df,
    x_start="开始",
    x_end="结束",
    y="产品",
    color="阶段",
    hover_data=["完整描述"],
    title=f"{selected} Milestone 流程图"
)

# 美化：小圆点 + 直接显示日期和描述
fig.update_traces(
    marker=dict(size=16, line=dict(width=2.5)),
    text=gantt_df["日期"] + "<br>" + gantt_df["描述"],   # 关键：节点上显示日期+描述
    textposition="top center",
    textfont=dict(size=10.5)
)

fig.update_layout(
    height=720,
    xaxis_title="时间轴 (2026 年)",
    yaxis_title="产品 / 子产品",
    legend_title="里程碑阶段",
    xaxis=dict(tickformat="%m.%d", tickangle=45),
    margin=dict(l=200, r=50, t=100, b=120)
)

fig.update_yaxes(autorange="reversed")

st.plotly_chart(fig, use_container_width=True)

st.caption("💡 小圆点 = 时间节点 • 横线连接不同日期 • 节点上方显示日期和描述")

with st.expander("查看当前产品原始数据"):
    st.dataframe(combined, use_container_width=True)