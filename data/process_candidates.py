import csv
import json

csv_file = open('award_candidates.csv', 'r')
jsonfile = open('candidates.json', 'w')

csv_reader = csv.reader(csv_file, delimiter=',')
line_count = 0
candidate_set = []
for row in csv_reader:
    if line_count == 0:
        print(f'Column names are {", ".join(row)}')
        line_count += 1
    else:
        print(f'\t{row[0]} has the alias {row[1]}, and is part of the org {row[2]}.')
        candidate_set.append(row[1])
        line_count += 1
print(f'Processed {line_count} lines.')

candidate_dict = {
    "Candidates": candidate_set
}

json.dump(candidate_dict, jsonfile, indent=2, separators=(',', ': '))