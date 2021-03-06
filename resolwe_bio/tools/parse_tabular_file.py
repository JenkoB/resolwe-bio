#!/usr/bin/env python2
"""Parse tabular file."""
from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import csv
import gzip
import os
import xlrd


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Parse tabular file")
    parser.add_argument('input_file', help="Tabular file.")
    parser.add_argument('output_file', help="Output file.")
    return parser.parse_args()


def main():
    """Invoked when run directly as a program."""
    args = parse_arguments()

    ext = os.path.splitext(args.input_file)[-1].lower()
    with gzip.open(args.output_file, mode='wt') as outfile:
        csvwriter = csv.writer(outfile, delimiter=str('\t'), lineterminator='\n')

        try:
            if ext in ('.tab', '.txt', '.tsv'):
                with open(args.input_file) as infile:
                    for line in infile:
                        outline = line.strip().split('\t')
                        csvwriter.writerow(outline)
            elif ext == '.csv':
                with open(args.input_file) as infile:
                    for line in infile:
                        outline = line.strip().split(',')
                        csvwriter.writerow(outline)
            elif ext in ('.xls', '.xlsx'):
                with open(args.input_file) as infile:
                    workbook = xlrd.open_workbook(args.input_file)
                    worksheet = workbook.sheets()[0]
                    for rownum in range(worksheet.nrows):
                        csvwriter.writerow(worksheet.row_values(rownum))
            else:
                print('{"proc.error":"File extension not recognized."}')
        except:
            print('{"proc.error":"Corrupt or unrecognized file."}')
            raise


if __name__ == "__main__":
    main()
