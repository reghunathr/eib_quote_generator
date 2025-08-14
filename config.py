# config.py

# Paths to assets (ensure these files exist in the project root or update the paths)
# config.py
# --- Font config (repo-root ./Fonts) ---
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent
_FONTS_DIR = _BASE_DIR / "Fonts"

# Repo-relative fonts
DEJAVU_REG = str(_FONTS_DIR / "DejaVuSans.ttf")
DEJAVU_BOLD = str(_FONTS_DIR / "DejaVuSans-Bold.ttf")
DEJAVU_OBLIQUE = str(_FONTS_DIR / "DejaVuSans-Oblique.ttf")
DEJAVU_BOLD_OBLIQUE = str(_FONTS_DIR / "DejaVuSans-BoldOblique.ttf")
DEJAVU_BOLD_ITALIC = str(_FONTS_DIR / "DejaVuSerifCondensed-BoldItalic.ttf")

# Fallback to system locations (useful on Streamlit Cloud containers)
if not Path(DEJAVU_REG).exists():
    sys_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if sys_path.exists():
        DEJAVU_REG = str(sys_path)

if not Path(DEJAVU_BOLD).exists():
    sys_bold = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    if sys_bold.exists():
        DEJAVU_BOLD = str(sys_bold)

header_path = "trustbay_header.png"
footer_path = "trustbay_footer.png"
logo_path = "218tblogo.jpg"

client_list_path = "Trustbay_EIB_Intro_Letter_Compact_Client_List.pdf"  # Update if needed

# Default font paths (used in PDF generation)
"""
FONT_REGULAR = "~/Library/Fonts/DejaVuSans.ttf"
FONT_BOLD = "~/Library/Fonts/DejaVuSans-Bold.ttf"
FONT_ITALIC = "~/Library/Fonts/DejaVuSans-Oblique.ttf"
FONT_BOLD_ITALIC = "~/Library/Fonts/DejaVuSans-BoldOblique.ttf"
"""
# PDF metadata
DEFAULT_AUTHOR = "Trustbay Finserv Pvt. Ltd."
DEFAULT_TITLE = "EIB Insurance Quotation"
DEFAULT_SUBJECT = "Educational Institution Bus Insurance Renewal"
