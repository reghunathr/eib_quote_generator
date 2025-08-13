import streamlit as st
import pandas as pd
import os

class PartnerSelector:
    def __init__(self, partner_file="partners0.xlsx"):
        self.partner_file = partner_file
        self.partner_df = self.load_partner_file()

    def load_partner_file(self):
        if os.path.exists(self.partner_file):
            return pd.read_excel(self.partner_file)
        else:
            return pd.DataFrame(columns=["Name", "Location", "Mobile", "Service_Point"])

    def save_partner(self, new_entry):
        self.partner_df = pd.concat([self.partner_df, new_entry], ignore_index=True)
        self.partner_df.to_excel(self.partner_file, index=False)

    def render(self) :
        st.header ( "Partner Selection" )

        partner_names = self.partner_df [ "Name" ].tolist ( )
        selected_partner = st.selectbox ( "Select a Partner" , [ "" ] + partner_names )

        # Track whether to show the "Add New Partner" form
        if "show_add_form" not in st.session_state :
            st.session_state.show_add_form = False

        if selected_partner :
            partner_row = self.partner_df [ self.partner_df [ "Name" ] == selected_partner ].iloc [ 0 ]
            partner_info = {
                "Name" : partner_row [ "Name" ] ,
                "Location" : partner_row [ "Location" ] ,
                "Mobile" : str ( partner_row [ "Mobile" ] ) ,
                "Service_Point" : partner_row [ "Service_Point" ]
            }
            st.success ( f"Selected Partner: {partner_info [ 'Name' ]} ({partner_info [ 'Location' ]})" )
            return partner_info

        # If no partner selected, offer a button to add new partner
        if not st.session_state.show_add_form :
            if st.button ( "Partner Not Listed? Add New Partner" ) :
                st.session_state.show_add_form = True
            return None

        # Now show add form
        st.markdown ( "### Add New Partner" )
        new_name = st.text_input ( "Partner Name" )
        new_location = st.text_input ( "Location" )
        new_contact = st.text_input ( "Mobile Number" )
        new_service_point = st.text_input ( "Service Point" )

        if st.button ( "Add Partner" ) :
            if new_name and new_location and new_contact :
                new_row = pd.DataFrame ( [ {
                    "Name" : new_name ,
                    "Location" : new_location ,
                    "Mobile" : new_contact ,
                    "Service_Point" : new_service_point
                } ] )
                self.save_partner ( new_row )
                st.success ( "Partner added successfully! Please select from the dropdown." )
                st.session_state.show_add_form = False
                st.rerun ( )
            else :
                st.warning ( "All fields are required to add a new partner." )

        return None
