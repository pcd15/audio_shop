with open(r'transcript.txt', 'r') as file:
    data = file.read()  

search = "SPEAKER_2"
replace = "Macklemore"
data = data.replace(search, replace)

search = "SPEAKER_1"
replace = "Kesha"
data = data.replace(search, replace)

with open(r'transcript_redux.txt', 'w') as file:
    file.write(data)