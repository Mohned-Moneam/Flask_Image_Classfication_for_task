import pandas as pd
from sqlalchemy import create_engine

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('static/Data_Storage/Events.csv')

# Create a SQLite database engine
engine = create_engine('sqlite:///api_requests.db', echo=True)

# Extract the time dimension data and insert into the time_dim table
time_dim_df = df[['Timestamp']].drop_duplicates()
time_dim_df['timestamp_key'] = time_dim_df.index + 1
time_dim_df.to_sql('time_dim', con=engine, index=False, if_exists='replace')

# Extract the user dimension data and insert into the user_dim table
user_dim_df = df[['IP Address', 'User-Agent', 'Username']].drop_duplicates()
user_dim_df['user_key'] = user_dim_df.index + 1
user_dim_df.to_sql('user_dim', con=engine, index=False, if_exists='replace')

# Extract the image dimension data and insert into the image_dim table
image_dim_df = df[['Image File']].drop_duplicates()
image_dim_df['image_key'] = image_dim_df.index + 1
image_dim_df.to_sql('image_dim', con=engine, index=False, if_exists='replace')

# Extract the class dimension data and insert into the class_dim table
class_dim_df = df[['Predicted Class']].drop_duplicates()
class_dim_df['class_key'] = class_dim_df.index + 1
class_dim_df.to_sql('class_dim', con=engine, index=False, if_exists='replace')

# Prepare the fact table data with foreign keys from dimension tables
fact_df = df.merge(time_dim_df, on='Timestamp')
fact_df = fact_df.merge(user_dim_df, on=['IP Address', 'User-Agent', 'Username'])
fact_df = fact_df.merge(image_dim_df, left_on='Image File', right_on='Image File')
fact_df = fact_df.merge(class_dim_df, left_on='Predicted Class', right_on='Predicted Class')
fact_df = fact_df[['timestamp_key', 'user_key', 'image_key', 'class_key', 'Time Taken']]

# Insert the fact table data into the api_event_fact table
fact_df.to_sql('api_event_fact', con=engine, index=False, if_exists='replace')
