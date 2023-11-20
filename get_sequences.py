#!/usr/bin/env python3
#importing necessary modules
import requests
import subprocess

#Creating a def containing the URLs necessary to get the sequence data in json format this code is edited from the
#ENSEMBL REST API code found on https://rest.ensembl.org/, I wasn't sure how to do it without biopython but this worked!
def get_sequences(waddyawant):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    search_url = f"{base_url}esearch.fcgi?db=protein&term={waddyawant}&retmax=1000&retmode=json"

#the next few lines check if the status code is 200 (successsful) & gets the protein IDs from the NCBI database
    try:
        jasons = requests.get(search_url)
        if jasons.status_code == 200:
            data = jasons.json()
            ids = data["esearchresult"]["idlist"]
#fetches the fasta sequences from the NCBI database
            if ids:
                id_list = ",".join(ids)
                make_url = f"{base_url}efetch.fcgi?db=protein&id={id_list}&rettype=fasta&retmode=text"
                sequences = requests.get(make_url)
#returns successful sequences or gives an error message with the error code if there was an issue
                if sequences.status_code == 200:
                    return sequences.text.split(">")[1:]
                else:
                    print(f"Failed to fetch sequences. Status code: {sequences.status_code}")
            else:
                print("No sequences found.")
        else:
            print(f"Failed to fetch IDs. Status code: {jasons.status_code}")
    except Exception as e:
        print("Error:", e)

    return None
#prompts the user to input their choice of protein and class
protein = input("Enter your protein of interest: ")
species = input("Enter your class: ")
#adds the inputted information into the def so the fetching part of the script can be applied to what was specified
waddyawant = f'"{protein}"[Protein] AND {species}[Organism]'

fetched_sequences = get_sequences(waddyawant)

if fetched_sequences:
    print(f"{len(fetched_sequences)} sequences retrieved") #prints how many sequences were retrieved
    output_filename = f"{protein}_{species}_sequences.fasta" #outputs the sequences into a named fasta output file
    with open(output_filename, "w") as file: #I didn't realise it needed a > to perform clustalo so I added the > back on :)
        for seq in fetched_sequences:
            if not seq.startswith('>'):
                seq = '>' + seq
            file.write(seq)

#this next chunk of code will ask the user whether they want to continue with conservation analysis of their chosen protein family
clustal = input("Would you like to analyse conservation in your chosen sequences? y/n: ")
if clustal == "y":
    try:
        clustalo = subprocess.run('clustalo -i *.fasta -o clustalo.output', shell = True)
        winsize = input("What is your desired winsize for plotting using plotcon? Enter intiger: ")
        png_maker = subprocess.run(f'plotcon -sequence clustalo.output -graph png -winsize {winsize}')
    except Exception as e:
        print("Error:", e)
elif clustl == "n":
    print("Programme terminated, exiting...")
    sys.exit()
else:
    print("Input not recognised. exiting...")
    sys.exit()
