import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from download_utils import list_pdfs, read_bytes , zip_bytes
from streamlit_tree_select import tree_select
from data_loader import load_and_clean_data
from tree_builder import build_tree_nodes
from quote_generator import generate_quotation_batch
from partner_selector import PartnerSelector

st.set_page_config(page_title="Quotation Generator", layout="wide")
st.title("📋 EIB Quotation Generator")

# Upload the Excel file
uploaded_file = st.file_uploader("📂 Upload your master Excel file", type=["xlsx"])
#uploaded_file_name = uploaded_file.name if uploaded_file is not None else "Uploaded"

if uploaded_file:
    try:
        df = load_and_clean_data(uploaded_file)

        # Build tree structure using external utility
        tree_nodes = build_tree_nodes(df)

        # Create two-column layout
        col1, col2 = st.columns([1, 2])

        with col1:
            selection = tree_select(nodes=tree_nodes)
            st.subheader("📄 Select components to include")
            components = st.multiselect(
                "Choose sections to generate:",
                ["Covering Letter", "Quotation Cards", "Client List"],
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

            selector = PartnerSelector ( "partners.xlsx" )
            partner_info = selector.render ( )

            if partner_info :
                st.write ( "Proceed with quotation generation..." )

            OUTPUT_DIR = Path ( "generated_quotations" )  # change if your code uses a different folder
            OUTPUT_DIR.mkdir ( parents=True , exist_ok=True )

            if "last_run_files" not in st.session_state :
                st.session_state.last_run_files = [ ]

            # Move the Generate button to the right column
            if st.button("🧾 Generate Quotation PDF"):
                print(uploaded_file.name)
                # app.py (inside the "Generate" button block)
                before = list_pdfs ( OUTPUT_DIR )

                # 2) Call your EXISTING generator exactly as-is
                #    (do not reimplement cover letter / quotation code)
                try :
                    result = generate_quotation_batch (
                        df ,  # your prepared dataframe
                        selection ,  # your selected institutions from tree
                        components ,  # ["Covering Letter", "Quotation Cards", "Client List"] etc
                        uploaded_file.name ,
                        partner_info ,  # your existing partner selector output
                    )
                except Exception as e :
                    st.error ( f"Generation failed: {e}" )
                    result = None

                # 3) Snapshot after generation and compute the new files
                after = list_pdfs ( OUTPUT_DIR )
                new_files = sorted ( after - before , key=lambda p : p.stat ( ).st_mtime , reverse=True )

                # 4) Prefer paths returned by your generator if it returns them
                #    (keeps names exact and allows including client list if it lives elsewhere)
                if isinstance ( result , dict ) and result.get ( "all_files" ) :
                    files = [ Path ( p ) for p in result [ "all_files" ] if Path ( p ).exists ( ) ]
                else :
                    files = new_files  # fallback: use diff of the output folder

                st.session_state.last_run_files = files

                if files :
                    st.success ( f"✅ Generated {len ( files )} file(s). Ready to download." )
                else :
                    st.warning ( "No new PDFs detected. Check OUTPUT_DIR or your component selections." )

            # --- Downloads panel (works even after rerun) ---
            st.divider ( )
            st.subheader ( "⬇️ Downloads" )

            files = st.session_state.last_run_files
            if not files :
                st.caption ( "Generate to populate downloads." )
            else :
                # Bulk ZIP option
                labels = [
                    f"{p.name}  ·  {datetime.fromtimestamp ( p.stat ( ).st_mtime ).strftime ( '%d-%m-%Y %H:%M' )}" for p
                    in files ]
                pick = st.multiselect ( "Select files to bundle as ZIP" , labels , default=labels )
                label_map = dict ( zip ( labels , files ) )
                sel = [ label_map [ x ] for x in pick ]

                if sel :
                    zipbuf = zip_bytes ( sel )
                    st.download_button (
                        "📦 Download selected as ZIP" ,
                        data=zipbuf ,
                        file_name=f"quotations_{datetime.now ( ).strftime ( '%Y%m%d_%H%M%S' )}.zip" ,
                        mime="application/zip" ,
                        use_container_width=True
                    )

                st.markdown ( "**Or download individually:**" )
                for p in files :
                    with st.container ( border=True ) :
                        c1 , c2 = st.columns ( [ 4 , 1 ] )
                        with c1 :
                            st.write ( f"**{p.name}**" )
                            st.caption ( str ( p ) )
                        with c2 :
                            st.download_button (
                                "Download" ,
                                data=read_bytes ( p ) ,
                                file_name=p.name ,
                                mime="application/pdf" ,
                                key=f"dl-{p.name}-{p.stat ( ).st_mtime}"
                            )
    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.warning("📥 Please upload your Excel master file to begin.")
