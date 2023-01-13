import pandas as pd 
import hashlib
import streamlit as st
import os
import sys

def update_mailchimp(contacts, list_id):

  from mailchimp3 import MailChimp

  API_KEY ='aa2b3bdc7d047dedc01fce3a524d0301-us20'
  client = MailChimp(mc_api = API_KEY, mc_user = "")
  for i in range(len(contacts)):
    i=5
    print("UPLOADING TO MAILCHIMP", contacts['Email Address'][i])
    shash = hashlib.md5(contacts['Email Address'][i].encode()).hexdigest()
    print("SHASH", shash)
    print("address", contacts['tags'][i])
    client.lists.members.create_or_update(list_id=list_id, subscriber_hash=shash, data={
      'email_address':contacts['Email Address'][i], 
      'status_if_new': 'subscribed',

      'merge_fields': {
        'FNAME': contacts['First Name'][i],
        'LNAME': contacts['Last Name'][i],
        'ADDRESS': contacts['Address'][i],
        'BIRTHDAY': contacts['Birthday'][i],
        'INSTRUMENT': contacts['Instrument'][i],
        'STUDENT_FN': contacts['Student First Name'][i],
        'STUDENT_LN': contacts['Student Last Name'][i],
        'D_START': contacts['Date Started'][i],
        'D_INACTIVE': contacts['Inactive Date'][i],

      },
    })

    #work out status
    if contacts['tags'][i] == 'Active':

      client.lists.members.tags.update(list_id='a09d2173ad', subscriber_hash=shash,data = {
        'tags': [
          {'name':'Active', 'status': 'active'}, 
          {'name':'Inactive', 'status': 'inactive'}, 
          {'name':'Lead', 'status': 'inactive'}],
      })

    if contacts['tags'][i] == 'Inactive':

      client.lists.members.tags.update(list_id='a09d2173ad', subscriber_hash=shash,data = {
        'tags': [
          {'name':'Active', 'status': 'inactive'}, 
          {'name':"Inactive", 'status': 'active'}, 
          {'name':'Lead', 'status': 'inactive'}],
      })

    if contacts['tags'][i] == 'Lead':

      client.lists.members.tags.update(list_id='a09d2173ad', subscriber_hash=shash,data = {
        'tags': [
          {'name':'Active', 'status': 'inactive'}, 
          {'name':"Inactive", 'status': 'inactive'}, 
          {'name':'Lead', 'status': 'active'}],
      })

            
    break


def parse_birthday(dates):

  dates = [x[:-5].replace('-', '/') for x in dates]
  #dates = [x[:-5] for x in dates]
  return dates

'''
Processes excel download from music school
'''

def clean_status(statuses):
  new_status=[]
  for status in statuses:
    if status == 'Lead' or status == 'Inactive' or status == 'Active':
      new_status.append(status)
    elif status == "Trial" or status == "Waiting":
      new_status.append("Lead")
    else:
      new_status.append("Unknown: ", status)
  return(new_status)


def process_contacts(filename):
  ''' this is the main program that does the processing of the csv file '''

  try:
    contacts = pd.read_csv(filename, keep_default_na=False, header=0)
  except:
    print("File could not be read -- is the spelling correct?")
    
  try:
    contacts.Birthday = parse_birthday(contacts.Birthday)
    
    #address formatting doesn't work for mailchimp so isn't enabled
    #contacts.Address = [x.replace('\n', '  ').strip() for x in contacts.Address]

    #use parent names as primary contact -- Adult students are also listed as their own parent.  
    contacts["Student First Name"] = contacts["First Name"] 
    contacts["Student Last Name"] = contacts["Last Name"] 
    contacts["First Name"] = contacts["Parent Contact 1 First Name"]  
    contacts["Last Name"] = contacts["Parent Contact 1 Last Name"] 
    contacts["tags"] = clean_status(contacts["Status"])
    contacts['Email Address']= contacts['Parent Contact 1 Email']
    
    #create the output dataframe
    output_contacts = contacts[['First Name', 'Last Name', 'Email Address', 'Student First Name', 'Student Last Name', 'Instrument', 'Birthday',  'Inactive Date', "Date Started", "tags"]]
    return(output_contacts)
#    output_contacts.to_csv("Cleaned_contacts.csv")
  except:
    st.write("File appears to be invalid -- has the mymusicstaff formatting changed?")



  

if __name__=="__main__":
  contactlist = st.file_uploader("Upload your contact list")
  if contactlist is not None:
      contactlist = pd.read_csv(contactlist)
  output_file = process_contacts(contactlist)
  if len(output_file)>0:
      @st.cache
      def convert_df(df):
          # IMPORTANT: Cache the conversion to prevent computation on every rerun
          return df.to_csv().encode('utf-8')

      csv = convert_df(output_file)

      st.download_button(
          label="Download data as CSV",
          data=csv,
          file_name='Cleaned_contacts.csv',
          mime='text/csv',
      )
  


