import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Poros Milestone 流程图", layout="wide")
st.title("🚀 Poros 产品 Milestone 流程图")
st.markdown("**老师要求样式**：横向时间轴 + 时间节点 + 日期和描述文字（支持父子产品）")

# 加载并处理数据
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
    
    # 处理父子关系
    if '父记录' in df.columns:
        df['父记录'] = df['父记录'].astype(str).str.strip()
        df['父记录'] = df['父记录'].replace('nan', None)
    else:
        df['父记录'] = None
    
    return df

df = load_data()

# ==================== 侧边栏选择要查看的产品 ====================
st.sidebar.header("选择要显示的产品")
all_main_products = sorted(df['产品名称'].unique())
selected_main = st.sidebar.selectbox("选择主产品（或父产品）", all_main_products, index=0)

# 获取当前选中的产品及其子产品
main_df = df[df['产品名称'] == selected_main].copy()
children = df[df['父记录'] == selected_main] if '父记录' in df.columns else pd.DataFrame()

show_children = not children.empty

st.success(f"当前显示：**{selected_main}** {'（含子产品）' if show_children else ''}")

# 准备节点数据
def prepare_timeline_data(dataframe, is_child=False):
    timeline = []
    for _, row in dataframe.iterrows():
        prod = str(row['产品名称']).strip()
        owner = str(row.get('负责人', '')) if pd.notna(row.get('负责人')) else ''
        prefix = f"{prod} - " if is_child else ""
        
        for i in [1, 2, 3]:
            desc_col = f"Milestone {i} 描述"
            date_col = f"Milestone {i} 目标日期"
            if pd.notna(row.get(desc_col)) and pd.notna(row.get(date_col)):
                desc = str(row[desc_col]).strip()
                date_val = row[date_col]
                if pd.notna(date_val):
                    short_desc = desc[:50] + ("..." if len(desc) > 50 else "")
                    timeline.append({
                        "产品": prod,
                        "显示名称": prefix + prod,
                        "阶段": f"MS{i}",
                        "日期": date_val,
                        "日期标签": date_val.strftime("%m.%d"),
                        "描述": short_desc,
                        "完整描述": desc,
                        "负责人": owner
                    })
    return pd.DataFrame(timeline)

# 生成图
timeline_df = prepare_timeline_data(main_df)
if show_children:
    child_df = prepare_timeline_data(children, is_child=True)
    if not child_df.empty:
        timeline_df = pd.concat([timeline_df, child_df], ignore_index=True)

if timeline_df.empty:
    st.error("当前产品没有有效的 Milestone 日期数据")
    st.stop()

# 绘制流程图
fig = px.timeline(
    timeline_df,
    x_start="日期",
    x_end="日期",
    y="显示名称",
    color="阶段",
    hover_data=["负责人", "完整描述"],
    title=f"{selected_main} Milestone 时间节点流程图",
)

fig.update_traces(
    marker=dict(size=18, line=dict(width=2)),
    text=timeline_df["日期标签"] + "<br>" + timeline_df["描述"],   # 在节点上直接显示日期 + 描述
    textposition="top center",
    textfont=dict(size=11, color="black")
)

fig.update_layout(
    height=700 if show_children else 550,
    xaxis_title="时间节点（2026 年）",
    yaxis_title="产品 / 子产品",
    legend_title="里程碑",
    xaxis=dict(tickformat="%m.%d", tickangle=0),
    hoverlabel=dict(font_size=14, bgcolor="white"),
    margin=dict(l=80, r=50, t=100, b=100)
)

fig.update_yaxes(autorange="reversed")

st.plotly_chart(fig, use_container_width=True)

st.caption("💡 说明：每个圆点/节点上直接显示日期 + 描述 • 鼠标悬停可看完整文字 • 有子产品的会自动把子产品也画在同一张图里")

# 可选：显示原始数据
with st.expander("查看原始数据（调试用）"):
    st.dataframe(df[df['产品名称'] == selected_main], use_container_width=True)
    if show_children:
        st.dataframe(children, use_container_width=True)