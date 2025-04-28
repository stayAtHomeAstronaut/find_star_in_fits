import pandas as pd


star_name = "TYC 3455-628-1" 
ra = 184.1537
dec = 47.0936
x = 2159.17
y = 1523.66

# Sample DataFrame
data = {
    'star_name': ['John', 'Anna', 'Peter'],
    'ra_degrees': [28, 24, 22],
    'dec_degrees': ['Engineer', 'Doctor', 'Student']
}
df = pd.DataFrame(data)

data = {
    'star_name': [{star_name}],
    'ra_degrees': [ra],
    'dec_degrees': [dec]
}
df = pd.DataFrame(data)


# Convert DataFrame to JSON
json_data = df.to_json(orient='records')

json_data = df.to_json(orient='records', indent=4)
print(json_data)
df.to_json('output.json', orient='records', indent=4)