import streamlit as st
import pandas as pd

st.set_page_config(page_title="Poros Milestone", layout="wide")

st.title("🚀 Poros 产品 Milestone 流程图")
st.success("✅ 应用加载成功！如果看到这行字，说明基本没问题了。")

try:
    df = pd.read_excel("data.xlsx", sheet_name="产品信息与Milestone")
    st.write(f"✅ 数据读取成功！共有 {len(df)} 行记录")
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"读取 Excel 出错: {str(e)}")
    st.info("请确认 data.xlsx 文件存在且在仓库根目录")