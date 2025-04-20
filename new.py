import streamlit as st
import numpy_financial as npf
import pandas as pd
from fpdf2 import FPDF  # Updated import
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
    pdf.set_font("Times
