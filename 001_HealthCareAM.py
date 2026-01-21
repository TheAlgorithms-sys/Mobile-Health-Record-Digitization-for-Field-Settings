import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import pytesseract

# --- PAGE CONFIG ---
st.set_page_config(page_title="HealthTrack AI", layout="wide")

# --- CORE LOGIC ---
class HealthCareWebEngine:
    def _init_(self, data_frame):
        self.dataFrame = data_frame

    def identifyNumericFeatures(self):
        cols = self.dataFrame.select_dtypes(include=["int64", "float64"]).columns.tolist()
        return [c for c in cols if c.lower() != "patientid"]

    def calculateMean(self):
        features = self.identifyNumericFeatures()
        return pd.DataFrame({
            "Feature": features,
            "Mean": [self.dataFrame[f].mean() for f in features]
        })

# --- UI ---
st.title("🏥 HealthTrack: Paper-to-Digital Assistant")
st.markdown("Digitizing handwritten records for continuity of care")

tabs = st.tabs(["📤 Upload & OCR", "📊 Patient Analytics", "📜 History"])

# ---------- TAB 1 ----------
with tabs[0]:
    st.header("Capture Medical Document")
    uploaded_image = st.file_uploader(
        "Upload lab report / prescription",
        type=["jpg", "jpeg", "png"],
        key="ocr_uploader"
    )

    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Document", width=400)

        if st.button("Extract Text (OCR)"):
            with st.spinner("Running OCR..."):
                text = pytesseract.image_to_string(image)
                st.text_area("Extracted Text", text, height=250)
                st.info("Future version: Auto-parse into structured health records.")

# ---------- TAB 2 ----------
with tabs[1]:
    st.header("Patient Analytics")
    uploaded_file = st.file_uploader(
        "Upload Health Records (Excel)",
        type=["xlsx"],
        key="excel_uploader"
    )

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.session_state["df"] = df
        except Exception as e:
            st.error(f"Error reading file: {e}")
            st.stop()

        engine = HealthCareWebEngine(df)
        mean_df = engine.calculateMean()

        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Summary Statistics")
            st.dataframe(mean_df, use_container_width=True)

        with col2:
            st.subheader("Average Values")
            fig, ax = plt.subplots()
            sns.barplot(data=mean_df, x="Feature", y="Mean", ax=ax)
            plt.xticks(rotation=45)
            st.pyplot(fig)

        # Correlation
        numeric_cols = engine.identifyNumericFeatures()
        if len(numeric_cols) > 1:
            st.subheader("Correlation Heatmap")
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax2)
            st.pyplot(fig2)

# ---------- TAB 3 ----------
with tabs[2]:
    st.header("Patient Follow-up History")
    if "df" in st.session_state:
        st.dataframe(st.session_state["df"].tail(10))
    else:
        st.warning("Upload health records in Analytics tab first.")

# --- SIDEBAR ---
st.sidebar.info("🔐 Data processed locally. Ensure patient consent.")