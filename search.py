from fuzzywuzzy import fuzz

def fuzzy_search(query:str, entries) -> list:
    
  query = query.lower()
  matching_entries = []
  for entry in entries:
    title = entry['title'].lower()
    if fuzz.token_set_ratio(query, title) >= 80:
      matching_entries.append(entry)
      
  return matching_entries