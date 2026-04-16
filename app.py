import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Poros Milestone 流程图", layout="wide")
st.title("🚀 Poros 产品 Milestone 流程图")
st.markdown("**横向时间节点流程图**（已简化，避免常见报错）")

# 加载数据
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

# 侧边栏
st.sidebar.header("选择产品")
products = sorted(df['产品名称'].unique())
selected = st.sidebar.selectbox("选择要查看的产品", products)

# 获取数据（主 + 子）
main_df = df[df['产品名称'] == selected].copy()
child_df = df[df['父记录'] == selected].copy() if '父记录' in df.columns else pd.DataFrame()
combined_df = pd.concat([main_df, child_df])

# 构建节点（只要有日期就显示）
nodes = []
for _, row in combined_df.iterrows():
    prod = str(row['产品名称']).strip()
    display_name = f"{prod} (子)" if row.get('父记录') == selected else prod
    
    for i in [1, 2, 3]:
        date_val = row.get(f"Milestone {i} 目标日期")
        desc = str(row.get(f"Milestone {i} 描述", "")).strip()
        
        if pd.notna(date_val):
            short_desc = (desc[:45] + "...") if len(desc) > 45 else desc
            if not short_desc:
                short_desc = "(无描述)"
            nodes.append({
                "显示名称": display_name,
                "阶段": f"MS{i}",
                "日期": date_val,
                "日期标签": date_val.strftime("%m.%d"),
                "描述": short_desc
            })

timeline_df = pd.DataFrame(nodes)

if timeline_df.empty:
    st.error(f"{selected} 没有检测到 Milestone 目标日期")
    st.stop()

st.success(f"当前显示：**{selected}** （{len(timeline_df)} 个时间节点）")

# 画图（去掉容易出错的 text 参数，改用 hover）
fig = px.timeline(
    timeline_df,
    x_start="日期",
    x_end="日期",
    y="显示名称",
    color="阶段",
    hover_data={"描述": True},
    title=f"{selected} Milestone 时间节点流程图"
)

# 简单美化（避免报错）
fig.update_layout(
    height=700,
    xaxis_title="时间节点（2026 年）",
    yaxis_title="产品 / 子产品",
    xaxis=dict(tickformat="%m.%d", tickangle=45),
    margin=dict(l=120, r=50, t=100, b=120)
)

fig.update_yaxes(autorange="reversed")

st.plotly_chart(fig, use_container_width=True)

st.caption("💡 鼠标悬停在节点上可看到日期和描述 • 日期已直接读取你的 Excel")

with st.expander("查看原始数据"):
    st.dataframe(combined_df, use_container_width=True)