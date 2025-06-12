from typing import List
from logger import logger
def get_names(sheet, spreadsheet_id, sheet_id):
    ranges = [
        f"{sheet_id}!C:C",
        f"{sheet_id}!D:D"
    ]
    CD_collumn = sheet.values().batchGet(
        spreadsheetId=spreadsheet_id,
        ranges=ranges
        ).execute()
    values = CD_collumn.get('valueRanges', [])
    return values[0]["values"], values[1]["values"]
def is_broken(C_collumn, D_collumn):
    if(len(C_collumn) != len(D_collumn)):
        return True
    return False
def is_duplicated(lastnames, firstnames, person):
    for index in range(len(firstnames)):
        if(person[1] == firstnames[index][0]):
            if(person[0] == lastnames[index][0]):
                return True
    return False
def update_name(sheet, spreadsheet_id, sheet_id, person: List):
    lastnames, firstnames = get_names(sheet, spreadsheet_id, sheet_id)
    #the reason to wrap person[1] = str inside a list is because firstnames
    #return a list of lists (these sub-list contain a singl string)
    #hence must person[1] be a list to be search among the lists
    if(is_duplicated(lastnames, firstnames, person)):
        logger.info("Person already added, skipped.")
        return False
    else:
        logger.info("Totally new person, adding...")
        logger.info(f"person: {str(person)}")

    if is_broken(lastnames, firstnames): return False

    append_body = {'values': [[]] * 1}
    sheet.values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_id}!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=append_body
    ).execute()

    data = [
        {"range": f"{sheet_id}!C{len(lastnames)+1}", "values": [person[:2]]},
        {"range": f"{sheet_id}!H{len(lastnames)+1}", "values": [[person[2]]]},
        {"range": f"{sheet_id}!K{len(lastnames)+1}", "values": [person[3:]]},
    ]
    body = {"valueInputOption": "USER_ENTERED", "data":data}
    result = sheet.values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body,
    ).execute()
    logger.info(f"{result.get('totalUpdatedCells')} cells updated.")
    return True
