import pandas as pd
import streamlit as st
import time

def on_click():
    st.success("Filtered Data Downloaded")

st.title("CSV Cleaner")
st.header("Use this application to filter your csv file")
st.write("Upload your csv below. The program will automatically filter the data for the required \
         columns and make the pre-specified changes to the data. You can then click the download \
             button to download your filtered and cleaned csv.")

with st.form("upload_file", clear_on_submit=True):
    st.subheader("Upload Your CSV")
    uploaded_file = st.file_uploader(label=" ",
                     type=["csv"])
    submit = st.form_submit_button(label="Upload",
                                   use_container_width=True)
    
if submit and uploaded_file is not None:
    #Success message
    st.toast("File has been uploaded")

    #Define file name
    file_name = uploaded_file.name.split(".")[0]
    new_file_name = f"Filtered_{file_name}.csv"

    #Load data as a pandas df
    df = pd.read_csv(uploaded_file)

        
    #Select columns (from client)
    columns_to_keep = [
        "Provider Name",
        "Patient Name", 
        "Patient DOB", 
        "Facility Name", 
        "Place of Service",
        "ICD10",
        "CPT", 
        "Modifiers",
        "Date of Service (Facility Timezone)"
    ]

    filtered_df = df[columns_to_keep].sort_values("Date of Service (Facility Timezone)")

    #Select only first 6 ICD10 codes
    new_ICD_codes = []

    for index, row in filtered_df.iterrows():
        new_code_list = filtered_df["ICD10"].iloc[index].split(",")[0:6]
        new_code_list = ", ".join(new_code_list)
        new_ICD_codes.append(new_code_list)

    filtered_df["ICD10"] = new_ICD_codes

    #Convert filtered data frame to csv
    csv_file = filtered_df.to_csv().format("UTF-8")

    #Download button
    st.download_button(label="Download Filtered Data",
                        use_container_width=True,
                        data = csv_file,
                        file_name=new_file_name,
                        mime="text/csv",
                        type="primary"
                        )
else:
    st.info("Please upload a file to run the cleaning script")