import streamlit as st
import pandas as pd
from streamlit_tree_select import tree_select

st.set_page_config(page_title="Quotation Selector", layout="wide")
st.title("📋 Vehicle Quotation Builder")

# Upload the Excel file
uploaded_file = st.file_uploader("📂 Upload your master Excel file", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.dropna(subset=["Institution Name", "regNo", "vehicleInsuranceUpto"], inplace=True)

        # Build tree structure
        tree_nodes = [{"label": "All Institutions & Buses", "value": "all_data", "children": []}]
        institutions = df.groupby("Institution Name")
        for inst_name, group in institutions:
            vehicle_nodes = [
                {
                    "label": f"{row['regNo']} (Valid upto {pd.to_datetime(row['vehicleInsuranceUpto']).date()})",
                    "value": f"bus::{inst_name}::{row['regNo']}"
                }
                for _, row in group.iterrows()
            ]
            inst_node = {
                "label": inst_name,
                "value": f"institution::{inst_name}",
                "children": vehicle_nodes
            }
            tree_nodes[0]["children"].append(inst_node)

        # Create two-column layout
        col1, col2 = st.columns([1, 2])

        with col1:
            selection = tree_select(nodes=tree_nodes)
            st.subheader("📄 Select components to include")
            components = st.multiselect(
                "Choose sections to generate:",
                ["Covering Letter", "Quotation Cards", "Client List (pre-made)"],
                default=["Quotation Cards"]
            )

        with col2:
            if "all_data" in selection.get("checked", []):
                with st.expander("📊 Summary of All Institutions"):
                    st.markdown(f"""
                    <div style='padding:15px; background:linear-gradient(to right, #f0f4ff, #f9f9f9); border:1px solid #ccc; border-radius:10px; box-shadow:2px 2px 8px rgba(0,0,0,0.05); margin-bottom:15px;'>
                        <h4 style='margin-top:0;'>📘 Summary for All Institutions</h4>
                        <ul style='list-style: none; padding-left: 0;'>
                            <li>🚍 <b>Total Vehicles:</b> {len(df)}</li>
                            <li>🏫 <b>Total Institutions:</b> {df['Institution Name'].nunique()}</li>
                            <li>💵 <b>Total IDV:</b> ₹{df['IDV'].sum():,.2f}</li>
                            <li>📑 <b>Net Premium:</b> ₹{df['Net_Premium'].sum():,.2f}</li>
                            <li>🧾 <b>GST:</b> ₹{df['GST_Amount'].sum():,.2f}</li>
                            <li>💰 <b>Advance Paid:</b> ₹{df['Adv_Paid'].sum():,.2f}</li>
                            <li>🔚 <b>Final Payable:</b> ₹{df['Final_Amount'].sum():,.2f}</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    st.dataframe(df[["regNo", "vehicleInsuranceUpto"]].head(10))

            for val in selection.get("checked", []):
                if val.startswith("institution::"):
                    _, inst = val.split("::")
                    inst_df = df[df["Institution Name"] == inst]
                    if not inst_df.empty:
                        st.markdown(f"""
                        <div style='padding:15px; background:linear-gradient(to right, #f0f4ff, #f9f9f9); border:1px solid #ccc; border-radius:10px; box-shadow:2px 2px 8px rgba(0,0,0,0.05); margin-bottom:15px;'>
                            <h4 style='margin-top:0;'>📘 Summary for {inst}</h4>
                            <ul style='list-style: none; padding-left: 0;'>
                                <li>🚍 <b>Total Vehicles:</b> {len(inst_df)}</li>
                                <li>💵 <b>Total IDV:</b> ₹{inst_df['IDV'].sum():,.2f}</li>
                                <li>📑 <b>Net Premium:</b> ₹{inst_df['Net_Premium'].sum():,.2f}</li>
                                <li>🧾 <b>GST:</b> ₹{inst_df['GST_Amount'].sum():,.2f}</li>
                                <li>💰 <b>Advance Paid:</b> ₹{inst_df['Adv_Paid'].sum():,.2f}</li>
                                <li>🔚 <b>Final Payable:</b> ₹{inst_df['Final_Amount'].sum():,.2f}</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)

            for val in selection.get("checked", []):
                if val.startswith("bus::"):
                    _, inst, reg = val.split("::")
                    vehicle_row = df[(df["Institution Name"] == inst) & (df["regNo"] == reg)]
                    if not vehicle_row.empty:
                        row = vehicle_row.iloc[0]
                        st.markdown(f"""
                        <div style='padding:15px; margin:10px 0; border-radius:12px; border:1px solid #ccc; background:#f9f9f9;'>
                            <h4>🚐 Vehicle: {row['regNo']}</h4>
                            🪑 <b>Seating Capacity:</b> {row.get('vehicleSeatCapacity', 'N/A')}<br>
                            🛠️ <b>Model:</b> {row.get('model', 'N/A')}<br>
                            🏭 <b>Manufacturer:</b> {row.get('vehicleManufacturerName', 'N/A')}<br>
                            🏢 <b>Previous Insurer:</b> {row.get('vehicleInsuranceCompanyName', 'N/A')}<br>
                            📆 <b>Insurance Expiry:</b> {pd.to_datetime(row.get('vehicleInsuranceUpto')).date()}<br>
                            💰 <b>Net Premium:</b> ₹{row.get('Net_Premium', 0):,.2f}<br>
                            🧾 <b>GST:</b> ₹{row.get('GST_Amount', 0):,.2f}<br>
                            🔚 <b>Final Amount:</b> ₹{row.get('Final_Amount', 0):,.2f}
                        </div>
                        """, unsafe_allow_html=True)

            # Move the Generate button to the right column
            if st.button("🧾 Generate Quotation PDF"):
                st.success("✅ Ready to invoke generate_quotation_pdf() based on selected components!")
                # PDF generation logic goes here

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.warning("📥 Please upload your Excel master file to begin.")
