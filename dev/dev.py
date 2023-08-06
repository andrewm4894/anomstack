#%%

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import matplotlib.pyplot as plt
import pandas as pd
import tempfile

# use dotenv to load environment variables
from dotenv import load_dotenv
load_dotenv()


def send_email_with_plot(df, subject, body, attachment_name):
    sender = os.getenv("ANOMSTACK_ALERT_EMAIL_FROM")
    password = os.getenv("ANOMSTACK_ALERT_EMAIL_PASSWORD")
    to = os.getenv("ANOMSTACK_ALERT_EMAIL_TO")
    
    # Plot the DataFrame and save as PNG
    with tempfile.NamedTemporaryFile(prefix=attachment_name, suffix=".png", delete=False) as temp:
        df.plot()
        plt.savefig(temp.name)
        
        # Set up the email
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = to
        msg['Subject'] = subject
        
        # Add the text to the email
        msg.attach(MIMEText(body, 'plain'))
        
        # Open the file in binary mode
        binary_file = open(temp.name, "rb")
        
        payload = MIMEBase('application', 'octate-stream', Name=f'{attachment_name}.png')
        # To change the payload into encoded form
        payload.set_payload((binary_file).read())
        encoders.encode_base64(payload)
       
        # Add header 
        #payload.add_header('Content-Decomposition', 'attachment', filename=temp.name)
        payload.add_header('Content-Decomposition', 'attachment', filename=f'{attachment_name}.png')
        msg.attach(payload)
        
        # Use Gmail's SMTP server to send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        text = msg.as_string()
        server.sendmail(sender, to, text)
        server.quit()

#%%

# Let's create a simple time series DataFrame with dates as the index and a single column of random values

import pandas as pd
import numpy as np

# Create a date range
date_range = pd.date_range(start='1/1/2022', end='1/31/2022')

# Create a DataFrame with random values
df = pd.DataFrame(np.random.randn(len(date_range)), index=date_range, columns=['Value'])

df.head()

#%%

send_email_with_plot(df, 'test', 'hello world', 'someplot')

#%%

#%%