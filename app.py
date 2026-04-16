import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Poros 产品 Milestone 流程图", layout="wide")
st.title("🚀 Poros 产品 Milestone 流程图")

# 读取 Excel 并处理日期（关键修复）
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx", sheet_name="产品信息与Milestone", engine="openpyxl")
    
    # 处理 Excel 序列号日期（46119 等）
    date_cols = ["Milestone 1 目标日期", "Milestone 2 目标日期", "Milestone 3 目标日期"]
    for col in date_cols:
        if col in df.columns:
            # 转换 Excel 数字日期
            df[col] = pd.to_numeric(df[col], errors='coerce')
            mask = df[col].notna()
            df.loc[mask, col] = pd.to_timedelta(df.loc[mask, col], unit='D') + pd.Timestamp('1899-12-30')
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # 清理空行和空产品名称
    df = df.dropna(subset=['产品名称']).copy()
    df = df[df['产品名称'].astype(str).str.strip() != '']
    
    return df

df = load_data()

if df.empty:
    st.error("数据为空，请检查 data.xlsx 文件")
    st.stop()

# 侧边栏过滤
st.sidebar.header("筛选条件")
products = sorted(df['产品名称'].dropna().unique())
selected_products = st.sidebar.multiselect("选择产品", products, default=products[:5])

status = df['当前状态'].dropna().unique()
selected_status = st.sidebar.multiselect("当前状态", status, default=status)

# 过滤数据
filtered_df = df.copy()
if selected_products:
    filtered_df = filtered_df[filtered_df['产品名称'].isin(selected_products)]
if selected_status:
    filtered_df = filtered_df[filtered_df['当前状态'].isin(selected_status)]

st.success(f"✅ 数据加载成功！共 {len(filtered_df)} 条记录（来自飞书文档）")

# 显示原始表格（类似飞书视图）
st.subheader("📋 原始 Milestone 数据表")
st.dataframe(filtered_df, use_container_width=True, height=400)

# ==================== 生成 Gantt 图（最像老师想要的流程图） ====================
st.subheader("📊 Milestone 时间轴流程图（Gantt 图）")

# 准备 Gantt 图数据（把每个 Milestone 转成一行）
gantt_data = []

for _, row in filtered_df.iterrows():
    product = str(row['产品名称']).strip()
    owner = str(row.get('负责人', '')) if pd.notna(row.get('负责人')) else ''
    
    for i in [1, 2, 3]:
        desc_col = f"Milestone {i} 描述"
        date_col = f"Milestone {i} 目标日期"
        
        if pd.notna(row.get(desc_col)) and pd.notna(row.get(date_col)):
            desc = str(row[desc_col]).strip()
            target_date = row[date_col]
            
            if pd.notna(target_date) and isinstance(target_date, pd.Timestamp):
                gantt_data.append({
                    "产品": product,
                    "负责人": owner,
                    "Milestone": f"MS{i}: {desc[:60]}{'...' if len(desc)>60 else ''}",
                    "开始日期": target_date - pd.Timedelta(days=7),  # 给一点起始宽度
                    "结束日期": target_date + pd.Timedelta(days=1),
                    "颜色分组": f"Milestone {i}"
                })

gantt_df = pd.DataFrame(gantt_data)

if not gantt_df.empty:
    # 绘制 Gantt 图
    fig = px.timeline(
        gantt_df,
        x_start="开始日期",
        x_end="结束日期",
        y="产品",
        color="颜色分组",
        hover_data=["负责人", "Milestone"],
        title="Poros 各产品 Milestone 时间轴（点击可交互）",
        labels={"产品": "产品名称", "颜色分组": "里程碑阶段"}
    )
    
    fig.update_yaxes(autorange="reversed")  # 让最新产品在上面
    fig.update_layout(
        height=max(600, len(gantt_df) * 25),
        xaxis_title="时间",
        yaxis_title="产品",
        legend_title="里程碑阶段",
        hoverlabel=dict(bgcolor="white", font_size=12)
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("没有找到有效的日期数据，无法生成时间轴图。请检查 Excel 中的日期列是否有值。")

# 额外信息
st.caption("💡 提示：日期来自飞书 Excel 的 Milestone 目标日期，已自动转换为正常日期。图表可缩放、hover 查看详情。")