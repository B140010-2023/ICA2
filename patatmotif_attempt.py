#!/usr/bin/env python3
import subprocess
import pandas as pd
import re
import csv

print("Initiating Patmatmotif...")

#I realise that I needed to create a dataframe using pandas to initiate the patmatmotif programme, to make a dataframe I needed
#to create a separate fasta format file for each individual sequence within the dataset, I then added a part at the end to add
#all of the results to one large file and delete all the intermediary files to keep the directory less messy

s1 = [] #all lines starting with > (the IDs) are added to this
s2 = [] #all parts starting with M (methionine) are put here which gets all the sequences in this part of the dataframe

try:
    with open('glucose-6-phosphatase_aves_sequences.fasta', 'r') as file:
        current_line = ''
        for line in file:
            line = line.strip()
            if line.startswith('>'):
                s1.append(line)
                if current_line != '':
                    s2.append(current_line)
                    current_line = ''
            else:
                current_line += line
        if current_line != '':
            s2.append(current_line) #realised after many attempts I needed to incorporate this for the last entry into the dataset

#these lines build the data frame and then create a loop which goes through each sequence and writes the fasta code to a new file
    df = pd.DataFrame({'Lines': s1, 'Sequence': s2})
    sequences = df.iloc[1::2]['Sequence'].tolist()
    for i, seq in enumerate(sequences):
        with open(f'sequence_{i}.fasta', 'w') as file:
            file.write(f'>Seq_{i}\n{seq}')

#these lines will perform patmatmotifs, stick the results in a summary file, then remove all the intermediary files
        subprocess.run(f'patmatmotifs -sequence sequence_{i}.fasta -outfile result_{i}.txt', shell=True)
        subprocess.run(f'paste result_{i}.txt >> motif_summary.txt', shell=True)
        subprocess.run(f'rm sequence_{i}.fasta', shell = True)
        subprocess.run(f'rm result_{i}.txt', shell = True)

except Exception as e:
    print("Error:", e)
print("Patmatmotif successful. Detailed summary of patmatmotif can be found in motif_summary.txt")


#to extract the various motifs that were present in the dataset I wrote this code using re to extract the part after Motif from
#the summary file and then put it in a new file called motif_count.txt
motif_count = {}
with open('motif_summary.txt', 'r') as file:
    for line in file:
        motifs = re.findall(r'Motif = (\w+)', line)
        for motif in motifs:
            motif_count[motif] = motif_count.get(motif, 0) + 1

with open('motif_count.txt', 'w') as outfile:
    for motif, count in motif_count.items():
        outfile.write(f"{motif}: {count}\n")

wanna_see = input("Would you like to see the most common motifs? y/n: ")
if wanna_see == 'y':
    with open('motif_count.txt', 'r') as file:
        the_counts = file.read()
        print(the_counts)
else:
    print("Motif count can be found in motif_count.txt")
