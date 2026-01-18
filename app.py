import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns

# --- OS별 한글 폰트 자동 설정 ---
def set_korean_font():
    # 1. 시스템에 설치된 전체 폰트 목록 로드
    font_names = [f.name for f in fm.fontManager.ttflist]
    
    # 2. 환경별 최적의 폰트 순차적 적용
    if 'NanumGothic' in font_names:          # Streamlit Cloud (Linux)
        plt.rc('font', family='NanumGothic')
    elif 'Malgun Gothic' in font_names:      # Windows
        plt.rc('font', family='Malgun Gothic')
    elif 'AppleGothic' in font_names:        # Mac
        plt.rc('font', family='AppleGothic')
    else:
        # 폰트를 못 찾을 경우 기본 폰트라도 설정 (ㅁㅁ 방지 시도)
        st.warning("시스템에서 한글 폰트를 찾을 수 없어 차트 글자가 깨질 수 있습니다.")

    # 마이너스 기호 깨짐 방지
    plt.rc('axes', unicode_minus=False)

set_korean_font()

def main():
    # 페이지 설정
    st.set_page_config(page_title="연말정산 쉽게 이해하기", layout="wide")

    # 사이드바 메뉴
    st.sidebar.title("📌 메뉴")
    menu = st.sidebar.radio("이동할 항목을 선택하세요", ["연말정산이란?", "세율 및 구조 시각화", "간이 시뮬레이터"])

    # 제목 부분
    st.title("🔍 국세청 자료 기반: 연말정산 가이드 대시보드")
    st.caption("참고: 국세청 연말정산의 이해 (https://www.nts.go.kr)")

    if menu == "연말정산이란?":
        st.header("1. 연말정산 정의 및 흐름")
        st.info("""
        **연말정산이란?** 급여 지급 시 원천징수했던 세액과 실제 1년간의 최종 산출 세액을 비교하여,  
        많이 냈으면 돌려받고(환급), 적게 냈으면 추가로 내는(추징) 절차입니다.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 주요 계산 단계")
            # 복잡한 계산식은 LaTeX를 활용해 가독성을 높였습니다.
            st.markdown(r"""
            1. **근로소득금액** = 총급여액 - 근로소득공제
            2. **과세표준** = 근로소득금액 - 인적공제/소득공제
            3. **산출세액** = 과세표준 $\times$ 세율
            4. **결정세액** = 산출세액 - 세액감면/공제
            """)
        
        with col2:
            steps = pd.DataFrame({
                "단계": ["총급여액", "소득공제 후", "세율 적용 후", "세액공제 후"],
                "금액 수준": [100, 70, 40, 30]
            })
            fig, ax = plt.subplots(figsize=(5, 3))
            sns.barplot(data=steps, x="단계", y="금액 수준", palette="Blues_d", ax=ax)
            ax.set_title("세금이 줄어드는 과정 (예시)")
            st.pyplot(fig)

    elif menu == "세율 및 구조 시각화":
        st.header("2. 소득 구간별 기본 세율 시각화")
        tax_data = {
            "과세표준 구간": ["1,400만원 이하", "5,000만원 이하", "8,800만원 이하", "1.5억원 이하", "3억원 이하", "5억원 이하", "10억원 이하", "10억원 초과"],
            "세율(%)": [6, 15, 24, 35, 38, 40, 42, 45]
        }
        df_tax = pd.DataFrame(tax_data)
        st.table(df_tax)

        st.subheader("📈 과세표준 구간별 세율 변화")
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=df_tax, x="과세표준 구간", y="세율(%)", marker="o", color="red", ax=ax)
        ax.set_ylim(0, 50)
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.6)
        st.pyplot(fig)

    elif menu == "간이 시뮬레이터":
        st.header("3. 나의 연말정산 간이 시뮬레이션")
        col1, col2 = st.columns(2)
        with col1:
            salary = st.number_input("연간 총급여 (원)", min_value=0, value=50000000, step=1000000)
            deduction = st.number_input("예상 소득공제 합계 (원)", min_value=0, value=15000000, step=500000)
            tax_credit = st.number_input("예상 세액공제 합계 (원)", min_value=0, value=1000000, step=100000)

        # 간단한 산식 적용
        taxable_income = max(0, salary - deduction)
        def calculate_tax(income):
            if income <= 14000000: return income * 0.06
            elif income <= 50000000: return 840000 + (income - 14000000) * 0.15
            elif income <= 88000000: return 6240000 + (income - 50000000) * 0.24
            else: return 15360000 + (income - 88000000) * 0.35

        calculated_tax = calculate_tax(taxable_income)
        final_tax = max(0, calculated_tax - tax_credit)

        with col2:
            st.metric("예상 과세표준", f"{taxable_income:,.0f} 원")
            st.metric("예상 산출세액", f"{calculated_tax:,.0f} 원")
            st.success(f"최종 결정세액: {final_tax:,.0f} 원")

        st.subheader("💰 급여 대비 세금 비중")
        remaining = salary - final_tax
        labels = ['결정세액', '실수령액(예상)']
        sizes = [final_tax, remaining]
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff'])
        ax2.axis('equal') 
        st.pyplot(fig2)

if __name__ == "__main__":
    main()