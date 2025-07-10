import pandas as pd

'''temp while our event file sucks'''

def default() -> str:
    database = pd.read_csv("data_collections/runningCSV.csv")
    return_msg = ""
    for row in database.head(5).itertuples():
        event_title = row.Title
        event_when_date = row.whenDate
        event_link = row.link 
        event_location = row.Location if pd.notna(row.Location) else "N/A"
        
        return_msg += (
            f"**{event_title}**\n"
            f"When: {event_when_date}\n"
            f"Where: {event_location}\n"
            f"Link: {event_link} \n\n"
        )
    print(return_msg)
    return return_msg

