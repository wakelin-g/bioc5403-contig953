import sys
import re
import json
import urllib.parse
import os.path

import argparse

def read_external_fasta(filename):
    fasta = {}
    with open(filename) as fp:
        lines = fp.read().splitlines()
        current_fasta = ''
        for line in lines:
            if line[0] == '>':
                current_fasta = line[1:]
            elif len(line) > 5:
                fasta[current_fasta] = line
    return fasta

def main():
    parser = argparse.ArgumentParser(description='convert gff file format to json')

    parser.add_argument('--fasta',
            help='user external fasta file')

    parser.add_argument('--out',
            help='specify the output name')

    parser.add_argument('gff_file',
            help='gff file')

    args = parser.parse_args()

    src_filename = args.gff_file
    if args.out:
        dst_filename = args.out
    else:
        dst_filename = os.path.splitext(src_filename)[0]+'.json'

    fasta = {}
    if args.fasta:
        fasta = read_external_fasta(args.fasta)

    f = open(src_filename)
    fastaSection = False
    records = []

    currentFasta = ''
    sequence = ''
    for line in f.readlines():
        if args.fasta and re.match('##FASTA', line):
            fastaSection = True
        if line[0] == '#':
            continue
        if not fastaSection:
            segment = re.split('\t| ', line)
            attributesString = re.split('\n|;', segment[8])
            attributes = {}
            for s in attributesString:
                e = s.split('=')
                if len(e) >= 2:
                    attributes[e[0]] = urllib.parse.unquote(e[1])

            record = {
                    'seqName': segment[0],
                    'source': segment[1],
                    'feature': segment[2],
                    'start': int(segment[3])-1,
                    'end': int(segment[4]),
                    'score': segment[5],
                    'strand': segment[6],
                    'frame': segment[7],
                    'attribute': attributes,
                    }
            records.append(record)
        else:
            if re.match(r'^>', line):
                print(line)
                if currentFasta != '':
                    fasta[currentFasta]=sequence
                currentFasta = re.findall('[a-zA-z0-9]+', line[1:])[0]
                sequence = ''
            else:
                sequence += re.match(r'\S+', line).group()
    else:
        fasta[currentFasta]=sequence
    f.close()
    with open(dst_filename, 'w') as f2:
        json.dump({'records': records, 'fasta': fasta}, f2, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    main()
