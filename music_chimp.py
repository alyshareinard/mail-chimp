import pandas as pd 
import hashlib
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
    output_contacts.to_csv("Cleaned_contacts.csv")
  except:
    print("File appears to be invalid -- has the mymusicstaff formatting changed?")
#    print >> sys.stderr, "Exception: %s" % str(e)
#    sys.exit(1)

  upload = input("Upload to Mailchimp (y/n)?")
  try:
    if upload.lower() == 'y':
      list = 'm'
      while list.lower() != 'y' and list.lower() != 'n':
        list = input("Use your default audience (y/n)?")
        if list.lower() == 'y':
          list_id = 'a09d2173ad'
        if list.lower() == 'n':
          list_id = input("New audience ID (To find audience id, go to 'all contacts', \
            select the correct audience, then go to settings and select 'audience name and defaults'): ")
      
      update_mailchimp(output_contacts, list_id)
      print("Contacts have been uploaded to Mailchimp.")
  except:
    print("Problem uploading to Mailchimp.")
  

if __name__=="__main__":
  print("Ready to convert your file.  Please put it in the same directory as this program.")
  file = input("What is the name of your file? (for default of 'ContactList.csv' just hit enter)")
  if file[-3:]=='.csv':
    filename = file
    process_contacts(filename)
  elif file.strip()=="":
    filename = 'ContactList.csv'
    process_contacts(filename)
  else:
    print("invalid file, try again")
  


