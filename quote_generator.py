from pdf_generator import generate_quotation_pdf
from covering_letter_fpdf import LetterPDF
from PyPDF2 import PdfMerger
import os
import time
import streamlit as st
import pandas as pd
from config import header_path, footer_path, logo_path, client_list_path

def generate_quotation_batch(master_df, selected_institutions, components, uploaded_filename,partner_info,
                             header_path=header_path, footer_path=footer_path, logo_path=logo_path, client_list_path=client_list_path):

    start_time = time.time()
    checked_items = selected_institutions.get("checked", [])
    print(f"Selected Institutions: {selected_institutions}")

    # Extract unique institution names from selected items
    institutions = list({
        item.split("::")[1]
        for item in checked_items
        if item.startswith("institution::") or item.startswith("bus::")
    })

    output_dir = "generated_quotations"
    os.makedirs(output_dir, exist_ok=True)

    for inst_name in institutions:
        # Get regNos selected for this institution
        selected_regnos = [
            item.split("::")[2]
            for item in checked_items
            if item.startswith("bus::") and item.split("::")[1] == inst_name
        ]

        inst_df = master_df[
            (master_df["Institution Name"] == inst_name) &
            (master_df["regNo"].isin(selected_regnos))
        ]

        print(f"\n🔍 Checking institution: {inst_name}, Records found: {len(inst_df)}")

        if inst_df.empty:
            print(f"❌ No records found for: {inst_name}")
            continue

        institution_info = {
            "name": inst_name,
            "owner": inst_df.iloc[0].get("owner", "Manager"),
            "address": inst_df.iloc[0].get("Institution Address", "")
        }

        base_filename = os.path.splitext(os.path.basename(str(uploaded_filename)))[0]
        final_filename = f"{inst_name}_{base_filename}_quotation.pdf"
        final_path = os.path.join(output_dir, final_filename)

        print(f"📝 Generating quotation for: {inst_name} → {final_filename}")

        temp_files = []
        merger = PdfMerger()
        print(components)
        # Component 1: Covering Letter
        if "Covering Letter" in components:
            letter_pdf_path = os.path.join(output_dir, f"{inst_name}_{base_filename}_covering_letter.pdf")
            letter_pdf = LetterPDF(partner_info, header_path=header_path, footer_path=footer_path)
            letter_pdf.add_page()
            letter_pdf.add_intro(institution_info["name"], institution_info["owner"], institution_info["address"])
            letter_pdf.add_letter_body()
            letter_pdf.output(letter_pdf_path, dest='F')
            if os.path.exists(letter_pdf_path) and os.path.getsize(letter_pdf_path) > 0:
                merger.append(letter_pdf_path)
                temp_files.append(letter_pdf_path)
            else:
                print(f"⚠️ Skipping empty/missing letter: {letter_pdf_path}")

        # Component 2: Quotation
        if "Quotation Cards" in components:
            quote_pdf_path = os.path.join(output_dir, f"{inst_name}_{base_filename}_quotation_details.pdf")
            generate_quotation_pdf(
                data=inst_df,
                institution_info=institution_info,
                partner_info=partner_info,
                output_path=quote_pdf_path,
                header_path=header_path,
                footer_path=footer_path,
                logo_path=logo_path
            )
            if os.path.exists(quote_pdf_path) and os.path.getsize(quote_pdf_path) > 0:
                merger.append(quote_pdf_path)
                temp_files.append(quote_pdf_path)
            else:
                print(f"⚠️ Skipping empty/missing quotation: {quote_pdf_path}")

        # Component 3: Client List
        if "Client List" in components and client_list_path:
            if os.path.exists(client_list_path) and os.path.getsize(client_list_path) > 0:
                merger.append(client_list_path)
            else:
                print(f"⚠️ Skipping empty/missing client list: {client_list_path}")

        # Write final merged file
        print(f"📝 Attempting to save PDF to {final_path}")
        merger.write(final_path)
        merger.close()
        print(f"✅ Successfully saved PDF to {final_path}")

        # Clean up temp files
        for file in temp_files:
            try:
                os.remove(file)
            except Exception as e:
                print(f"⚠️ Could not delete temp file {file}: {e}")

        print(f"🎉 Quotation generation completed for: {inst_name}\n")

    end_time = time.time()
    elapsed = end_time - start_time

    st.success ( f"✅ Quotation generated successfully in {elapsed:.2f} seconds." )
"""
from pdf_generator import generate_quotation_pdf
from covering_letter_fpdf import LetterPDF
from PyPDF2 import PdfMerger
import os
import pandas as pd
from config import header_path, footer_path, logo_path, client_list_path

def generate_quotation_batch(master_df, selected_institutions,components,uploaded_filename,
                             header_path=header_path, footer_path=footer_path, logo_path=logo_path, client_list_path=client_list_path):

    checked_items = selected_institutions.get("checked", [])
    print(f"Slected Institutions: {selected_institutions}")

    # Extract unique institution names
    institutions = list({item.split("::")[1] for item in checked_items if item.startswith("institution::") or item.startswith("bus::")})

    for inst_name in institutions:
        inst_df = master_df[master_df["Institution Name"] == inst_name]

        print(f"🔍 Checking institution: {inst_name}, Records found: {len(inst_df)}")
        if inst_df.empty:
            print(f"❌ No data found for: {inst_name}")
            continue

        filename = f"{inst_name}_{uploaded_filename}_quotation.pdf"
        output_path = os.path.join("generated_quotations", filename)

        institution_info = {
            "name": inst_name,
            "address": inst_df["Institution Address"].iloc[0],
            "owner": inst_df["owner"].iloc[0]
        }

        print(f"📝 Generating quotation for: {inst_name} → {filename}")
        generate_quotation_pdf(inst_df, institution_info, output_path,
                               header_path, footer_path, logo_path)

        print(f"🎉 Quotation generation completed for: {inst_name}")

"""