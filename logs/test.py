import os
import csv

def main():
    with open('logs.csv', 'w', newline='', encoding='utf-8') as out_file, open('sophos-control.log', 'r') as in_file:
        writer = csv.writer(out_file)
        writer.writerow(['Datum', 'Zeit', 'Benutzer Nachname', 'Benutzer Vorname', 'VPN Benutzer', 'Geschaltet auf'])
        
        for line in in_file:
              columns = line[:-1].split(' ')
              if(len(columns) == 6):
                  writer.writerow(columns[:6])

if __name__ == "__main__":
    main()
