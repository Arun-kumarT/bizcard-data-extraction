import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd
import easyocr
import re
import mysql.connector
from sqlalchemy import create_engine

##sqlalchemy 
config = {'user':'root',    'host':'localhost','password':'1234', 'database':'bizcard_data'}
connection = mysql.connector.connect(**config)
cursor = connection.cursor()
engine = create_engine('mysql+mysqlconnector://root:1234@localhost/bizcard_data',echo=False)

#creating a user built function to preprocess the extracted text 
def extract_data(result1):
    ext_dic1 = {'Name': [], 'Designation': [], 'Company name': [], 'Contact': [], 'Email': [], 'Website': [],
                'Address': []}
    dum=[]
    ext_dic1['Name'].append(result1[0])
    ext_dic1['Designation'].append(result1[1])
    for m in range(2, len(result1)):

        if result1[m].startswith('+') or (result1[m].replace('-', '').isdigit() and '-' in result1[m]):
            ext_dic1['Contact'].append(result1[m])

        elif '@' in result1[m] and '.com' in result1[m]:
            small = result1[m].lower()
            ext_dic1['Email'].append(small)

        elif 'www' in result1[m] or 'WWW' in result1[m] or 'wwW' in result1[m]:
            small = result1[m].lower()
            dum.append(small)
        elif '.com' in result1[m] or '.COM' in result1[m]:
            small = result1[m].lower()
            dum.append(small)
        elif  re.match(r'^[0-9]',result1[m])  or re.match(r'^[A-Za-z].*\,$',result1[m]):

            ext_dic1['Address'].append(result1[m])
        elif 'TamilNadu' in result1[m] or 'Tamil Nadu' in result1[m] or re.match(r'^[0-9]',result1[m]):
            ext_dic1['Address'].append(result1[m])

        elif re.match(r'^[A-Za-z]', result1[m]):
            ext_dic1['Company name'].append(result1[m])
        
        ext_dic1['Website']= '.'.join(dum)
    for key, value in ext_dic1.items():
        if len(value) > 0:
            concatenation_string = ' '.join(value)
            ext_dic1[key] = [concatenation_string]
        else:
            value = 'NA'
            ext_dic1[key] = [value]
    return ext_dic1

#Streamlit part

st.set_page_config(layout= "wide")
st.title(":rainbow[BizcardX Data Extraction using OCR]")
tab1,tab2,tab3,tab4=st.tabs(['Home','Modify',"Delete","View database"])
with tab1:
    #upload bizcard
    bizcard = st.file_uploader(label="Upload the image", type=['png', 'jpg', 'jpeg'], label_visibility="hidden")
    if bizcard is not None:
        img = Image.open(bizcard)
        reader = easyocr.Reader(['en']) # this needs to run only once to load the model into memory
        
        result = reader.readtext(np.array(img), detail = 0)
        st.image(bizcard)

        ext_text = extract_data(result)
        df = pd.DataFrame(ext_text)
        st.dataframe(df,hide_index=True,use_container_width=True)
        if st.button("Migrate to Database"):
            df.to_sql('bizcard',con=engine,if_exists='append',index=False)   
            st.write("Sucessfully Migrated")

with tab2:

    cursor.execute("select * from bizcard")
    data=cursor.fetchall()
    df1=pd.DataFrame(data,columns=['Name','Designation', 'Company name', 'Contact', 'Email', 'Website','Address'])
    names=df1["Name"].tolist()
    selected_name = st.selectbox("Select the name",names)

    df2 = df1[df1["Name"] == selected_name]
    st.dataframe(df2,hide_index=True,use_container_width=True)
    df3 = df2.copy() 
    New_name=st.text_input("Enter the name that should be changed")
    #.loc function=To access more than row or column using label
    df3.loc[df3["Name"] == selected_name, "Name"] = New_name
    selected_designation = st.selectbox("Designation already present", df2["Designation"])
    new_designation = st.text_input("Enter the designation that should be changed")
    selected_companyname = st.selectbox("Company Nmae already present", df2["Company name"])
    new_company_name = st.text_input("Enter the companyname that should be changed")
    selected_contact = st.selectbox("Contact Number already present", df2["Contact"])
    new_contact = st.text_input("Enter the contact that should be changed")
    selected_email= st.selectbox("Email id already present",df2["Email"])
    new_email = st.text_input("Enter the Email id that should be changed")
    selected_website= st.selectbox("website already present",df2["Website"])
    new_website = st.text_input("Enter the Website that should be changed")
    selected_Address= st.selectbox("Address to replace",df2["Address"])
    new_Address = st.text_input("Enter the Address that should be changed")
    df3.loc[df3["Designation"] == selected_designation, "Designation"] = new_designation
    df3.loc[df3["Company name"]== selected_companyname, "Company name"] = new_company_name
    df3.loc[df3["Contact"]== selected_contact,"Contact"]= new_contact
    df3.loc[df3["Email"]== selected_email,"Email"]= new_email
    df3.loc[df3["Website"]== selected_website,"Website"]= new_website
    df3.loc[df3["Address"]== selected_Address,"Address"]= new_Address
    if st.button("Modify"):
        cursor.execute(f"DELETE FROM bizcard WHERE Name ='{selected_name}'")
        connection.commit()
        df3.to_sql('bizcard',con=engine,if_exists='append',index=False)
        connection.commit()
        st.dataframe(df3,hide_index=True,use_container_width=True)
with tab3:
    cursor.execute("select * from bizcard")
    data=cursor.fetchall()
    df1=pd.DataFrame(data,columns=['Name','Designation', 'Company name', 'Contact', 'Email', 'Website','Address'])
    column = st.selectbox("Select the name",df1["Name"],key="visibility")
    if st.button("Delete")  :
            cursor.execute(f"DELETE FROM bizcard WHERE Name ='{column}'")
            connection.commit()
            st.write("sucessfull")
with tab4:            
    if st.button("View Database"):
                cursor.execute("select * from bizcard;")
                table=cursor.fetchall()
                database=pd.DataFrame(table,columns=['Name','Designation', 'Company name', 'Contact', 'Email', 'Website','Address'])
                st.dataframe(database)
                
