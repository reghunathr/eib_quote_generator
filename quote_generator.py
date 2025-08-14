# quote_generator.py
from pathlib import Path
import time
import pandas as pd
import streamlit as st

from PyPDF2 import PdfMerger, PdfReader
from pdf_generator import generate_quotation_pdf
from covering_letter_fpdf import generate_covering_letter_pdf
from config import header_path, footer_path, logo_path, client_list_path


# ---------- helpers ----------
def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def _safe_name(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        return "Institution"
    s = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in name).strip()
    return (s or "Institution").replace(" ", "_")

def _ts() -> str:
    # millisecond timestamp to avoid collisions when generating many PDFs quickly
    return str(int(time.time() * 1000))

def _is_valid_pdf(p: Path) -> bool:
    try:
        with open(p, "rb") as fh:
            PdfReader(fh, strict=False)  # pre-validate before appending
        return True
    except Exception as e:
        st.warning(f"Skipping invalid PDF '{p.name}': {e}")
        return False
# ------------------------------


def generate_quotation_batch(
    master_df: pd.DataFrame,
    selected_institutions: dict,
    components: list[str],
    uploaded_filename: str,
    partner_info: dict,
    header_path: str = header_path,
    footer_path: str = footer_path,
    logo_path: str = logo_path,
    client_list_path: str = client_list_path,
):
    """
    Generates PDFs and RETURNS file paths for download.
    - Covering Letter is generated PER SCHOOL (named with school).
    - Quotation is generated PER SCHOOL.
    - Clients List is included as-is (if selected).
    - MERGE happens ONLY IF all three components are selected together:
        {"Covering Letter", "Quotation Cards", "Client List"} ⊆ components

    Returns:
        {
          "covering_letters": list[Path],
          "quotations": list[Path],
          "merged_packs": list[Path],         # per-school Combined PDFs (if merge condition met)
          "client_list": Path | None,
          "all_files": list[Path],
          "out_dir": Path,
          "elapsed_sec": float
        }
    """
    start_time = time.time()
    out_dir = Path("generated_quotations")
    _ensure_dir(out_dir)

    checked_items = (selected_institutions or {}).get("checked", []) or []

    # Institutions referenced in tree selection (institution::<name> or bus::<name>::<regNo>)
    institutions = list({
        item.split("::")[1]
        for item in checked_items
        if item.startswith("institution::") or item.startswith("bus::")
    })

    covering_letters: list[Path] = []
    quotations: list[Path] = []
    merged_packs: list[Path] = []
    client_added_path: Path | None = None

    # Is merge requested? Only when *all three* components are selected together.
    merge_enabled = {"Covering Letter", "Quotation Cards", "Client List"}.issubset(set(components or []))

    # Generate per-school outputs
    for inst_name in institutions:
        # Buses explicitly selected under this institution
        selected_regnos = [
            item.split("::")[2]
            for item in checked_items
            if item.startswith("bus::") and item.split("::")[1] == inst_name
        ]

        if selected_regnos:
            inst_df = master_df[
                (master_df["Institution Name"] == inst_name)
                & (master_df["regNo"].isin(selected_regnos))
            ]
        else:
            # If no buses chosen under the institution, use all rows for that institution
            inst_df = master_df[master_df["Institution Name"] == inst_name]

        if inst_df.empty:
            st.warning(f"No records found for: {inst_name}")
            continue

        safe = _safe_name(inst_name)
        tag = _ts()

        # Shared info for generators
        institution_info = {
            "name": inst_name,
            "owner": inst_df.iloc[0].get("owner", "Manager"),
            "address": inst_df.iloc[0].get("Institution Address", ""),
        }

        # 1) Covering Letter (per school, named with school)
        cover_path: Path | None = None
        if "Covering Letter" in (components or []):
            cover_path = out_dir / f"Covering_Letter_{safe}_{tag}.pdf"
            try:
                generate_covering_letter_pdf(inst_df,
                    institution_info=institution_info,
                    partner_info=partner_info,
                    output_path=str(cover_path),
                    header_path=header_path,
                    footer_path=footer_path,
                    logo_path=logo_path,
                )
                if cover_path.exists() and cover_path.stat().st_size > 0:
                    covering_letters.append(cover_path)
                else:
                    st.warning(f"Covering letter empty for: {inst_name}")
                    cover_path = None
            except Exception as e:
                st.warning(f"Covering letter generation failed for {inst_name}: {e}")
                cover_path = None

        # 2) Quotation PDF (per school)
        quote_path: Path | None = None
        if "Quotation Cards" in (components or []):
            quote_path = out_dir / f"Quotation_{safe}_{tag}.pdf"
            try:
                generate_quotation_pdf(
                    inst_df,
                    institution_info,
                    partner_info=partner_info,
                    output_path=str(quote_path),
                    header_path=header_path,
                    footer_path=footer_path,
                    logo_path=logo_path,
                )
                if quote_path.exists() and quote_path.stat().st_size > 0:
                    quotations.append(quote_path)
                else:
                    st.warning(f"Quotation empty/missing for: {inst_name}")
                    quote_path = None
            except Exception as e:
                st.warning(f"Quotation generation failed for {inst_name}: {e}")
                quote_path = None

        # 3) Per-school MERGED pack (only if all three components are selected)
        if merge_enabled:
            # We attempt to merge whatever of the three exists (cover, quote, client list)
            pieces: list[Path] = []
            if cover_path and _is_valid_pdf(cover_path):
                pieces.append(cover_path)
            if quote_path and _is_valid_pdf(quote_path):
                pieces.append(quote_path)
            if client_list_path:
                p = Path(client_list_path)
                if p.exists() and p.stat().st_size > 0 and _is_valid_pdf(p):
                    pieces.append(p)

            if pieces:
                combined_path = out_dir / f"Combined_{safe}_{tag}.pdf"
                merger = PdfMerger()
                try:
                    for part in pieces:
                        merger.append(str(part))
                    with open(combined_path, "wb") as fh:
                        merger.write(fh)
                    merged_packs.append(combined_path)
                except Exception as e:
                    st.warning(f"Could not create merged pack for {inst_name}: {e}")
                finally:
                    try:
                        merger.close()
                    except Exception:
                        pass

    # Single Clients List artifact (even if not merged)
    if "Client List" in (components or []) and client_list_path:
        p = Path(client_list_path)
        if p.exists() and p.stat().st_size > 0:
            client_added_path = p
        else:
            st.warning("Clients List file not found or empty; skipping.")

    # Collect all files for downloads
    all_files: list[Path] = []
    all_files.extend(covering_letters)
    all_files.extend(quotations)
    if client_added_path:
        all_files.append(client_added_path)
    all_files.extend(merged_packs)

    return {
        "covering_letters": covering_letters,
        "quotations": quotations,
        "merged_packs": merged_packs,      # one Combined_... per school if merge condition met
        "client_list": client_added_path,  # single path, if available
        "all_files": all_files,
        "out_dir": out_dir,
        "elapsed_sec": round(time.time() - start_time, 2),
    }
