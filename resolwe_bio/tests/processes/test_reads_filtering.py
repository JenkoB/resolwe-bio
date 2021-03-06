# pylint: disable=missing-docstring
from resolwe_bio.utils.test import BioProcessTestCase


class ReadsFilteringProcessorTestCase(BioProcessTestCase):

    def test_prinseq_single(self):
        reads = self.prepare_reads()
        inputs = {'reads': reads.pk}

        filtered_reads = self.run_process('prinseq-lite-single', inputs)
        self.assertFiles(filtered_reads, 'fastq', ['filtered_reads_prinseq_single.fastq.gz'], compression='gzip')
        self.assertFields(filtered_reads, "fastqc_url", [{'file': 'fastqc/reads_fastqc/fastqc_report.html',
                                                          'refs': ['fastqc/reads_fastqc'],
                                                          'size': 314749}])

    def test_prinseq_paired(self):
        inputs = {
            'src1': ['rRNA_forw.fastq.gz'],
            'src2': ['rRNA_rew.fastq.gz']}
        reads = self.run_process('upload-fastq-paired', inputs)

        inputs = {'reads': reads.pk}
        filtered_reads = self.run_process('prinseq-lite-paired', inputs)
        self.assertFiles(filtered_reads, 'fastq', ['filtered_reads_prinseq_paired_fw.fastq.gz'], compression='gzip')
        self.assertFiles(filtered_reads, 'fastq2', ['filtered_reads_prinseq_paired_rw.fastq.gz'], compression='gzip')
        self.assertFields(filtered_reads, "fastqc_url", [{'file': 'fastqc/rRNA_forw_fastqc/fastqc_report.html',
                                                          'refs': ['fastqc/rRNA_forw_fastqc'],
                                                          'size': 347773}])
        self.assertFields(filtered_reads, "fastqc_url2", [{'file': 'fastqc/rRNA_rew_fastqc/fastqc_report.html',
                                                           'refs': ['fastqc/rRNA_rew_fastqc'],
                                                           'size': 340697}])

    def test_fastqmcf_single(self):
        reads = self.prepare_reads()
        inputs = {'reads': reads.pk}
        filtered_reads = self.run_process('fastq-mcf-single', inputs)

        self.assertFiles(filtered_reads, 'fastq', ['filtered_reads_fastqmcf_single.fastq.gz'], compression='gzip')
        self.assertFields(filtered_reads, "fastqc_url", [{'file': 'fastqc/reads_fastqc/fastqc_report.html',
                                                          'refs': ['fastqc/reads_fastqc'],
                                                          'size': 305101}])

    def test_fastqmcf_paired(self):
        inputs = {
            'src1': ['rRNA_forw.fastq.gz'],
            'src2': ['rRNA_rew.fastq.gz']}
        reads = self.run_process('upload-fastq-paired', inputs)

        inputs = {'reads': reads.pk}
        filtered_reads = self.run_process('fastq-mcf-paired', inputs)
        self.assertFiles(filtered_reads, 'fastq', ['filtered_reads_fastqmcf_paired_fw.fastq.gz'], compression='gzip')
        self.assertFiles(filtered_reads, 'fastq2', ['filtered_reads_fastqmcf_paired_rw.fastq.gz'], compression='gzip')
        self.assertFields(filtered_reads, "fastqc_url", [{'file': 'fastqc/rRNA_forw_fastqc/fastqc_report.html',
                                                          'refs': ['fastqc/rRNA_forw_fastqc'],
                                                          'size': 347791}])
        self.assertFields(filtered_reads, "fastqc_url2", [{'file': 'fastqc/rRNA_rew_fastqc/fastqc_report.html',
                                                           'refs': ['fastqc/rRNA_rew_fastqc'],
                                                           'size': 340715}])

    def test_sortmerna_single(self):
        reads = self.prepare_reads(['rRNA_forw.fastq.gz'])
        rrnadb_1 = self.run_process('upload-fasta-nucl', {'src': 'silva-arc-16s-id95.fasta.gz'})
        rrnadb_2 = self.run_process('upload-fasta-nucl', {'src': 'silva-arc-23s-id98.fasta.gz'})

        inputs = {
            'reads': reads.id,
            'database_selection': [rrnadb_1.id, rrnadb_2.id],
            'options': {'threads': 2, 'sam': True}}
        filtered_reads = self.run_process('sortmerna-single', inputs)
        self.assertFiles(filtered_reads, 'fastq', ['reads_wo_rRNA_single.fastq.gz'], compression='gzip')
        self.assertFile(filtered_reads, 'fastq_rRNA', 'reads_rRNA_single.fastq.gz', compression='gzip')
        self.assertFields(filtered_reads, 'fastq_rRNA_sam', {'file': 'rRNA_forw_rRNA.sam'})
        self.assertFields(filtered_reads, 'stats', {'file': 'stats.log'})
        self.assertFields(filtered_reads, "fastqc_url",
                          [{'file': 'fastqc/rRNA_forw_filtered_fastqc/fastqc_report.html',
                            'refs': ['fastqc/rRNA_forw_filtered_fastqc'],
                            'size': 345492}])

    def test_sortmerna_paired(self):
        inputs = {
            'src1': ['rRNA_forw.fastq.gz'],
            'src2': ['rRNA_rew.fastq.gz']}
        reads = self.run_process('upload-fastq-paired', inputs)

        rrnadb_1 = self.run_process('upload-fasta-nucl', {'src': 'silva-arc-16s-id95.fasta.gz'})
        rrnadb_2 = self.run_process('upload-fasta-nucl', {'src': 'silva-arc-23s-id98.fasta.gz'})

        inputs = {
            'reads': reads.id,
            'database_selection': [rrnadb_1.id, rrnadb_2.id],
            'options': {'threads': 2, 'sam': True}}

        filtered_reads = self.run_process('sortmerna-paired', inputs)
        self.assertFiles(filtered_reads, 'fastq', ['reads_wo_rRNA_paired_forw.fastq.gz'], compression='gzip')
        self.assertFiles(filtered_reads, 'fastq2', ['reads_wo_rRNA_paired_rew.fastq.gz'], compression='gzip')
        self.assertFile(filtered_reads, 'fastq_rRNA', 'reads_rRNA_paired.fastq.gz', compression='gzip')
        self.assertFields(filtered_reads, 'fastq_rRNA_sam', {'file': 'rRNA_forw_rRNA.sam'})
        self.assertFields(filtered_reads, 'stats', {'file': 'stats.log'})
        self.assertFields(filtered_reads, "fastqc_url",
                          [{'file': 'fastqc/rRNA_forw_filtered_fastqc/fastqc_report.html',
                            'refs': ['fastqc/rRNA_forw_filtered_fastqc'],
                            'size': 345492}])
        self.assertFields(filtered_reads, "fastqc_url2",
                          [{'file': 'fastqc/rRNA_rew_filtered_fastqc/fastqc_report.html',
                            'refs': ['fastqc/rRNA_rew_filtered_fastqc'],
                            'size': 347212}])

    def test_trimmomatic_single(self):
        reads = self.prepare_reads()
        inputs = {'reads': reads.pk,
                  'trailing': 3,
                  'crop': 5}
        filtered_reads = self.run_processor('trimmomatic-single', inputs)

        self.assertFiles(filtered_reads, 'fastq', ['filtered_reads_trimmomatic_single.fastq.gz'], compression='gzip')
        self.assertFields(filtered_reads, "fastqc_url", [{'file': 'fastqc/reads_fastqc/fastqc_report.html',
                                                          'refs': ['fastqc/reads_fastqc'],
                                                          'size': 206718}])

    def test_trimmomatic_paired(self):
        inputs = {
            'src1': ['rRNA_forw.fastq.gz'],
            'src2': ['rRNA_rew.fastq.gz']}
        reads = self.run_processor('upload-fastq-paired', inputs)
        inputs = {'reads': reads.pk,
                  'trailing': 3}
        filtered_reads = self.run_processor('trimmomatic-paired', inputs)
        self.assertFiles(filtered_reads, 'fastq', ['filtered_reads_trimmomatic_paired_fw.fastq.gz'],
                         compression='gzip')
        self.assertFiles(filtered_reads, 'fastq2', ['filtered_reads_trimmomatic_paired_rw.fastq.gz'],
                         compression='gzip')
        self.assertFields(filtered_reads, "fastqc_url", [{'file': 'fastqc/rRNA_forw_fastqc/fastqc_report.html',
                                                          'refs': ['fastqc/rRNA_forw_fastqc'],
                                                          'size': 352347}])
        self.assertFields(filtered_reads, "fastqc_url2", [{'file': 'fastqc/rRNA_rew_fastqc/fastqc_report.html',
                                                           'refs': ['fastqc/rRNA_rew_fastqc'],
                                                           'size': 340745}])

    def test_hsqutils_trimm(self):
        inputs = {
            'src1': ['hsqutils_reads_mate1_paired_filtered.fastq.gz'],
            'src2': ['hsqutils_reads_mate2_paired_filtered.fastq.gz']}
        reads = self.run_processor('upload-fastq-paired', inputs)

        probe = self.run_processor('upload-file', {'src': 'hsqutils_probe_info.txt'})

        inputs = {'reads': reads.id,
                  'probe': probe.id}

        hsqutils_trimm = self.run_processor('hsqutils-trim', inputs)

        self.assertFiles(hsqutils_trimm, 'fastq', ['hsqutils_reads_trimmed_mate1.fastq.gz'],
                         compression='gzip')
        self.assertFiles(hsqutils_trimm, 'fastq2', ['hsqutils_reads_trimmed_mate2.fastq.gz'],
                         compression='gzip')
