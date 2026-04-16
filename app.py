import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Poros Milestone 流程图", layout="wide")
st.title("🚀 Poros 产品 Milestone 流程图")
st.markdown("**老师要求样式**：横向时间轴 + 时间节点 + 日期和描述文字（支持父子产品）")

# 加载数据
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx", sheet_name="产品信息与Milestone", engine="openpyxl")
    
    # 转换日期（已验证有效）
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
        df['父记录'] = df['父记录'].astype(str).str.strip().replace(['nan', 'None', ''], None)
    else:
        df['父记录'] = None
    
    return df

df = load_data()

# 侧边栏选择产品
st.sidebar.header("选择要显示的产品")
main_products = sorted(df['产品名称'].unique())
selected_main = st.sidebar.selectbox("选择主产品", main_products, index=0)

# 获取主产品 + 子产品
main_rows = df[df['产品名称'] == selected_main].copy()
child_rows = df[df['父记录'] == selected_main].copy() if '父记录' in df.columns else pd.DataFrame()

show_children = not child_rows.empty
st.success(f"当前显示：**{selected_main}** {'（+ 子产品）' if show_children else ''}")

# 准备时间节点数据（放宽条件，只要有日期就显示）
def prepare_nodes(data, is_child=False):
    nodes = []
    prefix = ""
    for _, row in data.iterrows():
        prod = str(row['产品名称']).strip()
        owner = str(row.get('负责人', '')) if pd.notna(row.get('负责人')) else ''
        if is_child:
            prefix = f"{prod} → "
        
        for i in [1, 2, 3]:
            desc_col = f"Milestone {i} 描述"
            date_col = f"Milestone {i} 目标日期"
            
            desc = str(row.get(desc_col, '')) if pd.notna(row.get(desc_col)) else ""
            date_val = row.get(date_col)
            
            if pd.notna(date_val) and desc.strip() != "":   # 只要有日期和描述就加入
                short_desc = desc[:48] + ("..." if len(desc) > 48 else "")
                nodes.append({
                    "产品": prod,
                    "显示名称": prefix + prod,
                    "阶段": f"MS{i}",
                    "日期": date_val,
                    "日期标签": date_val.strftime("%m.%d"),
                    "描述": short_desc,
                    "完整描述": desc,
                    "负责人": owner
                })
    return pd.DataFrame(nodes)

# 生成数据
timeline_df = prepare_nodes(main_rows)
if show_children and not child_rows.empty:
    child_nodes = prepare_nodes(child_rows, is_child=True)
    if not child_nodes.empty:
        timeline_df = pd.concat([timeline_df, child_nodes], ignore_index=True)

if timeline_df.empty:
    st.error(f"**{selected_main}** 及其子产品暂无有效的 Milestone 日期和描述")
    st.info("提示：请尝试选择其他产品（如 PorosHoster、PorosData toolset）")
    st.stop()

# 绘制横向时间节点流程图
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
    marker=dict(size=20, line=dict(width=3, color="black")),
    text=timeline_df.apply(lambda x: f"{x['日期标签']}<br>{x['描述']}", axis=1),
    textposition="top center",
    textfont=dict(size=11)
)

fig.update_layout(
    height=680 if show_children else 520,
    xaxis_title="时间节点（2026 年）",
    yaxis_title="产品 / 子产品",
    legend_title="里程碑阶段",
    xaxis=dict(tickformat="%m.%d", tickangle=45),
    hoverlabel=dict(font_size=14, bgcolor="white"),
    margin=dict(l=100, r=50, t=100, b=120)
)

fig.update_yaxes(autorange="reversed", categoryorder="total ascending")

st.plotly_chart(fig, use_container_width=True)

st.caption("💡 每个节点上直接显示 **日期 + 描述** • 鼠标悬停看完整内容 • 有子产品时会一起显示")

# 调试表格
with st.expander("查看当前产品原始数据"):
    st.dataframe(pd.concat([main_rows, child_rows]), use_container_width=True)