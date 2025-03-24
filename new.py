import streamlit as st
import numpy_financial as npf
import pandas as pd
from fpdf import FPDF
import numpy as np
import math
import io

# Function to calculate water volume
def calculate_water_volume(culture_type, species, yearly_production):
    if culture_type == "Intensive":
        culture_density = 80
    elif culture_type == "Semi-Intensive":
        culture_density = 60
    else:
        raise ValueError("Invalid culture type")

    if species == "Pabda":
        batch_per_year = 2.4
    elif species == "Gulsha":
        batch_per_year = 2.6
    else:
        raise ValueError("Invalid species")

    total_volume = yearly_production / (culture_density * batch_per_year)
    return round(total_volume, 2)

# Function to calculate payback period
def calculate_payback_period(cumulative_cash_flow):
    for year, cash in enumerate(cumulative_cash_flow):
        if cash >= 0:
            return year
    return None

# Function to print all results
def print_results(initial_investment, estimated_revenue, operational_cost, payback_period, irr, cash_flow_data, total_volume, tank_diameter, volume_per_tank):
    irr_display = "N/A"
    if irr is not None and not pd.isna(irr):
        irr_display = f"{irr:.2%}"

    report_text = (
        f"Initial Investment: {initial_investment:,.2f} BDT\n"
        f"Estimated Annual Revenue: {estimated_revenue:,.2f} BDT\n"
        f"Operational Cost per Year: {operational_cost:,.2f} BDT\n"
        f"Project Payback Period (Years): {payback_period if payback_period is not None else 'N/A'}\n"
        f"Internal Rate of Return (IRR): {irr_display}\n"
        f"Total Water Volume Required: {total_volume} m³\n"
        f"Tank Diameter: {tank_diameter} m\n"
        f"Total Volume per Tank: {volume_per_tank} m³\n"
    )

    st.markdown(
        """
        <style>
            .responsive-header h1 {
                color: green;
                text-decoration: underline;
                font-weight: bold;
                text-align: center;
                font-size: clamp(25px, 4vw, 35px);
                margin-bottom: 0px;
            }
        </style>
        <div class="responsive-header">
            <h1>Report Details</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.text_area("", report_text, height=300)

    st.subheader("Cash Flow Table")
    st.write(cash_flow_data)

    if st.button("Prepare Report"):
        pdf_buffer = generate_pdf_report(initial_investment, estimated_revenue, operational_cost, payback_period, irr, cash_flow_data, total_volume, tank_diameter, volume_per_tank)
        st.download_button(
            label="Download PDF Report",
            data=pdf_buffer.getvalue(),
            file_name="financial_report.pdf",
            mime="application/pdf"
        )

# Function to generate PDF report (professional look, more results, elaborated analysis)
def generate_pdf_report(initial_investment, estimated_revenue, operational_cost, payback_period, irr, cash_flow_data, total_volume, tank_diameter, volume_per_tank):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Page Border
    pdf.set_line_width(0.5)
    pdf.rect(5, 5, 200, 287)  # Border around entire page (210mm x 297mm - 5mm padding)

    # Title with Background
    pdf.set_fill_color(230, 230, 230)  # Light gray
    pdf.set_font("Times", 'B', size=14)
    pdf.cell(0, 10, txt="Cost-Benefit Analysis Report", ln=True, align="C", fill=True)
    pdf.ln(5)

    # Project Overview
    pdf.set_font("Times", 'B', size=12)
    pdf.cell(0, 7, txt="Project Overview", ln=True, align='L')
    pdf.set_font("Times", size=10)
    irr_display = "N/A" if (pd.isna(irr) or irr is None) else f"{round(irr * 100, 2)}%"
    annual_profit = estimated_revenue - operational_cost
    cash_flow = [-initial_investment] + [annual_profit] * (len(cash_flow_data) - 1)
    npv = round(npf.npv(0.10, cash_flow), 0)  # NPV at 10% discount rate
    report_text = (
        f"Investment: {initial_investment:,.0f} BDT  Revenue/Yr: {estimated_revenue:,.0f} BDT  Cost/Yr: {operational_cost:,.0f} BDT\n"
        f"Profit/Yr: {annual_profit:,.0f} BDT  Payback: {payback_period if payback_period is not None else 'N/A'} yrs  IRR: {irr_display}  NPV (10%): {npv:,.0f} BDT\n"
        f"Water: {total_volume} m³  Tank Dia.: {tank_diameter} m  Vol./Tank: {volume_per_tank} m³"
    )
    pdf.multi_cell(0, 5, report_text)
    pdf.ln(5)

    # Cash Flow Chart
    pdf.set_font("Times", 'B', size=12)
    pdf.cell(0, 7, txt="Cash Flow Chart", ln=True, align='L')
    pdf.set_font("Times", 'B', size=10)
    pdf.set_fill_color(240, 240, 240)  # Very light gray for table header
    pdf.cell(25, 6, "Year", border=1, align="C", fill=True)
    pdf.cell(40, 6, "Cash In", border=1, align="C", fill=True)
    pdf.cell(40, 6, "Cash Out", border=1, align="C", fill=True)
    pdf.cell(55, 6, "Cumulative CF", border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Times", size=10)
    for i, row in cash_flow_data.iterrows():
        pdf.cell(25, 5, str(int(row['Year'])), border=1, align="C")
        pdf.cell(40, 5, f"{int(row['Cash In']):,}", border=1, align="R")
        pdf.cell(40, 5, f"{int(row['Cash Out']):,}", border=1, align="R")
        pdf.cell(55, 5, f"{int(row['Cumulative Cash Flow']):,}", border=1, align="R")
        pdf.ln()
    pdf.ln(4)

    # Financial Analysis (Elaborated)
    pdf.set_font("Times", 'B', size=12)
    pdf.cell(0, 7, txt="Financial Analysis", ln=True)
    pdf.set_font("Times", size=10)
    if pd.isna(irr) or irr is None:
        analysis_text = "IRR unavailable; cash flows undefined. Profitability unclear."
    elif irr > 0.20:
        analysis_text = f"IRR {irr:.2%} exceeds 20%, signaling strong returns. Payback in {payback_period} yrs is swift, and NPV {npv:,.0f} BDT reflects high value."
    elif irr > 0.10:
        analysis_text = f"IRR {irr:.2%} offers solid returns above 10%. Payback in {payback_period} yrs is reasonable, with NPV {npv:,.0f} BDT showing positive value."
    else:
        analysis_text = f"IRR {irr:.2%} below 10% suggests modest returns. Payback in {payback_period if payback_period is not None else 'N/A'} yrs and NPV {npv:,.0f} BDT need scrutiny."
    pdf.multi_cell(0, 5, analysis_text)
    pdf.ln(4)

    # Conclusion
    pdf.set_font("Times", 'B', size=12)
    pdf.cell(0, 7, txt="Conclusion", ln=True)
    pdf.set_font("Times", size=10)
    if pd.isna(irr) or irr is None:
        conclusion_text = "Financial viability unclear due to undefined cash flows. More data is needed for assessment."
    elif irr > 0.20 and payback_period is not None and payback_period < 3:
        conclusion_text = "Highly promising project with strong returns and quick recovery. Ideal for investment with minimal risk."
    elif irr <= 0.10 or (payback_period is not None and payback_period > 5):
        conclusion_text = "Low IRR or long payback indicates risks. Consider cost reduction or revenue enhancement strategies."
    else:
        conclusion_text = "Moderate viability with decent returns by 2030. Positive NPV suggests value, but review market trends and costs before proceeding."
    pdf.multi_cell(0, 5, conclusion_text)

    pdf_buffer = io.BytesIO()
    pdf.output(dest='F', name=pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

# Streamlit App Setup
st.markdown("""
    <style>
        .responsive-header h1 {
            text-decoration: underline;
            font-weight: bold;
            text-align: center;
            font-size: clamp(25px, 4vw, 35px);
        }
        .responsive-header h2 {
            text-align: center;
            font-size: clamp(20px, 2.5vw, 25px);
        }
    </style>
    <div class="responsive-header">
        <h1>Cost-Benefit Analysis Tool</h1>
        <h2>Developed by ITTI</h2>
    </div>
""", unsafe_allow_html=True)

# Session State Initialization
if "current_section" not in st.session_state:
    st.session_state.current_section = "Project Plan"
if "plan_data" not in st.session_state:
    st.session_state.plan_data = {
        "culture_type": "Intensive",
        "species": "Pabda",
        "yearly_production": 10000.0,
        "tank_number": 6,
        "year_of_investment": 2025,
    }
if "financial_data" not in st.session_state:
    st.session_state.financial_data = {
        "initial_investment": 5000000.0,
        "equipment_cost": 2000000.0,
        "land_cost": 1500000.0,
        "infrastructure_cost": 1000000.0,
        "construction_labor_cost": 500000.0,
        "electricity_cost": 438000.0,
        "selling_price": 400.0,
        "fcr": 1.5,
        "salary_payment": 600000.0,
        "maintenance_cost": 240000.0,
        "marketing_cost": 180000.0,
        "fingerlings_cost": 2.5,
        "feed_cost_per_kg": 60.0,
        "project_lifetime": 10,
    }

# Sidebar Navigation
with st.sidebar:
    st.markdown('<h1 style="color:green; text-decoration:underline; font-weight:bold;">ITTI-BCSIR</h1>', unsafe_allow_html=True)
    st.subheader(":green[Quick navigation]")
    if st.button("Project Plan"):
        st.session_state.current_section = "Project Plan"
    if st.button("Financial Information"):
        st.session_state.current_section = "Financial Information"
    if st.button("Results"):
        st.session_state.current_section = "Results"

# Project Plan Section
if st.session_state.current_section == "Project Plan":
    st.header("Project Plan")
    st.session_state.plan_data["culture_type"] = st.selectbox(
        "Select Culture Type", ["Intensive", "Semi-Intensive"], index=["Intensive", "Semi-Intensive"].index(st.session_state.plan_data["culture_type"])
    )
    st.session_state.plan_data["species"] = st.selectbox(
        "Select Fish Species", ["Pabda", "Gulsha"], index=["Pabda", "Gulsha"].index(st.session_state.plan_data["species"])
    )
    st.session_state.plan_data["yearly_production"] = st.number_input(
        "Desired Yearly Production (kg)", min_value=0.0, value=st.session_state.plan_data["yearly_production"], step=100.0
    )
    st.session_state.plan_data["tank_number"] = st.number_input(
        "Number of Tanks", min_value=1, max_value=20, value=st.session_state.plan_data["tank_number"], step=1
    )
    st.session_state.plan_data["year_of_investment"] = st.selectbox(
        "Year of Investment", [2025, 2026, 2027, 2028], index=[2025, 2026, 2027, 2028].index(st.session_state.plan_data["year_of_investment"])
    )
    if st.button("Next - Financial Information"):
        st.session_state.current_section = "Financial Information"

# Financial Information Section
if st.session_state.current_section == "Financial Information":
    st.header("Financial Information")
    st.subheader("Investment Costs")
    st.session_state.financial_data["equipment_cost"] = st.number_input(
        "Equipment Cost (BDT)", min_value=0.0, value=st.session_state.financial_data["equipment_cost"], step=10000.0
    )
    st.session_state.financial_data["land_cost"] = st.number_input(
        "Land Cost (BDT)", min_value=0.0, value=st.session_state.financial_data["land_cost"], step=10000.0
    )
    st.session_state.financial_data["infrastructure_cost"] = st.number_input(
        "Infrastructure Cost (BDT)", min_value=0.0, value=st.session_state.financial_data["infrastructure_cost"], step=10000.0
    )
    st.session_state.financial_data["construction_labor_cost"] = st.number_input(
        "Construction Labor Cost (BDT)", min_value=0.0, value=st.session_state.financial_data["construction_labor_cost"], step=10000.0
    )

    st.subheader("Operational Costs")
    electric_load_kwh = st.number_input("Electric Load Requirement (kW)", min_value=0.0, value=6.0, step=1.0)
    hours_per_day, days_per_year = 20, 365
    yearly_electricity_demand = electric_load_kwh * hours_per_day * days_per_year
    electricity_rate = st.number_input("Electricity Rate (BDT per kWh)", min_value=0.0, value=10.0, step=0.5)
    electricity_cost = yearly_electricity_demand * electricity_rate

    monthly_marketing_cost = st.number_input("Monthly Marketing Cost (BDT)", min_value=0.0, value=st.session_state.financial_data["marketing_cost"] / 12, step=1000.0)
    marketing_cost = monthly_marketing_cost * 12

    monthly_maintenance_cost = st.number_input("Monthly Maintenance Cost (BDT)", min_value=0.0, value=st.session_state.financial_data["maintenance_cost"] / 12, step=1000.0)
    maintenance_cost = monthly_maintenance_cost * 12

    fingerlings_cost = st.number_input("Fingerling Cost per Piece (BDT)", min_value=0.0, value=st.session_state.financial_data["fingerlings_cost"], step=0.5)
    fingerling_quantity = (st.session_state.plan_data["yearly_production"] * 1000) / 40
    total_fingerling_cost = fingerlings_cost * fingerling_quantity

    st.subheader("Feed Cost")
    fcr = st.number_input("Feed Conversion Ratio (FCR)", min_value=0.0, value=st.session_state.financial_data["fcr"], step=0.1)
    feed_cost_per_kg = st.number_input("Feed Cost per kg (BDT)", min_value=0.0, value=st.session_state.financial_data["feed_cost_per_kg"], step=1.0)
    yearly_feed_requirement = fcr * st.session_state.plan_data["yearly_production"]
    feed_cost = yearly_feed_requirement * feed_cost_per_kg

    st.subheader("Revenue Inputs")
    selling_price = st.number_input("Selling Price per Unit (BDT)", min_value=0.0, value=st.session_state.financial_data["selling_price"], step=5.0)

    salary_payment = st.number_input("Employee Salary per Year (BDT)", min_value=0.0, value=st.session_state.financial_data["salary_payment"], step=10000.0)
    project_lifetime = st.number_input("Project Lifetime (Years)", min_value=1, value=st.session_state.financial_data["project_lifetime"], step=1)

    if st.button("Next - Results"):
        st.session_state.financial_data.update({
            "electricity_cost": electricity_cost,
            "marketing_cost": marketing_cost,
            "maintenance_cost": maintenance_cost,
            "fingerlings_cost": fingerlings_cost,
            "total_fingerling_cost": total_fingerling_cost,
            "fcr": fcr,
            "feed_cost_per_kg": feed_cost_per_kg,
            "feed_cost": feed_cost,
            "selling_price": selling_price,
            "salary_payment": salary_payment,
            "project_lifetime": project_lifetime
        })
        st.session_state.current_section = "Results"

# Results Section
if st.session_state.current_section == "Results":
    initial_investment = (
        st.session_state.financial_data["equipment_cost"] +
        st.session_state.financial_data["land_cost"] +
        st.session_state.financial_data["infrastructure_cost"] +
        st.session_state.financial_data["construction_labor_cost"]
    )

    fingerling_quantity = (st.session_state.plan_data["yearly_production"] * 1000) / 40
    total_fingerling_cost = st.session_state.financial_data["fingerlings_cost"] * fingerling_quantity
    yearly_feed_requirement = st.session_state.financial_data["fcr"] * st.session_state.plan_data["yearly_production"]
    feed_cost = yearly_feed_requirement * st.session_state.financial_data["feed_cost_per_kg"]

    operational_cost = (
        st.session_state.financial_data["electricity_cost"] +
        st.session_state.financial_data["marketing_cost"] +
        st.session_state.financial_data["maintenance_cost"] +
        total_fingerling_cost +
        feed_cost +
        st.session_state.financial_data["salary_payment"]
    )
    revenue = st.session_state.plan_data["yearly_production"] * st.session_state.financial_data["selling_price"]

    cash_flow = [-initial_investment] + [revenue - operational_cost for _ in range(st.session_state.financial_data["project_lifetime"] - 1)]
    cumulative_cash_flow = [sum(cash_flow[:i+1]) for i in range(len(cash_flow))]
    irr = npf.irr(cash_flow)
    payback_period = calculate_payback_period(cumulative_cash_flow)

    total_volume = calculate_water_volume(
        st.session_state.plan_data["culture_type"],
        st.session_state.plan_data["species"],
        st.session_state.plan_data["yearly_production"]
    )
    tank_height, water_height = 1.5, 1.2
    tank_diameter = round(math.sqrt(total_volume * 4 / (3.1416 * water_height)), 2)
    final_water_volume = round((3.1416 * tank_diameter * tank_diameter * tank_height / 4), 2)
    volume_per_tank = round(final_water_volume / st.session_state.plan_data["tank_number"], 2)

    years = [st.session_state.plan_data["year_of_investment"] + i for i in range(st.session_state.financial_data["project_lifetime"])]
    cash_flow_df = pd.DataFrame({
        "Year": years,
        "Cash In": [0] + [revenue] * (st.session_state.financial_data["project_lifetime"] - 1),
        "Cash Out": [initial_investment] + [operational_cost] * (st.session_state.financial_data["project_lifetime"] - 1),
        "Cumulative Cash Flow": cumulative_cash_flow
    })

    print_results(initial_investment, revenue, operational_cost, payback_period, irr, cash_flow_df, total_volume, tank_diameter, volume_per_tank)
