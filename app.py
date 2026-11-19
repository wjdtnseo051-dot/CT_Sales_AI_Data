import streamlit as st
from pathlib import Path
from pypdf import PdfReader
import pandas as pd

st.set_page_config(page_title="CT Sales AI", layout="wide")

# =========================================================
# Visual theme only: all original search/data functions below are unchanged
# =========================================================
import base64
from html import escape

hero_path = Path("ct_hero.png")
hero_image = ""
if hero_path.is_file():
    hero_image = "data:image/png;base64," + base64.b64encode(hero_path.read_bytes()).decode("ascii")

st.markdown("""<style>
.stApp {background:radial-gradient(ellipse at 83% 8%,#4b0b17 0%,#1a1116 28%,#0b0b0f 72%);color:#f8f6f6}
.block-container {max-width:1320px;padding-top:2rem;padding-bottom:5rem}
header[data-testid="stHeader"] {background:transparent}
#MainMenu,footer {visibility:hidden}
.ct-hero {position:relative;overflow:hidden;min-height:345px;border:1px solid #56323b;border-radius:24px;background:linear-gradient(105deg,#161115 0%,#241319 52%,#4b101b 100%);box-shadow:0 20px 70px #0009;margin-bottom:22px;padding:42px}
.ct-hero:before {content:"";position:absolute;right:-120px;top:-150px;width:650px;height:650px;border:2px solid #e51b32;border-radius:50%;box-shadow:0 0 80px #d71c3e90;opacity:.45}
.ct-hero img {position:absolute;right:0;top:0;height:100%;width:49%;object-fit:cover;object-position:center;mask-image:linear-gradient(to right,transparent,black 22%);-webkit-mask-image:linear-gradient(to right,transparent,black 22%)}
.ct-hero .content {position:relative;z-index:2;max-width:62%}
.ct-brand {font-weight:800;font-size:19px;letter-spacing:.2px}
.ct-brand span {color:#f1293f}
.ct-hero h1 {font-size:clamp(30px,4vw,52px);line-height:1.1;letter-spacing:-1.5px;margin:65px 0 13px}
.ct-hero p {font-size:15px;color:#e4cfd4}
.ct-heading {font-size:19px;font-weight:750;margin:23px 0 10px}
div[data-testid="stTextInput"] input {background:#211b21;color:#fff;border:1px solid #67404a;border-radius:12px;min-height:54px}
div[data-testid="stButton"] button {min-height:80px;background:linear-gradient(135deg,#34232a,#1d1b20);border:1px solid #63414a;border-radius:15px;color:#fff;font-size:16px;font-weight:650;white-space:normal}
div[data-testid="stButton"] button:hover {background:#4b2732;border-color:#f13249;color:#fff}
div[data-testid="stDataFrame"] {border-radius:12px;overflow:hidden}
@media(max-width:700px){.ct-hero{padding:25px;min-height:285px}.ct-hero img{opacity:.35;width:85%}.ct-hero .content{max-width:100%}.ct-hero h1{margin-top:45px}}
</style>""", unsafe_allow_html=True)

st.markdown(
    '<div class="ct-hero">'
    + (f'<img src="{hero_image}" alt="Canon CT hero">' if hero_image else '')
    + '<div class="content"><div class="ct-brand"><span>Canon</span> &nbsp; CANON MEDICAL</div>'
    + '<h1>Canon CT AI Assistant</h1>'
    + '<p>CT Sales &amp; Clinical Knowledge Hub</p>'
    + '<p>제품 사양, 경쟁사 비교, 설치 현황 및 현장 피드백 검색</p>'
    + '</div></div>',
    unsafe_allow_html=True,
)

# =========================================================
# Data
# =========================================================

data_folder = Path("Data")

pdf_files = list(data_folder.rglob("*.pdf"))
excel_files = list(data_folder.rglob("*.xlsx"))


# =========================================================
# 직접 입력 영업 지식 DB
# =========================================================

sales_knowledge = {

    # -----------------------------------------------------
    # GE VIBE
    # -----------------------------------------------------

    "vibe": {

        "설치 현황": [
            "부산성모병원",
            "BH한서병원",
            "좋은삼선병원",
        ],

        "현장 피드백": [
            "4 cm Helical scan만 가능한 부분에 대해 불만족 의견이 있음",
            "ECG-less 기능에 대해서는 대부분 만족하는 반응을 보이고 있음",
            "3D Camera의 역할 및 활용성에 대해서도 긍정적인 평가가 존재함",
        ],

        "공격 포인트": [
            "디텍터 구조상 FOV 32 cm 제한 이슈를 고객 확인 포인트로 제시 가능",
            "하드웨어/물리적 구조 차이를 모식도로 설명하면 고객 이해도가 높음",
            "중국 생산 여부는 제조국을 중요하게 보는 고객에게 확인 포인트로 활용 가능",
        ],

        "고객 설명": [
            "현재 파악된 GE VIBE CT 설치 병원은 부산성모병원, BH한서병원, 좋은삼선병원입니다.",
            "현장 피드백으로는 4 cm Helical scan만 가능한 부분에 대한 불만족 의견이 있습니다.",
            "반면 ECG-less 기능에 대해서는 대부분 만족하는 반응을 보이고 있으며, 3D Camera의 역할에 대해서도 긍정적인 평가가 존재합니다.",
        ],
    },


    # -----------------------------------------------------
    # Canon PRISM
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # Canon Serve
    # -----------------------------------------------------

    "serve": {

        "셀링 포인트": [
            "160 slice / 80 detector rows",
            "40mm coverage",
            "80cm gantry aperture",
            "AiCE 적용 가능",
            "SURESubtraction, 3D Landmark Scan 등 workflow 장점",
        ],
    },


    # -----------------------------------------------------
    # Siemens Pro.Pulse
    # -----------------------------------------------------

    "pulse": {

        "설치 현황": [
            "강남차병원",
            "시화병원",
            "좋은강안병원",
        ],

        "현장 피드백": [
            "가장 최근 설치된 좋은강안병원에서 70 cm의 좁은 보어에 대한 피드백이 있음",
            "Dual Source 시스템이지만 3.84 cm Helical Cardiac Scan을 사용하며, HR 80 이상 환자군에서는 촬영하지 않는다는 현장 피드백이 있음",
        ],

        "공격 포인트": [
            "일부 AI reconstruction 옵션 구성 여부 확인 필요",
            "초고해상도/1024 matrix 관련 실제 AI 기반 여부 확인 필요",
            "콘솔 옵션 구성에 따라 reconstruction workflow 차이가 발생할 수 있음",
        ],

        "고객 설명": [
            "현재 파악된 Siemens SOMATOM Pro.Pulse 설치 병원은 강남차병원, 시화병원, 좋은강안병원입니다.",
            "특히 가장 최근에 설치된 좋은강안병원에서는 70 cm의 좁은 보어에 대한 피드백이 있습니다.",
            "또한 Dual Source 시스템이지만 3.84 cm Helical Cardiac Scan을 사용하며, HR 80 이상 환자군에서는 촬영하지 않는다는 현장 피드백이 존재합니다.",
        ],
    },
}


# =========================================================
# 제품명 / 별칭 DB
# =========================================================

keyword_alias = {

    "vibe": [
        "vibe",
        "vibe ct",
        "ge vibe",
        "ge vibe ct",
        "바이브",
        "바이브 ct",
        "지이 바이브",
        "지이 바이브 ct",
    ],

    "prism": [
        "prism",
        "프리즘",
        "aquilion prism",
        "aquilion one prism",
        "캐논 프리즘",
        "canon prism",
    ],

    "serve": [
        "serve",
        "serve sp",
        "서브",
        "서브 sp",
        "aquilion serve",
        "aquilion serve sp",
        "캐논 서브",
        "canon serve",
    ],

    "pulse": [
        "pulse",
        "pro.pulse",
        "pro pulse",
        "propulse",
        "프로펄스",
        "프로 펄스",
        "펄스",
        "siemens pro.pulse",
        "siemens pro pulse",
        "지멘스 프로펄스",
        "지멘스 프로 펄스",
    ],
}


# =========================================================
# 제품 표시 이름
# =========================================================

product_display_names = {
    "vibe": "GE VIBE CT",
    "prism": "Canon Aquilion ONE PRISM",
    "serve": "Canon Aquilion Serve",
    "pulse": "Siemens SOMATOM Pro.Pulse",
}


# =========================================================
# Functions
# =========================================================

def read_pdf_text(pdf_path, max_pages=5):

    try:
        reader = PdfReader(pdf_path)
        text = ""

        for page in reader.pages[:max_pages]:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    except Exception:
        return ""


def read_excel_table(excel_path):

    try:

        df = pd.read_excel(
            excel_path,
            header=None
        )

        return df.fillna("")

    except Exception:

        return pd.DataFrame()


# =========================================================
# 제품 인식
# =========================================================

def detect_products(question):

    q = question.lower()

    detected = []

    for product, aliases in keyword_alias.items():

        if any(alias.lower() in q for alias in aliases):

            detected.append(product)

    return detected


# =========================================================
# 질문 의도 인식
# =========================================================

def detect_intents(question):

    q = question.lower()

    intents = []

    # 설치 현황
    installation_words = [
        "설치",
        "설치현황",
        "설치 현황",
        "설치병원",
        "설치 병원",
        "어디 설치",
        "어디에 설치",
        "어느 병원",
    ]

    if any(word in q for word in installation_words):
        intents.append("설치 현황")


    # 현장 피드백
    feedback_words = [
        "피드백",
        "평가",
        "반응",
        "후기",
        "현장반응",
        "현장 반응",
        "사용자 반응",
        "불만",
    ]

    if any(word in q for word in feedback_words):
        intents.append("현장 피드백")


    # 공격 포인트
    attack_words = [
        "공격",
        "공격포인트",
        "공격 포인트",
        "단점",
        "약점",
        "문제점",
        "경쟁",
    ]

    if any(word in q for word in attack_words):
        intents.append("공격 포인트")


    # 셀링 포인트
    selling_words = [
        "셀링",
        "셀링포인트",
        "셀링 포인트",
        "장점",
        "강점",
        "특징",
    ]

    if any(word in q for word in selling_words):
        intents.append("셀링 포인트")


    # 고객 설명
    explanation_words = [
        "고객 설명",
        "설명해",
        "설명",
        "어떻게 말",
        "멘트",
    ]

    if any(word in q for word in explanation_words):
        intents.append("고객 설명")


    return list(dict.fromkeys(intents))


# =========================================================
# 영업 지식 검색
# =========================================================

def find_sales_knowledge(question):

    detected_products = detect_products(question)
    intents = detect_intents(question)

    results = []

    for product in detected_products:

        categories = sales_knowledge.get(product, {})

        # 질문 의도가 명확한 경우
        if intents:

            for intent in intents:

                if intent in categories:

                    results.append({
                        "keyword": product_display_names.get(
                            product,
                            product.upper()
                        ),
                        "category": intent,
                        "answers": categories[intent],
                    })

        # 질문 의도가 없는 경우
        # 해당 제품에 저장된 정보 전체 표시
        else:

            for category, answers in categories.items():

                results.append({
                    "keyword": product_display_names.get(
                        product,
                        product.upper()
                    ),
                    "category": category,
                    "answers": answers,
                })

    return results


# =========================================================
# 파일 검색
# =========================================================

def find_files(question):

    q = question.lower()

    matched = []

    for file in list(pdf_files) + list(excel_files):

        target = (
            file.name
            + " "
            + str(file.parent)
        ).lower()


        # Mid High
        if (
            "미드하이" in q
            or "mid_high" in q
            or "mid high" in q
        ):

            if (
                "mid_high" in target
                or "mid high" in target
                or "high" in target
            ):
                matched.append(file)


        # Mid Mid
        elif (
            "미드미드" in q
            or "mid_mid" in q
            or "mid mid" in q
        ):

            if (
                "mid_mid" in target
                or "mid mid" in target
            ):
                matched.append(file)


        # Serve
        elif (
            "serve" in q
            or "서브" in q
        ):

            if "serve" in target:
                matched.append(file)


        # PRISM
        elif (
            "prism" in q
            or "프리즘" in q
        ):

            if "prism" in target:
                matched.append(file)


        # VIBE
        elif (
            "vibe" in q
            or "바이브" in q
        ):

            if "vibe" in target:
                matched.append(file)


        # Exceed LB
        elif (
            "exceed" in q
            or "엑시드" in q
            or "exceed lb" in q
        ):

            if (
                "exceed" in target
                or "lb" in target
            ):
                matched.append(file)


        # Pro.Pulse
        elif (
            "pulse" in q
            or "펄스" in q
            or "프로펄스" in q
            or "pro.pulse" in q
            or "pro pulse" in q
        ):

            if (
                "pulse" in target
                or "pro.pulse" in target
                or "pro pulse" in target
            ):
                matched.append(file)


        # Canon
        elif (
            "canon" in q
            or "캐논" in q
        ):

            if (
                "canon" in target
                or "aquilion" in target
            ):
                matched.append(file)


        # GE
        elif (
            "ge" in q
            or "지이" in q
        ):

            if (
                "ge" in target
                or "revolution" in target
                or "vibe" in target
            ):
                matched.append(file)


        # Siemens
        elif (
            "siemens" in q
            or "지멘스" in q
        ):

            if (
                "siemens" in target
                or "somatom" in target
                or "pulse" in target
            ):
                matched.append(file)


        # Philips
        elif (
            "philips" in q
            or "필립스" in q
        ):

            if "philips" in target:
                matched.append(file)


    # 중복 제거
    matched = list(dict.fromkeys(matched))

    return matched


# =========================================================
# Mid High 비교표
# =========================================================

def parse_mid_high_table():

    rows = [

        [
            "Model",
            "Aquilion Serve SP",
            "SOMATOM X.CITE",
            "Revolution Ascend",
            "5300"
        ],

        [
            "Detector",
            "PUREViSION",
            "Stellarinfinity",
            "Gemstone",
            "NonoPannel Elite Detector"
        ],

        [
            "No. of slice per rotation",
            "160 slice",
            "128 slice",
            "128 slice",
            "128 slice"
        ],

        [
            "No. of detector rows",
            "80 rows",
            "64 rows",
            "64 rows",
            "64 rows"
        ],

        [
            "Width of detector rows",
            "0.5 mm",
            "0.6 mm",
            "0.625 mm",
            "0.625 mm"
        ],

        [
            "Max. Coverage of detector",
            "40 mm",
            "38.4 mm",
            "40 mm",
            "40 mm"
        ],

        [
            "Min. Slice thickness",
            "0.5 mm",
            "0.6 mm",
            "0.625 mm",
            "0.625 mm"
        ],

        [
            "Gantry aperture size",
            "80 cm",
            "82 cm",
            "75 cm",
            "72 cm"
        ],

        [
            "Min. Rotation time",
            "0.35 sec",
            "0.3 sec",
            "0.35 sec",
            "0.35 sec"
        ],

        [
            "Cooling Type",
            "Oil/Air",
            "Chilled water",
            "Oil/Air",
            "Oil/Air"
        ],

        [
            "Anode heat storage",
            "7.5 MHU",
            "0.6 MHU",
            "7.0 MHU",
            "8.0 MHU"
        ],

        [
            "Max. kVp Range",
            "135 kVp",
            "150 kVp",
            "140 kVp",
            "140 kVp"
        ],

        [
            "Max. mA Range",
            "600 mA",
            "1200 mA (option)",
            "600 mA",
            "667 mA"
        ],

        [
            "Scan Range",
            "180 cm",
            "160 cm",
            "170 cm",
            "185 cm"
        ],

        [
            "Min. table height",
            "33 cm",
            "33 cm",
            "45 cm",
            "45 cm"
        ],

        [
            "Max. table weight",
            "220 kg",
            "227 kg option",
            "227 kg",
            "227 kg"
        ],

        [
            "Noise reduction filter",
            "QDS+",
            "N/A",
            "4D noise reduction",
            "Provided"
        ],

        [
            "Metal artifact reduction",
            "SEMAR",
            "iMAR",
            "SMAR",
            "O MAR"
        ],

        [
            "Adaptive iterative dose reduction",
            "AIDR 3D Enhanced",
            "ADMIRE",
            "ASIR-V",
            "IMR"
        ],

        [
            "Auto kV selection",
            "SUREkV",
            "CARE kV",
            "kV Assist",
            "Right Dose Package"
        ],

        [
            "AI iterative reconstruction",
            "AiCE (All Parts)",
            "N/A",
            "TrueFidelity",
            "Precise image"
        ],

        [
            "AI Ultra High Resolution",
            "0.25mm PIQE 1024",
            "N/A",
            "ZeeFree / N/A",
            "SSF2 / Precise Cardiac"
        ],

        [
            "Image reconstruction time",
            "50 image/sec with AIDR 3D",
            "16~40 image/sec with ADMIRE",
            "65 image/sec with ASIR-V",
            "100 IPS with FBP"
        ],

        [
            "Cardiac navigation",
            "SURECardio",
            "Provided",
            "Provided",
            "Provided"
        ],

        [
            "Min. temporal resolution",
            "35 msec",
            "75 msec",
            "45 msec",
            "45 msec"
        ],

        [
            "Max. no. of segment",
            "5 segment",
            "2 segment",
            "4 segment",
            "4 segment"
        ],

        [
            "Auto Position",
            "3D Camera Built-in",
            "3D Camera 2EA option",
            "option",
            "option"
        ],

        [
            "Auto Planning",
            "3D Landmark Scan",
            "N/A",
            "N/A",
            "N/A"
        ],

        [
            "3D SCOUT View",
            "3D Landmark Scan",
            "N/A",
            "N/A",
            "N/A"
        ],

        [
            "ONE Click Subtraction",
            "SURESubtraction",
            "N/A",
            "N/A",
            "N/A"
        ],
    ]

    return pd.DataFrame(
        rows,
        columns=[
            "항목",
            "Canon",
            "Siemens",
            "GE",
            "Philips"
        ]
    )


# =========================================================
# 영업 지식 출력
# =========================================================

def show_sales_knowledge(results):

    st.subheader("🎯 영업 정보")

    current_product = None

    for result in results:

        if current_product != result["keyword"]:

            st.markdown(
                f"## {result['keyword']}"
            )

            current_product = result["keyword"]

        st.markdown(
            f"### {result['category']}"
        )

        for idx, answer in enumerate(
            result["answers"],
            start=1
        ):

            st.markdown(
                f"{idx}. {answer}"
            )


# =========================================================
# 파일 결과 출력
# =========================================================

def show_file_result(file):

    st.markdown(
        f"### 📄 {file.name}"
    )

    if file.suffix.lower() == ".pdf":

        if (
            "mid_high" in file.name.lower()
            or "serve" in file.name.lower()
        ):

            df = parse_mid_high_table()

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            text = read_pdf_text(file)

            st.text(
                text[:3000]
            )


    elif file.suffix.lower() == ".xlsx":

        df = read_excel_table(file)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# Search UI (original query/results retained; quick buttons are additive)
# =========================================================

if "search_question" not in st.session_state:
    st.session_state.search_question = ""

def set_quick_search(value):
    st.session_state.search_question = value

st.markdown('<div class="ct-heading">빠른 검색</div>', unsafe_allow_html=True)
menu_columns = st.columns(4)
menu_options = [
    ("제품 정보", "PRISM 셀링 포인트 알려줘"),
    ("경쟁사 비교", "미드하이 경쟁사 비교표"),
    ("정비 및 운영", "Serve 사양 알려줘"),
    ("현장 피드백", "GE VIBE CT 설치현황과 피드백 알려줘"),
]
for i, (label, query_text) in enumerate(menu_options):
    with menu_columns[i]:
        st.button(label, key=f"quick_menu_{i}", on_click=set_quick_search, args=(query_text,), use_container_width=True)

st.markdown('<div class="ct-heading">통합 검색</div>', unsafe_allow_html=True)

question = st.text_input(
    "질문을 입력하세요",
    key="search_question",
    placeholder=(
        "예: GE VIBE CT 설치현황과 피드백 알려줘 / "
        "프로펄스 피드백 알려줘 / "
        "PRISM 셀링 포인트 알려줘"
    )
)


if question:

    st.markdown(
        f"### 질문: {question}"
    )

    knowledge_results = find_sales_knowledge(
        question
    )

    matched_files = find_files(
        question
    )


    # 직접 입력된 영업 정보
    if knowledge_results:

        show_sales_knowledge(
            knowledge_results
        )


    # PDF / Excel 자료
    if matched_files:

        st.subheader(
            "📚 참고 자료"
        )

        st.success(
            f"관련 자료 {len(matched_files)}개를 찾았습니다."
        )

        for file in matched_files:

            show_file_result(
                file
            )


    # 아무것도 없는 경우
    if (
        not knowledge_results
        and not matched_files
    ):

        st.warning(
            "관련 자료 또는 영업 정보를 찾지 못했습니다."
        )