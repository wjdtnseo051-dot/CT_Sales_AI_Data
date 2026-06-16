import streamlit as st
from pathlib import Path
from pypdf import PdfReader
import pandas as pd

st.set_page_config(page_title="CT Sales AI", layout="wide")

# ===== Header =====
logo_path = Path("logo.png")

if logo_path.exists():
    st.image(str(logo_path), width=900)

st.markdown(
    """
    <h2 style='color:#cc0000;'>CT Sales AI Assistant</h2>
    <p>Canon / GE / Siemens / Philips CT 사양, 비교표, 영업 포인트 검색</p>
    <hr>
    """,
    unsafe_allow_html=True
)

# ===== Data =====
data_folder = Path("Data")
pdf_files = list(data_folder.rglob("*.pdf"))
excel_files = list(data_folder.rglob("*.xlsx"))

# ===== 직접 입력 영업 지식 DB =====
sales_knowledge = {
    "vibe": {
        "공격 포인트": [
            "디텍터 구조상 FOV 32cm 제한 이슈를 고객 확인 포인트로 제시 가능",
            "하드웨어/물리적 구조 차이를 모식도로 설명하면 고객 이해도가 높음",
            "중국 생산 여부는 제조국을 중요하게 보는 고객에게 확인 포인트로 활용 가능",
        ],
        "고객 설명": [
            "VIBE는 스펙상 장점도 있으나, 실제 임상 운용에서는 디텍터 FOV 제한, 하드웨어 구조 차이, 제조국 이슈를 함께 확인할 필요가 있습니다.",
        ],
    },
    "prism": {
        "셀링 포인트": [
            "AiCE 기반 Deep Learning Reconstruction",
            "PIQE 1024 기반 초고해상도 재구성",
            "160mm wide coverage",
            "Clear Motion 기반 cardiac/chest motion correction",
            "SURESubtraction 기반 CTA workflow 개선",
        ],
        "고객 설명": [
            "PRISM은 고해상도, 저선량, 심장/흉부 모션 보정, Subtraction workflow까지 모두 강조할 수 있는 High-end CT입니다.",
        ],
    },
    "serve": {
        "셀링 포인트": [
            "160 slice / 80 detector rows",
            "40mm coverage",
            "80cm gantry aperture",
            "AiCE 적용 가능",
            "SURESubtraction, 3D Landmark Scan 등 workflow 장점",
        ],
    },
    "pulse": {
        "공격 포인트": [
            "일부 AI reconstruction 옵션 구성 여부 확인 필요",
            "초고해상도/1024 matrix 관련 실제 AI 기반 여부 확인 필요",
            "콘솔 옵션 구성에 따라 reconstruction workflow 차이가 발생할 수 있음",
        ],
    },
}

# ===== Functions =====
def read_pdf_text(pdf_path, max_pages=5):
    reader = PdfReader(pdf_path)
    text = ""

    for page in reader.pages[:max_pages]:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def read_excel_table(excel_path):
    try:
        df = pd.read_excel(excel_path, header=None)
        return df.fillna("")
    except Exception:
        return pd.DataFrame()


def find_sales_knowledge(question):
    q = question.lower()
    results = []

    keyword_alias = {
        "vibe": ["vibe", "바이브"],
        "prism": ["prism", "프리즘"],
        "serve": ["serve", "서브"],
        "pulse": ["pulse", "펄스", "pro.pulse"],
    }

    for keyword, aliases in keyword_alias.items():
        if any(alias in q for alias in aliases):
            categories = sales_knowledge.get(keyword, {})

            for category, answers in categories.items():
                if (
                    category in question
                    or "공격" in question
                    or "셀링" in question
                    or "장점" in question
                    or "설명" in question
                    or "포인트" in question
                ):
                    results.append({
                        "keyword": keyword.upper(),
                        "category": category,
                        "answers": answers,
                    })

    return results


def find_files(question):
    q = question.lower()
    matched = []

    for file in list(pdf_files) + list(excel_files):
        target = (file.name + " " + str(file.parent)).lower()

        if "미드하이" in q or "mid_high" in q or "mid high" in q:
            if "mid_high" in target or "mid high" in target or "high" in target:
                matched.append(file)

        elif "미드미드" in q or "mid_mid" in q or "mid mid" in q:
            if "mid_mid" in target or "mid mid" in target:
                matched.append(file)

        elif "serve" in q or "서브" in q:
            if "serve" in target:
                matched.append(file)

        elif "prism" in q or "프리즘" in q:
            if "prism" in target:
                matched.append(file)

        elif "vibe" in q or "바이브" in q:
            if "vibe" in target:
                matched.append(file)

        elif "exceed" in q or "lb" in q or "엑시드" in q:
            if "exceed" in target or "lb" in target:
                matched.append(file)

        elif "pulse" in q or "펄스" in q:
            if "pulse" in target:
                matched.append(file)

        elif "canon" in q or "캐논" in q:
            if "canon" in target or "aquilion" in target:
                matched.append(file)

        elif "ge" in q:
            if "ge" in target or "revolution" in target:
                matched.append(file)

        elif "siemens" in q or "지멘스" in q:
            if "siemens" in target or "somatom" in target:
                matched.append(file)

        elif "philips" in q or "필립스" in q:
            if "philips" in target:
                matched.append(file)

    return matched


def parse_mid_high_table():
    rows = [
        ["Model", "Aquilion Serve SP", "SOMATOM X.CITE", "Revolution Ascend", "5300"],
        ["Detector", "PUREViSION", "Stellarinfinity", "Gemstone", "NonoPannel Elite Detector"],
        ["No. of slice per rotation", "160 slice", "128 slice", "128 slice", "128 slice"],
        ["No. of detector rows", "80 rows", "64 rows", "64 rows", "64 rows"],
        ["Width of detector rows", "0.5 mm", "0.6 mm", "0.625 mm", "0.625 mm"],
        ["Max. Coverage of detector", "40 mm", "38.4 mm", "40 mm", "40 mm"],
        ["Min. Slice thickness", "0.5 mm", "0.6 mm", "0.625 mm", "0.625 mm"],
        ["Gantry aperture size", "80 cm", "82 cm", "75 cm", "72 cm"],
        ["Min. Rotation time", "0.35 sec", "0.3 sec", "0.35 sec", "0.35 sec"],
        ["Cooling Type", "Oil/Air", "Chilled water", "Oil/Air", "Oil/Air"],
        ["Anode heat storage", "7.5 MHU", "0.6 MHU", "7.0 MHU", "8.0 MHU"],
        ["Max. kVp Range", "135 kVp", "150 kVp", "140 kVp", "140 kVp"],
        ["Max. mA Range", "600 mA", "1200 mA (option)", "600 mA", "667 mA"],
        ["Scan Range", "180 cm", "160 cm", "170 cm", "185 cm"],
        ["Min. table height", "33 cm", "33 cm", "45 cm", "45 cm"],
        ["Max. table weight", "220 kg", "227 kg option", "227 kg", "227 kg"],
        ["Noise reduction filter", "QDS+", "N/A", "4D noise reduction", "Provided"],
        ["Metal artifact reduction", "SEMAR", "iMAR", "SMAR", "O MAR"],
        ["Adaptive iterative dose reduction", "AIDR 3D Enhanced", "ADMIRE", "ASIR-V", "IMR"],
        ["Auto kV selection", "SUREkV", "CARE kV", "kV Assist", "Right Dose Package"],
        ["AI iterative reconstruction", "AiCE (All Parts)", "N/A", "TrueFidelity", "Precise image"],
        ["AI Ultra High Resolution", "0.25mm PIQE 1024", "N/A", "ZeeFree / N/A", "SSF2 / Precise Cardiac"],
        ["Image reconstruction time", "50 image/sec with AIDR 3D", "16~40 image/sec with ADMIRE", "65 image/sec with ASIR-V", "100 IPS with FBP"],
        ["Cardiac navigation", "SURECardio", "Provided", "Provided", "Provided"],
        ["Min. temporal resolution", "35 msec", "75 msec", "45 msec", "45 msec"],
        ["Max. no. of segment", "5 segment", "2 segment", "4 segment", "4 segment"],
        ["Auto Position", "3D Camera Built-in", "3D Camera 2EA option", "option", "option"],
        ["Auto Planning", "3D Landmark Scan", "N/A", "N/A", "N/A"],
        ["3D SCOUT View", "3D Landmark Scan", "N/A", "N/A", "N/A"],
        ["ONE Click Subtraction", "SURESubtraction", "N/A", "N/A", "N/A"],
    ]

    return pd.DataFrame(rows, columns=["항목", "Canon", "Siemens", "GE", "Philips"])


def show_sales_knowledge(results):
    st.subheader("🎯 영업 포인트")

    for result in results:
        st.markdown(f"### {result['keyword']} / {result['category']}")

        for idx, answer in enumerate(result["answers"], start=1):
            st.markdown(f"{idx}. {answer}")


def show_file_result(file):
    st.markdown(f"### 📄 {file.name}")

    if file.suffix.lower() == ".pdf":
        if "mid_high" in file.name.lower() or "serve" in file.name.lower():
            df = parse_mid_high_table()
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            text = read_pdf_text(file)
            st.text(text[:3000])

    elif file.suffix.lower() == ".xlsx":
        df = read_excel_table(file)
        st.dataframe(df, use_container_width=True, hide_index=True)


# ===== Search UI =====
question = st.text_input(
    "질문을 입력하세요",
    placeholder="예: 바이브 공격 포인트 알려줘 / 미드하이 Serve 비교해줘"
)

if question:
    st.markdown(f"### 질문: {question}")

    knowledge_results = find_sales_knowledge(question)
    matched_files = find_files(question)

    if knowledge_results:
        show_sales_knowledge(knowledge_results)

    if matched_files:
        st.subheader("📚 참고 자료")
        st.success(f"관련 자료 {len(matched_files)}개를 찾았습니다.")

        for file in matched_files:
            show_file_result(file)

    if not knowledge_results and not matched_files:
        st.warning("관련 자료 또는 영업 포인트를 찾지 못했습니다.")