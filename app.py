import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Poros Milestone 流程图", layout="wide")

st.title("🚀 Poros 产品 Milestone 流程图")
st.markdown("**老师要求的样式**：横向时间轴 + 时间节点 + 描述文字")

# 加载数据
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx", sheet_name="产品信息与Milestone", engine="openpyxl")
    
    # 转换日期
    date_cols = ["Milestone 1 目标日期", "Milestone 2 目标日期", "Milestone 3 目标日期"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = pd.to_datetime(df[col], unit='D', origin='1899-12-30', errors='coerce')
    
    df = df.dropna(subset=['产品名称']).copy()
    df['产品名称'] = df['产品名称'].astype(str).str.strip()
    df = df[df['产品名称'] != '']
    return df

df = load_data()

# 准备流程图数据（每个 Milestone 作为一个节点）
timeline_data = []

for _, row in df.iterrows():
    product = str(row['产品名称']).strip()
    owner = str(row.get('负责人', '')) if pd.notna(row.get('负责人')) else ''
    
    for i in [1, 2, 3]:
        desc_col = f"Milestone {i} 描述"
        date_col = f"Milestone {i} 目标日期"
        
        if pd.notna(row.get(desc_col)) and pd.notna(row.get(date_col)):
            desc = str(row[desc_col]).strip()
            date = row[date_col]
            
            if pd.notna(date):
                short_desc = desc[:55] + ("..." if len(desc) > 55 else "")
                timeline_data.append({
                    "产品": product,
                    "负责人": owner,
                    "阶段": f"MS{i}",
                    "日期": date,
                    "描述": short_desc,
                    "完整描述": desc,
                    "显示文字": f"{date.strftime('%m-%d')} {short_desc}"
                })

timeline_df = pd.DataFrame(timeline_data)

if timeline_df.empty:
    st.error("没有找到有效的日期和描述数据")
    st.stop()

# 绘制横向流程图（时间轴 + 节点标签）
fig = px.timeline(
    timeline_df,
    x_start="日期",
    x_end="日期",                    # 让每个点变成短的节点条
    y="产品",
    color="阶段",
    hover_data=["负责人", "完整描述"],
    title="Poros Milestone 时间节点流程图（横向）",
    labels={"产品": "产品 / 项目", "阶段": "里程碑"}
)

# 美化设置 - 更像流程图
fig.update_traces(
    marker_line_width=2,
    opacity=0.85,
    text=timeline_df["显示文字"],      # 在节点上显示日期 + 描述
    textposition="top center",
    textfont=dict(size=11)
)

fig.update_layout(
    height=750,
    xaxis_title="时间节点（2026 年）",
    yaxis_title="产品名称",
    legend_title="里程碑阶段",
    xaxis=dict(tickformat="%m-%d", tickangle=45),
    hoverlabel=dict(font_size=13, bgcolor="white"),
    margin=dict(l=50, r=50, t=80, b=120)
)

fig.update_yaxes(autorange="reversed")   # 让产品从上到下排列更自然

st.plotly_chart(fig, use_container_width=True)

st.caption("💡 使用说明：鼠标悬停在节点上可看完整描述 • 日期直接显示在节点附近 • 可拖动缩放时间范围")

# 同时保留一个简单表格供你自己查看
st.subheader("📋 原始数据表（仅供参考）")
st.dataframe(df, use_container_width=True, height=300)