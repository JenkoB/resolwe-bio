# pylint: disable=missing-docstring
from resolwe.test import tag_process

from resolwe_bio.utils.test import BioProcessTestCase


class PathwayMapTestCase(BioProcessTestCase):

    @tag_process('upload-metabolic-pathway')
    def test_upload_metabolic_pathway(self):
        file_name = 'matabolic pathway.json.gz'
        inputs = {'src': file_name}
        upload = self.run_process("upload-metabolic-pathway", inputs)
        self.assertJSON(upload, upload.output['pathway'], '', file_name)
