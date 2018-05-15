
# coding: utf-8

# # USCIS Case Status Info for multiple cases

# ### Imports

# In[1]:


from requests import post
from bs4 import BeautifulSoup
from IPython.core.display import display
from ipywidgets import widgets
import pandas as pd
import numpy as np
import re
from datetime import datetime


# ### Enter USCIS receipt number(s)

# In[2]:


receipt_inputs = widgets.Textarea(value = 'MSC1890265705\nMSC1890265706\nMSC1890265762\nMSC1890265763\nMSC1791508027',
                                  placeholder = 'Enter USCIS Receipt Numbers, one on each line',
                                  description = 'Receipt #s',
                                  disabled = False)
display(receipt_inputs)


# ### Get case status information for a given receipt

# In[3]:


def get_case_status(rcpt, http_status = False):
    # USCIS case status form
    endpoint = "https://egov.uscis.gov/casestatus/mycasestatus.do"
    
    # Get response from POST request
    response = post(endpoint,
                    data={'appReceiptNum': rcpt, 
                          'caseStatusSearchBtn': 'CHECK+STATUS'})
    
    # Print response status code, if specified
    if http_status:
        print("Response:", response.status_code, response.reason)
    
    # Response is HTML. Use BS4 to parse it and get relevant info
    soup = BeautifulSoup(response.text, 'html.parser')
    relevant_info = soup.find("div", {"class": "rows text-center"})
    case_summary = str(relevant_info.h1.get_text())
    case_details = str(relevant_info.p.get_text())
    
    # Get application type
    form_type_search = re.search("Form ([^,]+)", case_details)
    if form_type_search:
        form_type = form_type_search.group(1)
    else:
        form_type = None
    
    # Get last update date
    last_update_search = re.search("^On (\w+\s\d{1,2},\s+\d{4})", case_details)
    if last_update_search:
        last_update = last_update_search.group(1)
        # Calculate days since last update
        days_since_update = (datetime.now() - datetime.strptime(last_update, '%B %d, %Y')).days
    else:
        last_update = None
        days_since_update = None
    
    # Return list of case summary and details
    return[rcpt, case_summary, form_type, last_update, days_since_update, case_details]


# ### Insert case status information into a Pandas DataFrame
# 

# In[4]:


rcpts = receipt_inputs.value.split('\n')
case_statuses = pd.DataFrame(index = np.arange(0, len(rcpts)), 
                             columns=['RECEIPT #', 'STATUS', 'FORM TYPE', 'LAST UPDATE', 'DAYS SINCE LAST UPDATE', 'DETAILS'])
for r in np.arange(0, len(rcpts)):
    case_statuses.loc[r] = get_case_status(rcpts[r]) # Append results to DF


# ### Results

# In[5]:


pd.set_option('display.max_colwidth', -1) # Don't truncate long values
case_statuses

