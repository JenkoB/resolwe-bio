#!/usr/bin/env python2
import argparse
import csv
import os
import sys
import gzip
import re

from itertools import chain

parser = argparse.ArgumentParser(description='Merge columns of multiple experiments by gene id.')
parser.add_argument('files', nargs='*', help='expression files')
parser.add_argument('--experiments', nargs='+', help='experiment ids')
parser.add_argument('--genes', nargs='+', help='filter genes')
parser.add_argument('--ncrna', help='Cuffmerge annotation file <annotation_file>')
parser.add_argument('--intersection', action='store_true', help='merge by intersection of gene ids')
parser.add_argument('--out', help='output file')


args = parser.parse_args()

# if args.experiments and len(args.experiments) != len(args.files):
#     raise ValueError("Number of experiments must match the number of files")

gene_id_re = re.compile('ID=([\w\-\.]*)')
gene_name_re = re.compile('oId=([\w\-\.]*)')
class_code_re = re.compile('class_code=([\w\-\.]*)')

def _search(regex, string):
    match = regex.search(string)
    return match.group(1) if match.group(1) != "asInReference" else "="


def get_gene_id(ids):
    return _search(gene_id_re, ids)


def get_gene_name(ids):
    return _search(gene_name_re, ids)


def get_class_code(ids):
    return _search(class_code_re, ids)


genes = set()
expressions = []
headers = []
op = set.intersection if args.intersection else set.union
offset = 0

for f in args.files:
    if not os.path.isfile(f):
        exit(1)

    base, ext = os.path.splitext(f)
    delimiter = ';' if ext == '.csv' else '\t'

    with gzip.open(f, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        header = reader.next()[1:]
        headers.append(args.experiments[offset:offset + len(header)] if args.experiments else header)
        offset += len(headers[-1])
        expressions.append(dict((r[0], r[1:]) for r in reader))
        genes = set(expressions[-1].keys()) if args.intersection and not genes else op(genes, expressions[-1].keys())

if args.genes:
    genes = genes.intersection(args.genes)


with open(args.ncrna) as gff:
    gene_id_to_name = {}
    gene_id_to_type = {}
    gene_id_to_location = {}
    gene_id_to_strand = {}

    for l in gff:
        if l.startswith('#'):
            continue
        t = l.split('\t')
        if t[2] != 'transcript':
            continue
        gene_id_to_name[get_gene_id(l)] = get_gene_name(l)
        gene_id_to_type[get_gene_id(l)] = get_class_code(l)
        gene_id_to_location[get_gene_id(l)] = '{}:{}-{}'.format(t[0], t[3], t[4])
        gene_id_to_strand[get_gene_id(l)] = t[6]

genes = sorted(genes)
he = zip(headers, expressions)
rows = []

for g in genes:
    exp = [zip(h, e[g]) for h, e in he if g in e]
    exp.append([('Location', gene_id_to_location[g])])
    exp.append([('Strand', gene_id_to_strand[g])])
    exp.append([('Class_code', gene_id_to_type[g])])
    rows.append(dict(chain.from_iterable(exp), **{'Gene': gene_id_to_name[g]}))
fhandler = open(args.out, 'wb') if args.out else sys.stdout

writer = csv.DictWriter(fhandler, ['Gene'] + ['Location'] + ['Strand'] + ['Class_code'] +
                        [h for subheader in headers for h in subheader], delimiter='\t')
writer.writeheader()
writer.writerows(rows)
