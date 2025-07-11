import pandas as pd



def print_events(message: str) -> str:
    database = pd.read_csv("data_collections/runningCSV.csv")
    count = 0
    '''in the message look for month and common tags'''
    months = ["january", "february", "march", "april", "may", "june","july", "august", "september", "october", "november", "december"]
    common_tags = ["job fair", "career fair", "workshop", "info session", "ecs",  "information session", "session"]


    date = ""
    for month in months:
        if month in message.lower():
            date = month
            break
   
    tags = []
    for tag in common_tags:
        if tag in message.lower():
            tags.append(tag)
       
    return_msg = ""
    for row in database.itertuples():
        event_found = 0
        if count < 8:
            '''if we find a date'''
            if date:
                if date in row.whenDate.lower():
                    '''now check if there are tags'''
                    if not tags:
                        event_title = row.Title
                        event_when_date = row.whenDate
                        event_link = row.link
                        event_location = row.Location if pd.notna(row.Location) else "N/A"
                        event_found += 1
                    else:
                        for tag in tags:
                            if tag in row.Title.lower():
                                event_title = row.Title
                                event_when_date = row.whenDate
                                event_link = row.link
                                event_location = row.Location if pd.notna(row.Location) else "N/A"
                                event_found += 1
            else:
                '''this is for if we find no date, same system for checking tags'''
                if not tags:
                    '''if found no matching tags/month, just give first 10'''
                    event_title = row.Title
                    event_when_date = row.whenDate
                    event_link = row.link
                    event_location = row.Location if pd.notna(row.Location) else "N/A"
                    event_found += 1
                else:
                    for tag in tags:
                        if tag in row.Title.lower():
                            event_title = row.Title
                            event_when_date = row.whenDate
                            event_link = row.link
                            event_location = row.Location if pd.notna(row.Location) else "N/A"
                            event_found += 1
        else:
            break


        '''if they find the events we add it.... duh'''
        if event_found > 0:
            return_msg += (
            f"**{event_title}**\n"
            f"When: {event_when_date}\n"
            f"Where: {event_location}\n"
            f"Link: {event_link} \n\n"
        )

    return_msg = return_msg[:1999]
    if len(return_msg) < 20:
        return_msg = "No events found :("

    return return_msg
               
           
                       



'''if no prompt just print the first 10 upcoming events'''
def default() -> str:
    database = pd.read_csv("data_collections/runningCSV.csv")
    return_msg = ""
    for row in database.head(8).itertuples():
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

    return_msg = return_msg[:1999]
    if len(return_msg) < 20:
        return_msg = "No events found :("
    return return_msg


       
