from fpdf import FPDF, HTMLMixin, XPos , YPos
from PIL import Image
import os
import re
from config import DEFAULT_SUBJECT

class LetterPDF(FPDF, HTMLMixin):
    def __init__(self, partner_info, header_path=None, footer_path=None):
        super().__init__()
        self.header_path = header_path
        self.footer_path = footer_path
        self.partner_info = partner_info
        self.set_left_margin ( 15 )
        self.set_right_margin ( 15 )

        self.add_font ( "DejaVu" , "" , os.path.expanduser ( "Fonts/DejaVuSans.ttf" ) )
        self.add_font ( "DejaVu" , "B" , os.path.expanduser ( "Fonts/DejaVuSans-Bold.ttf" ) )
        self.add_font ( "DejaVu" , "I" , os.path.expanduser ( "Fonts/DejaVuSans-Oblique.ttf" ) )
        self.add_font ( "DejaVu" , "BI" , os.path.expanduser ( "Fonts/DejaVuSerifCondensed-BoldItalic.ttf" ) )

    def ensure_space(self , height_needed) :
        """
        Ensure there's enough space on the page for a block of content.
        If not, add a new page first.
        """
        if self.get_y ( ) + height_needed > self.h - self.b_margin :
            self.add_page ( )

    def add_watermark(self , watermark_path) :
        center_x = 105  # A4 center width
        center_y = 160  # Center height approx

        with self.rotation ( angle=45 , x=center_x , y=center_y ) :
            self.image ( watermark_path , x=center_x - 40 , y=center_y - 40 , w=135 )

    def header(self) :
        """
        if os.path.exists(self.header_path):
            self.image(self.header_path, x=10, y=8, w=190)
        self.set_y(20)
        """
        # Dimensions
        self.add_watermark ( "trustbay_watermark.png" )
        page_width = self.w
        banner_height = 10
        image_path = "TB Caption.jpg"

        # Load the image and get size
        img = Image.open ( image_path )
        img_width_mm = 45  # Desired width in mm
        img_height_mm = banner_height

        # Calculate positions
        # left_block_width = (page_width - img_width_mm) / 2 - 1  # 1mm gap padding
        # right_block_x = left_block_width + img_width_mm + 2  # 1mm padding both sides

        left_block_width = 20  # 1mm gap padding
        right_block_x = left_block_width + img_width_mm + 2  # 1mm padding both sides

        # Blue fill
        self.set_fill_color ( 1 , 129 , 200 )

        # Draw left blue block
        self.rect ( 5 , 8 , left_block_width , banner_height , style="F" )

        # Draw right blue block
        self.rect ( right_block_x , 8 , page_width - (right_block_x + 5) , banner_height , style="F" )

        # Place the image in the center
        self.image ( image_path , x=left_block_width + 1 , y=8 , w=img_width_mm , h=img_height_mm )

        self.set_text_color ( 0 , 0 , 0 )  # Reset to black
        self.ln ( 12 )

    def footer(self) :
        HO_ADDRESS = "HO : 5, NSP Nagar | Pattom P.O | Kesavadasapuram | Trivandrum | PH: 9447157307, 9567300733"

        # Get list of service points (assumed to be a list of strings)
        service_points = self.partner_info.get ( "Service_Point" , [ ] )  # List of points
        if isinstance ( service_points , str ) :
            # Handle comma-separated string fallback
            service_points = [ s.strip ( ) for s in service_points.split ( ',' ) if s.strip ( ) ]

        # Filter out "HO" or blank values
        custom_service_points = [ sp for sp in service_points if sp and sp.upper ( ) != "HO" ]

        total_lines = 1 + len ( custom_service_points )
        self.set_y ( -total_lines * 5 - 5 )  # Adjust based on number of lines

        self.set_fill_color ( 1 , 129 , 200 )  # Trustbay blue
        self.set_text_color ( 255 , 255 , 255 )  # White text
        self.set_font ( "helvetica" , "I" , 9 )

        page_width = self.w - 10
        line_height = 5

        # Line 1: Always print HO Address
        self.set_x ( 5 )
        self.cell (
            page_width ,
            line_height ,
            HO_ADDRESS ,
            new_x=XPos.LMARGIN ,
            new_y=YPos.NEXT ,
            align="C" ,
            fill=True ,
        )

        # Additional service points (if any)
        for sp in custom_service_points :
            self.set_x ( 5 )
            self.cell (
                page_width ,
                line_height ,
                f"Service Point: {sp}" ,
                new_x=XPos.LMARGIN ,
                new_y=YPos.NEXT ,
                align="C" ,
                fill=True ,
            )

        # Reset colors for main content
        self.set_text_color ( 0 , 0 , 0 )

    def safe_multicell(self , text , height=5) :
        # Sanitize problematic characters
        text = text.replace ( "–" , "-" ).replace ( "₹" , "₹" )  # Keep ₹ if font supports, else use Rs.

        # Get available width (total width - left margin - right margin)
        usable_width = self.w - self.l_margin - self.r_margin

        try :
            self.multi_cell ( usable_width , height , text )
        except Exception :
            # Attempt recovery by injecting zero-width spaces after special chars
            safe_text = re.sub ( r"([/@._-])" , r"\1\u200b" , text )
            self.multi_cell ( usable_width , height , safe_text )


    def add_intro(self, institution, owner, address):
        self.set_font("DejaVu", "", 8)
        self.ln(3)
        self.multi_cell(0, 6, f"To:\n{owner}\n{institution}\n{address}")
        self.ln(3)
        self.set_font("DejaVu", "BI", 8)
        self.multi_cell(0, 6, F"Subject: {DEFAULT_SUBJECT}")
        self.ln(3)

    def add_letter_body(self) :
        self.ln ( 6 )
        self.set_text_color ( 255 , 255 , 255 )
        self.set_fill_color ( 0 , 102 , 204 )
        self.cell ( 60 , 6 ,"Greetings from Trustbay Finserv Pvt. Ltd." , border=1 , ln=True , fill=True , align='C' )
        #self.safe_multicell ( "Greetings from Trustbay Finserv Pvt. Ltd." )
        self.ln ( 9 )

        self.set_text_color ( 0 , 0 , 0 )
        self.set_fill_color ( 255 , 255 , 255 )

        self.set_font ( "DejaVu" , "" , 7 )

        self.safe_multicell (
            "We thank you sincerely for considering us for your Educational Institution Bus insurance renewal. Based on our discussions and the information shared, we are pleased to submit our quotation for your kind perusal." )

        # self.ln(2)
        # self.safe_multicell("Based on our discussions and the information shared, we are pleased to submit our quotation for your kind perusal.")

        self.ln ( 4 )
        self.set_font ( "DejaVu" , "BI" , 7 )
        self.safe_multicell (
            "Trustbay is a trusted and growing name in insurance services, offering customer-centric solutions tailored for schools." )
        #self.set_font ( "DejaVu" , size=7 )
        self.ln ( 4 )

        self.safe_multicell (
            "In FY 2024–25, we insured 1307 vehicles from 390 schools across Kerala and Kanyakumari, with over ₹4.85 crore in collected premiums. To serve you better, we’ve expanded operations to Calicut in addition to our Trivandrum head office." )
        # self.safe_multicell("To serve you better, we’ve expanded operations to Calicut in addition to our Trivandrum head office.")

        self.ln ( 3 )
        self.set_font ( "DejaVu" , "B" , 8 )
        self.cell ( 0 , 6 , "Please Note:" , ln=True )

        self.set_font ( "DejaVu" , "BI" , 7 )
        self.set_text_color ( 0 , 0 , 0 )
        self.set_fill_color ( 242 , 249 , 255 )

        notes_lines = [
            "The quoted IDV is approximate and may vary based on the previous insurance." ,
            "Seating capacity is fetched from the Parivahan portal and will be finalized upon receipt of RC." ,
            "Additional charges may apply for standing capacity." ,
            "Quotation is based on current rates and may be revised at the time of policy issuance." ,
            "TP Premium includes Legal Liability" ,
        ]

        # Build a single string with bullets
        notes_text = "\n".join ( "• " + ln for ln in notes_lines )

        self.multi_cell ( 0 , 5 , notes_text , border=1 , fill=True )
        self.set_fill_color ( 255 , 255 , 255 )
        self.ln ( 3 )

        self.ensure_space ( 25 )
        self.ln ( 3 )
        self.set_font ( "DejaVu" , "B" , 8 )
        self.cell ( 0 , 6 , "Covers:" , ln=True )
        self.set_font ( "DejaVu" , "BI" , 7 )
        self.set_fill_color ( 242 , 249 , 255 )  # Light blue background

        covers_text = (
            "* Accidents – Damages and losses caused to your bus due to an accident.  "
            "* Theft – Damages and losses caused to your bus in the case of a theft.  "
            "* Fire – Damages or losses caused to your bus due to fire.  "
            "* Natural Disasters – Damages and losses due to floods, earthquakes, or other natural calamities.  "
            "* Third Party Losses – Losses and damages caused to third-party vehicle, property, or persons.  "
            "* Comprehensive Coverage – Own Damage (including IMT 23) and Third Party coverage."
        )

        self.multi_cell ( 0 , 5 , covers_text , border=1 , fill=True )
        self.set_fill_color ( 255 , 255 , 255 )  # Reset fill color to white
        self.ln ( 3 )

        self.ln ( 3 )
        self.set_font ( "DejaVu" , size=7)
        self.safe_multicell (
            "We work with leading insurers such as Tata AIG, Reliance General, Future Generali and major Public Sector Companies." )

        self.ln ( 3 )

        """
        self.set_font ( "DejaVu" , "B" , 7 )
        self.safe_multicell ( "Please note:" )
        self.set_font ( "DejaVu" , size=7 )
        self.ln ( 1 )
        self.set_font ( "DejaVu" , "I" , size=7 )
        self.safe_multicell ( "- The quoted IDV is approximate and may vary based on prior insurance." )
        self.ln ( 1 )
        self.safe_multicell (
            "- Seating capacity is fetched from the Parivahan portal and will be finalized upon receipt of RC." )
        self.ln ( 1 )
        self.safe_multicell ( "- Additional charges may apply for standing capacity." )
        self.ln ( 1 )
        self.safe_multicell (
            "- Quotation is based on current rates and may be revised at the time of policy issuance." )
        self.set_font ( "DejaVu" , size=7 )
        self.ln ( 2 )
        """

        self.ensure_space ( 25 )
        self.ln ( 2 )
        self.set_font ( "DejaVu" , "B" , 8 )
        self.cell ( 0 , 6 , "Our Unique Offerings:" , ln=True )

        self.set_font ( "DejaVu" , "BI" , 7 )
        self.set_fill_color ( 242 , 249 , 255 )

        # Construct the message
        offers_text = (
            f"> - 24x7 Claim Support from our offices in {self.partner_info [ 'Location' ]} and HO. Call: {self.partner_info [ 'Mobile' ]}, 9567300733, 7902748494 "
            "> - Prompt assistance to help you initiate claims and complete forms effortlessly.  "
            "> - End-to-end support from surveyor scheduling to final claim settlement.  "
            "> - 95% Discount on Own Damage (OD) Premium.  "
        )

        # Draw a box around the notes using multi_cell with border
        self.multi_cell ( 0 , 5 , offers_text , border=1 , fill=True )
        self.set_fill_color ( 255 , 255 , 255 )
        self.ln ( 3 )
        self.set_font ( "DejaVu" , "B" , 7 )
        self.safe_multicell ( "For any queries or support, please contact:" )
        self.set_font ( "DejaVu" , size=9 )
        self.set_font ( "DejaVu" , "BI" , size=7 )
        self.ln ( 3 )
        self.safe_multicell (f"{self.partner_info [ 'Name' ]} ({self.partner_info [ 'Location' ]}) – {self.partner_info [ 'Mobile' ]}")
        self.ln ( 3 )
        self.safe_multicell ( "Mr. Saiju Philip (Head – EIB Services) – 9447157307" )

        self.ln ( 3 )
        self.set_font ( "DejaVu" , size=7 )
        self.safe_multicell (
            "We look forward to partnering with your institution in safeguarding your transport operations." )

        self.ln ( 3 )
        self.set_font ( "DejaVu" , "BI" , 7)
        self.safe_multicell ( "Warm regards:" )
        self.ln ( 4 )
        self.set_font ( "DejaVu" , "B" , size=9 )
        self.safe_multicell ( "Trustbay Finserv Pvt. Ltd." )
