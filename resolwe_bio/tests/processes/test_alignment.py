# pylint: disable=missing-docstring
from resolwe_bio.utils.test import BioProcessTestCase
from resolwe.flow.models import Data


class AlignmentProcessorTestCase(BioProcessTestCase):

    def test_bowtie(self):
        genome = self.prepare_genome()
        reads_single = self.prepare_reads()
        reads_paired = self.prepare_paired_reads(mate1=['fw_reads.fastq.gz', 'fw_reads_2.fastq.gz'],
                                                 mate2=['rw_reads.fastq.gz', 'rw_reads_2.fastq.gz'])

        inputs = {
            'genome': genome.id,
            'reads': reads_single.id,
            'reporting': {'r': "-a -m 1 --best --strata"}
        }
        alignment = self.run_process('alignment-bowtie', inputs)
        self.assertFile(alignment, 'stats', 'bowtie_single_reads_report.tab.gz', compression='gzip')

        inputs = {
            'genome': genome.id,
            'reads': reads_paired.id,
            'reporting': {'r': "-a -m 1 --best --strata"},
            'use_SE': True
        }
        alignment = self.run_process('alignment-bowtie', inputs)
        self.assertFile(alignment, 'stats', 'bowtie_use_SE_report.tab.gz', compression='gzip')

        inputs = {
            'genome': genome.id,
            'reads': reads_paired.id,
            'reporting': {'r': "-a -m 1 --best --strata"}
        }
        alignment = self.run_process('alignment-bowtie', inputs)
        self.assertFile(alignment, 'stats', 'bowtie_paired_reads_report.tab.gz', compression='gzip')

    def test_bowtie2(self):
        genome = self.prepare_genome()
        reads = self.prepare_reads()
        reads_paired = self.prepare_paired_reads(mate1=['fw_reads.fastq.gz', 'fw_reads_2.fastq.gz'],
                                                 mate2=['rw_reads.fastq.gz', 'rw_reads_2.fastq.gz'])

        inputs = {
            'genome': genome.pk,
            'reads': reads.pk,
            'reporting': {'rep_mode': "def"}
        }
        aligned_reads = self.run_process('alignment-bowtie2', inputs)
        self.assertFile(aligned_reads, 'stats', 'bowtie2_reads_report.txt')

        inputs = {
            'genome': genome.id,
            'reads': reads_paired.id,
            'reporting': {'rep_mode': "def"}
        }
        aligned_reads = self.run_process('alignment-bowtie2', inputs)
        self.assertFile(aligned_reads, 'stats', 'bowtie2_paired_end_report.txt')

        inputs = {
            'genome': genome.id,
            'reads': reads_paired.id,
            'reporting': {'rep_mode': "def"},
            'PE_options': {'use_SE': True}
        }
        aligned_reads = self.run_process('alignment-bowtie2', inputs)
        self.assertFile(aligned_reads, 'stats', 'bowtie2_use_SE_report.txt')

    def test_tophat(self):
        genome = self.prepare_genome()
        reads = self.prepare_reads()
        reads_paired = self.prepare_paired_reads(mate1=['fw_reads.fastq.gz', 'fw_reads_2.fastq.gz'],
                                                 mate2=['rw_reads.fastq.gz', 'rw_reads_2.fastq.gz'])

        inputs = {'src': 'annotation.gff.gz', 'source': 'DICTYBASE'}
        annotation = self.run_process('upload-gff3', inputs)

        inputs = {
            'genome': genome.id,
            'reads': reads.id,
            'gff': annotation.id,
            'PE_options': {
                'library_type': "fr-unstranded"}}
        aligned_reads = self.run_process('alignment-tophat2', inputs)
        self.assertFile(aligned_reads, 'stats', 'tophat_reads_report.txt')

        inputs = {
            'genome': genome.id,
            'reads': reads_paired.id,
            'gff': annotation.id,
            'PE_options': {
                'library_type': "fr-unstranded"}}
        aligned_reads = self.run_process('alignment-tophat2', inputs)
        self.assertFile(aligned_reads, 'stats', 'tophat_paired_reads_report.txt')

    def test_star(self):
        genome = self.prepare_genome()
        reads = self.prepare_reads()

        inputs = {'src': 'annotation.gff.gz', 'source': 'DICTYBASE'}
        annotation = self.run_process('upload-gff3', inputs)

        inputs = {'genome': genome.pk,
                  'annotation': annotation.pk,
                  'threads': 2,
                  'advanced': {
                      'genomeSAindexNbases': 12,
                      'genomeSAsparseD': 4
                  }}

        genome_index = self.run_process('alignment-star-index', inputs)

        inputs = {
            'genome': genome_index.pk,
            'reads': reads.pk,
            'threads': 2,
            't_coordinates': {
                'quantmode': True,
                'gene_counts': True}}
        aligned_reads = self.run_process('alignment-star', inputs)
        self.assertFile(aligned_reads, 'gene_counts', 'gene_counts_star.tab.gz', compression='gzip')

        exp = Data.objects.last()
        self.assertFile(exp, 'exp', 'star_expression.tab.gz', compression='gzip')
        self.assertFields(exp, 'source', 'DICTYBASE')

    def test_bwa_bt(self):
        genome = self.prepare_genome()
        reads = self.prepare_reads()
        reads_paired = self.prepare_paired_reads(mate1=['fw_reads.fastq.gz', 'fw_reads_2.fastq.gz'],
                                                 mate2=['rw_reads.fastq.gz', 'rw_reads_2.fastq.gz'])

        inputs = {'genome': genome.id, 'reads': reads.id}
        aligned_reads = self.run_process('alignment-bwa-aln', inputs)
        self.assertFile(aligned_reads, 'stats', 'bwa_bt_reads_report.txt')

        inputs = {'genome': genome.id, 'reads': reads_paired.id}
        aligned_reads = self.run_process('alignment-bwa-aln', inputs)
        self.assertFile(aligned_reads, 'stats', 'bwa_bt_paired_reads_report.txt')

    def test_bwa_sw(self):
        genome = self.prepare_genome()
        reads = self.prepare_reads()
        reads_paired = self.prepare_paired_reads(mate1=['fw_reads.fastq.gz', 'fw_reads_2.fastq.gz'],
                                                 mate2=['rw_reads.fastq.gz', 'rw_reads_2.fastq.gz'])

        inputs = {'genome': genome.id, 'reads': reads.id}
        aligned_reads = self.run_process('alignment-bwa-sw', inputs)
        self.assertFile(aligned_reads, 'bam', 'bwa_sw_reads_mapped.bam')
        self.assertFile(aligned_reads, 'stats', 'bwa_sw_reads_report.txt')

        inputs = {'genome': genome.id, 'reads': reads_paired.id}
        aligned_reads = self.run_process('alignment-bwa-sw', inputs)
        self.assertFile(aligned_reads, 'bam', 'bwa_sw_paired_reads_mapped.bam')
        self.assertFile(aligned_reads, 'stats', 'bwa_sw_paired_reads_report.txt')

    def test_bwa_mem(self):
        genome = self.prepare_genome()
        reads = self.prepare_reads()
        reads_paired = self.prepare_paired_reads(mate1=['fw_reads.fastq.gz', 'fw_reads_2.fastq.gz'],
                                                 mate2=['rw_reads.fastq.gz', 'rw_reads_2.fastq.gz'])

        inputs = {'genome': genome.id, 'reads': reads.id}
        aligned_reads = self.run_process('alignment-bwa-mem', inputs)
        self.assertFile(aligned_reads, 'stats', 'bwa_mem_reads_report.txt')

        inputs = {'genome': genome.id, 'reads': reads_paired.id}
        aligned_reads = self.run_process('alignment-bwa-mem', inputs)
        self.assertFile(aligned_reads, 'stats', 'bwa_mem_paired_reads_report.txt')
        self.assertFile(aligned_reads, 'unmapped', 'bwa_mem_unmapped_reads.fastq.gz', compression='gzip')

    def test_hisat2(self):
        genome = self.prepare_genome()
        reads = self.prepare_reads()
        reads_paired = self.prepare_paired_reads(mate1=['fw_reads.fastq.gz', 'fw_reads_2.fastq.gz'],
                                                 mate2=['rw_reads.fastq.gz', 'rw_reads_2.fastq.gz'])

        inputs = {
            'genome': genome.id,
            'reads': reads.id}
        aligned_reads = self.run_process('alignment-hisat2', inputs)
        self.assertFile(aligned_reads, 'stats', 'hisat2_report.txt')

        inputs = {
            'genome': genome.id,
            'reads': reads_paired.id}
        aligned_reads = self.run_process('alignment-hisat2', inputs)
        self.assertFile(aligned_reads, 'stats', 'hisat2_paired_report.txt')

    def test_subread(self):
        genome = self.prepare_genome()

        inputs = {'src': 'my.strange.genome name$.fasta.gz'}
        genome_2 = self.run_process('upload-genome', inputs)

        reads = self.prepare_reads()
        reads_paired = self.prepare_paired_reads(mate1=['fw_reads.fastq.gz', 'fw_reads_2.fastq.gz'],
                                                 mate2=['rw_reads.fastq.gz', 'rw_reads_2.fastq.gz'])

        inputs = {'genome': genome.id, 'reads': reads.id}
        aligned_reads = self.run_process('alignment-subread', inputs)
        self.assertFile(aligned_reads, 'stats', 'subread_reads_report.txt')

        inputs = {'genome': genome_2.id, 'reads': reads_paired.id}
        aligned_reads = self.run_process('alignment-subread', inputs)
        self.assertFile(aligned_reads, 'stats', 'subread_paired_reads_report.txt')
