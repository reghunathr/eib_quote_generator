from fpdf import FPDF
import os
from PIL import Image, ImageEnhance
from pandas import to_datetime
from config import DEFAULT_SUBJECT, DEJAVU_BOLD,DEJAVU_REG,DEJAVU_BOLD_ITALIC,DEJAVU_BOLD_OBLIQUE,DEJAVU_OBLIQUE
from fpdf.enums import XPos , YPos


class QuotationPDF(FPDF):
    def __init__(self, header_path, footer_path, logo_path,partner_info):
        super().__init__()
        self.header_path = header_path
        self.footer_path = footer_path
        self.logo_path = logo_path
        self.partner_info = partner_info
        self.set_margin(5)
        self.add_font ( "DejaVu" , "" , os.path.expanduser ( DEJAVU_REG ))
        self.add_font ( "DejaVu" , "B" , os.path.expanduser ( DEJAVU_BOLD ) )
        self.add_font ( "DejaVu" , "I" , os.path.expanduser ( DEJAVU_OBLIQUE ) )
        self.add_font ( "DejaVu" , "BI" , os.path.expanduser ( DEJAVU_BOLD_ITALIC ))
        self.set_font ( "DejaVu" , size=7 )

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

    def header(self):
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
        self.ln(12)

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

    """
    def footer(self):
        
        
        print({self.partner_info['Service_Point']})
        if os.path.exists(self.footer_path):
            self.set_y(-20)
            self.image(self.footer_path, x=10, y=self.get_y(), w=190)
        """
    def add_intro(self, institution, owner, address):
        self.set_font("DejaVu", "", 8)
        self.ln(2)
        self.multi_cell(0, 6, f"To:\n{owner}\n{institution}\n{address}")
        self.ln(2)
        self.set_font("DejaVu", "BI", 8)
        self.multi_cell(0, 6, f"Subject: {DEFAULT_SUBJECT}")
        self.ln(2)
        self.set_font ( "DejaVu" ,"" , 8 )

        self.multi_cell (
            0 , 6 ,
            "Respected Sir/Madam,\n"
            "At the outset, we express our sincere thanks for considering us to submit a quote for your insurance renewal. "
            "As per our discussion and the information shared, please find the quotation enclosed for your kind perusal."
        )
        self.ln ( 2 )

    def add_vehicle_card(self, row):
        self.ln(2)
        line_height = 5
        card_height = line_height * 5 + 4  # 5 lines + spacing
        self.ensure_space ( card_height + 4 )

        # Line with "Vehicle Details:" in black and regNo in white on blue
        self.set_font ( "DejaVu" , "B" , 7 )

        # "Vehicle Details:" - black on white
        self.set_text_color ( 0 , 0 , 0 )
        self.set_fill_color ( 255 , 255 , 255 )
        self.cell ( 35 , 8 , "Registration No:" , border=1 , ln=0 )

        # regNo - white on blue
        self.set_text_color ( 255 , 255 , 255 )
        self.set_fill_color ( 0 , 102 , 204 )
        self.cell(30, 8, row['regNo'], border=1, ln=True, fill=True, align='C')
        self.ln(1)

        # Reset for body
        self.set_text_color ( 0 , 0 , 0 )
        self.set_fill_color ( 255 , 255 , 255 )

        self.set_font("DejaVu", "", 7)

        expiry_raw = row['vehicleInsuranceUpto']
        try:
            expiry_date = to_datetime(expiry_raw).strftime('%d/%m/%Y')
        except Exception:
            expiry_date = str(expiry_raw)

        self.set_fill_color ( 255 , 255 , 255 )
        self.cell ( 140, 6 , f"Previous Insurer: {row [ 'vehicleInsuranceCompanyName' ]}" , border=1 , ln=False )

        self.set_fill_color(220, 220, 220)
        self.set_font ( "DejaVu" , "B" , 7 )
        self.cell(50, 6, f"Expiry: {expiry_date}", align="C", border=1, ln=True, fill=True)
        self.set_font ( "DejaVu" , "" , 7 )

        self.cell(120, 6, f"Make: {row['vehicleManufacturerName']} {row['model']}", border=1)
        self.cell(20, 6, f"Year: {int(float(row['ModelYear']))}", border=1)
        self.cell(20, 6, f"Seat: {int(float(row['vehicleSeatCapacity']))}", border=1)
        self.cell(30, 6, f"IDV: ₹{float(row['IDV']):,.2f}", border=1, ln=True)

        self.cell(40, 6, f"TP: ₹{float(row['TP_Premium']):,.2f}", border=1)
        self.cell(40, 6, f"OD: ₹{float(row['OD_Premium']):,.2f}", border=1)
        self.cell(40, 6, f"Net: ₹{float(row['Net_Premium']):,.2f}", border=1)
        self.cell(40, 6, f"GST: ₹{float(row['GST_Amount']):,.2f}", border=1)
        self.cell(30, 6, f"Total: ₹{float(row['Gross_Premium']):,.2f}", border=1, ln=True)


        self.cell(90, 6, f"Advance Paid: ₹{float(row['Adv_Paid']):,.2f}", border=1)

        self.set_font ( "DejaVu" , "B" , 8 )
        self.set_fill_color ( 220 , 220 , 220 )
        self.cell(100, 6, f"Final Amount: ₹{float(row['Final_Amount']):,.2f}", align="C", border=1, ln=True,fill=True)

    def add_vehicle_table(self , df) :

        self.set_font ( "DejaVu" , "B" , 8 )
        self.cell ( 0 , 7 , "Vehicle-wise Insurance Premium Details" , ln=True , align="C" )

        self.ln ( 1 )
        self.set_text_color ( 0 , 0 , 0 )

        # (DataFrame column, Display Label, Width)
        headers = [
            ("regNo" , "Reg No" , 18) ,
            ("vehicleSeatCapacity" , "Seat" , 10) ,
            ("ModelYear" , "Model" , 10 ),
            ("IDV" , "IDV **" , 18) ,
            ("TP_Premium" , "TP" , 18) ,
            ("OD_Premium" , "OD" , 18) ,
            ("Net_Premium" , "Net" , 18) ,
            ("GST_Amount" , "GST" , 18) ,
            ("Gross_Premium" , "Total" , 18) ,
            ("Adv_Paid" , "Advance" , 18) ,
            ("Final_Amount" , "Final" , 18) ,
            ("vehicleInsuranceUpto" , "Expiry" , 18) ,
        ]

        row_height = 5
        font_size = 7

        # Print headers
        self.set_font ( "DejaVu" , "B" , font_size )
        self.set_fill_color ( 1 , 129 , 200 )
        #self.set_fill_color ( 0 , 51 , 102 )
        self.set_draw_color ( 200 , 200 , 200 )
        self.set_text_color ( 255 , 255 , 255 )
        for _ , label , width in headers :
            self.cell ( width , row_height , label , border=1 , fill=True , align="C" )
        self.ln ( )

        self.set_text_color ( 0 , 0 , 0 )
        self.set_draw_color ( 0 , 0 , 0 )
        # Print each row
        self.set_font ( "DejaVu" , "" , font_size )

        for _ , row in df.iterrows ( ) :
            for col , _ , width in headers :
                val = row.get ( col , "" )

                if col == "vehicleInsuranceUpto" :
                    try :
                        val = to_datetime ( val ).strftime ( '%d/%m/%Y' )
                    except Exception :
                        val = str ( val )
                    self.set_font ( "DejaVu" , "B" , font_size )  # 👈 Bold font for date
                else :
                    if col in ("IDV" , "TP_Premium" , "OD_Premium" , "Net_Premium" , "GST_Amount" ,
                               "Gross_Premium" , "Adv_Paid" , "Final_Amount") :
                        val = f"₹{float ( val ):,.0f}"
                    elif col == ("vehicleSeatCapacity","ModelYear") :
                        val = str ( int ( float ( val ) ) ) if val else ""

                    self.set_font ( "DejaVu" , "" , font_size )  # 👈 Normal font

                self.cell ( width , row_height , str ( val ) , border=1 , align="C" )
            self.ln ( )

        # Totals (exclude: regNo, seat, expiry)
        self.set_font ( "DejaVu" , "B" , font_size )
        self.set_fill_color ( 242 , 249 , 255 )
        self.cell ( headers [ 0 ] [ 2 ] , row_height , "TOTAL" , border=1 , align="C" , fill=True )  # RegNo
        self.cell ( headers [ 1 ] [ 2 ] , row_height , "" , border=1 , fill=True )  # Seat

        for col , _ , width in headers [ 2 :-1 ] :  # From IDV to Final_Amount
            total = df [ col ].sum ( )
            val = f"₹{total:,.0f}" if col not in ("vehicleSeatCapacity", "ModelYear") else ""
            self.cell ( width , row_height , val , border=1 , align="C" , fill=True )

        self.cell ( headers [ -1 ] [ 2 ] , row_height , "" , border=1 , fill=True )  # Expiry
        self.ln ( 5 )

    def add_summary(self , summary_df , institution_info) :
        line_height = 5
        card_height = line_height * 7 + 4  # 7 lines + spacing
        self.ensure_space ( card_height + 4 )

        self.set_font ( "DejaVu" , "B" , 8 )
        self.cell ( 0 , 8 , f"Summary for {institution_info [ 'name' ]}" , ln=True )

        self.set_font ( "DejaVu" , "" , 7 )

        # Calculations
        total_vehicles = summary_df['Total Vehicles'].iloc[0]

        total_idv = summary_df [ 'IDV' ].sum ( )
        total_tp = summary_df [ 'TP_Premium' ].sum ( )
        total_od = summary_df [ 'OD_Premium' ].sum ( )
        total_net = summary_df [ 'Net_Premium' ].sum ( )
        total_gst = summary_df [ 'GST_Amount' ].sum ( )
        total_gross = summary_df [ 'Gross_Premium' ].sum ( )
        total_adv = summary_df [ 'Adv_Paid' ].sum ( )
        total_final = summary_df [ 'Final_Amount' ].sum ( )

        # Set font and styles
        self.set_font ( "DejaVu" , "B" , 7 )
        self.set_fill_color ( 230 , 230 , 230 )  # Light grey background
        self.set_text_color ( 0 )

        # Row 1: Vehicle Count & IDV
        self.cell ( 60 , 6 , "Total Vehicles" , border=1 , align="C" , fill=True )
        self.cell ( 60 , 6 , "Total IDV" , border=1 , align="C" , fill=True , ln=1 )
        self.set_font ( "DejaVu" , "B" , 7 )
        self.cell ( 60 , 6 , str ( total_vehicles ) , border=1 , align="C" )
        self.cell ( 60 , 6 , f"₹{total_idv:,.0f}" , border=1 , align="C" , ln=1 )

        # Row 2: TP, OD, Net, GST
        self.set_font ( "DejaVu" , "B" , 7 )
        self.cell ( 40 , 6 , "TP Premium" , border=1 , align="C" , fill=True )
        self.cell ( 40 , 6 , "OD Premium" , border=1 , align="C" , fill=True )
        self.cell ( 40 , 6 , "Net Premium" , border=1 , align="C" , fill=True )
        self.cell ( 40 , 6 , "GST" , border=1 , align="C" , fill=True , ln=1 )
        self.set_font ( "DejaVu" , "B" , 7 )
        self.cell ( 40 , 6 , f"₹{total_tp:,.0f}" , border=1 , align="C" )
        self.cell ( 40 , 6 , f"₹{total_od:,.0f}" , border=1 , align="C" )
        self.cell ( 40 , 6 , f"₹{total_net:,.0f}" , border=1 , align="C" )
        self.cell ( 40 , 6 , f"₹{total_gst:,.0f}" , border=1 , align="C" , ln=1 )

        # Row 3: Gross, Advance, Final
        self.set_font ( "DejaVu" , "B" , 7 )
        self.cell ( 60 , 6 , "Gross Premium" , border=1 , align="C" , fill=True )
        self.cell ( 60 , 6 , "Advance Paid" , border=1 , align="C" , fill=True )
        self.cell ( 60 , 6 , "Final Amount" , border=1 , align="C" , fill=True , ln=1 )
        self.set_font ( "DejaVu" , "B" , 7 )
        self.cell ( 60 , 6 , f"₹{total_gross:,.0f}" , border=1 , align="C" )
        self.cell ( 60 , 6 , f"₹{total_adv:,.0f}" , border=1 , align="C" )
        self.set_font ( "DejaVu" , "BI" , 9 )
        self.set_fill_color ( 173 , 216 , 230 )# Light Blue background
        self.cell ( 60 , 6 , f"₹{total_final:,.0f}" , border=1 , align="C" ,fill=True,  ln=1 )
        self.set_fill_color ( 255 , 255 , 255 )  # Light grey background
        self.ln ( 2 )

    """
    def add_summary(self, summary_df, institution_info):
        print(summary_df.head())
        self.set_font("DejaVu", "B", 8)
        self.cell(0, 8, f"Summary for {institution_info['name']}", ln=True)
        self.set_font("DejaVu", "", 7)
        for col in summary_df.columns:
            value = summary_df.at[0, col]
            self.cell(50, 6, f"{col}", border=1)
            self.cell(50, 6, f"{value}", border=1, ln=True)
    """
    def add_disclaimer_and_contact(self):
        self.ensure_space ( 25 )
        self.ln(3)
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
        self.ln ( 2 )

        self.ensure_space ( 12 )
        self.ln(5)
        self.set_font ( "DejaVu" , "BI", size=8 )
        self.multi_cell (0,5,
            "The rates quoted above are from Reliance General Insurance Company Limited. We work with leading insurers such as Tata AIG, Reliance General, Future Generali and major Public Sector Companies." )

        self.ln(2)
        self.ensure_space (25)
        self.set_font("DejaVu", "B", 8)
        self.cell(0, 6, "Please note:", ln=True)

        self.set_font("DejaVu", "BI", 7)
        self.set_fill_color(242, 249, 255)


        # Construct the message
        notes_text = (
            "** The quoted IDV is approximate and may vary based on the previous insurance.  "
            "* Seating capacity is fetched from the Parivahan portal and will be finalized upon receipt of RC.  "
            "* Additional charges may apply for standing capacity.  "
            "* Quotation is based on current rates and may be revised at the time of policy issuance.  "
            "* TP Premium includes Legal Liability"
        )

        # Draw a box around the notes using multi_cell with border
        self.multi_cell(0, 5, notes_text, border=1,fill=True)
        self.set_fill_color ( 255 , 255 , 255 )

        self.ln(2)



        """
        self.ln ( 2 )
        self.set_font ( "DejaVu" , "B" , 8 )
        self.multi_cell ( 0,5,"Please note:" )
        self.set_font ( "DejaVu" , size=8 )
        self.ln ( 1 )
        self.set_font ( "DejaVu" , "BI" , size=7 )
        self.multi_cell ( 0,5,"- The quoted IDV is approximate and may vary based on the previous insurance." )
        self.ln ( 1 )
        self.multi_cell (0,5,
            "- Seating capacity is fetched from the Parivahan portal and will be finalized upon receipt of RC." )
        self.ln ( 1 )
        self.multi_cell ( 0,5,"- Additional charges may apply for standing capacity." )
        self.ln ( 1 )
        self.multi_cell (0,5,
            "- Quotation is based on current rates and may be revised at the time of policy issuance." )
        self.set_font ( "DejaVu" , size=8 )
        """
        """
        self.ensure_space ( 20)
        self.ln ( 2 )
        self.set_font ( "DejaVu" , "B" , 8 )
        self.multi_cell ( 0,5,"For any queries or support, please contact:" )
        self.set_font ( "DejaVu" , size=9 )
        self.set_font ( "DejaVu" , "BI" , size=8 )
        self.ln ( 1 )
        self.multi_cell (0,5, "- Mr. Sathyanath R (North Kerala) – 9744696462" )
        self.ln ( 1 )
        self.multi_cell ( 0,5,"- Mr. Saiju Philip (Head – EIB Services) – 9447157307" )
        """
        self.ensure_space ( 20 )
        self.ln ( 3 )

        # Caption with blue color and bold font, centered
        self.set_font ( "DejaVu" , "" , 8 )

        self.cell ( 0 , 5 , "Connect with us for assistance and guidance:" , ln=True , align="C" )

        # Contact names in bold italic and black, centered
        self.set_text_color ( 0 )  # Reset to black
        self.set_font ( "DejaVu" , "BI" , 8 )
        self.ln ( 1 )
        self.set_text_color ( 0 , 51 , 102 )  # Soft blue
        #self.cell ( 0 , 5 , "Mr. Sathyanath R (North Kerala) – 9744696462" , ln=True , align="C" )
        self.multi_cell (
            0 ,  # width (0 = full width)
            10 ,  # height of each line
            text=f"{ self.partner_info [ 'Name' ]} ({self.partner_info [ 'Location' ]}) – {self.partner_info [ 'Mobile' ]}",align="C" ,ln=True
        )

        self.cell ( 0 , 5 , "Mr. Saiju Philip (Head – EIB Services) – 9447157307" , ln=True , align="C" )

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

        self.ensure_space ( 21 )
        self.ln ( 4 )
        self.set_font ( "DejaVu" , size=8 )
        self.multi_cell (0,5,
            "We look forward to partnering with your institution in safeguarding your transport operations." )

        self.ln ( 4 )
        self.set_font ( "DejaVu" , "BI" , 9 )
        self.multi_cell (0,6, "Warm regards, Trustbay Finserv Pvt. Ltd." )
        #self.ln ( 5 )
        #self.set_font ( "DejaVu" , "B" , size=9 )
        #self.multi_cell ( 100,6,"Trustbay Finserv Pvt. Ltd." )


def generate_quotation_pdf(data, institution_info, partner_info, output_path, header_path, footer_path, logo_path):
    pdf = QuotationPDF(header_path, footer_path, logo_path,partner_info)
    pdf.add_page()

    pdf.add_intro(institution_info['name'], institution_info.get('owner', 'Principal'), institution_info.get('address', ''))
    """
    summary_df = data [ [
        'IDV' , 'TP_Premium' , 'OD_Premium' , 'Net_Premium' ,
        'GST_Amount' , 'Gross_Premium' , 'Adv_Paid' , 'Final_Amount'
    ] ].sum ( ).to_frame ( ).T

    # Add Total Vehicles count
    summary_df.insert ( 0 , 'Total Vehicles' , len ( data ) )

    pdf.add_summary ( summary_df , institution_info )
    """
    pdf.add_vehicle_table(data)

    """
    for _, row in data.iterrows():
        pdf.add_vehicle_card(row)

    """

    """
    pdf.add_summary(data[[
        'IDV', 'TP_Premium', 'OD_Premium','Net_Premium', 'GST_Amount', 'Gross_Premium', 'Adv_Paid', 'Final_Amount'
    ]].sum().to_frame().T, institution_info)
    """

    pdf.add_disclaimer_and_contact()

    print(f"📝 Attempting to save PDF to {output_path}")
    pdf.output(output_path)
    print(f"✅ Successfully saved PDF to {output_path}")
