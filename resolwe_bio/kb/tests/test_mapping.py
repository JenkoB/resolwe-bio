# pylint: disable=missing-docstring,invalid-name,no-member
from __future__ import absolute_import, division, print_function, unicode_literals

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.management import call_command

from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Mapping


class MappingTestCase(APITestCase):
    def setUp(self):
        self.mappings = []
        for i in range(10):
            self.mappings.append(Mapping.objects.create(
                relation_type='crossdb',
                source_db='SRC',
                source_id='FT{}'.format(i),
                target_db='TGT',
                target_id='ANOTHER{}'.format(i),
            ))

        call_command('rebuild_index', interactive=False, verbosity=0)

    def assertMappingEqual(self, data, mapping):
        self.assertEqual(data['relation_type'], mapping.relation_type)
        self.assertEqual(data['source_db'], mapping.source_db)
        self.assertEqual(data['source_id'], mapping.source_id)
        self.assertEqual(data['target_db'], mapping.target_db)
        self.assertEqual(data['target_id'], mapping.target_id)

    def test_lookup(self):
        MAPPING_URL = reverse('resolwebio-api:kb_mapping_search-list')

        # Test without any query.
        response = self.client.get(MAPPING_URL, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.mappings))

        # Test lookup by source_db, target_db and a single source feature identifier.
        response = self.client.get(MAPPING_URL, {
            'source_db': 'SRC',
            'target_db': 'TGT',
            'source_id': 'FT0',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertMappingEqual(response.data[0], self.mappings[0])

        # Test lookup by source_db, target_db and a list of source feature identifiers.
        response = self.client.post(MAPPING_URL, {
            'source_db': 'SRC',
            'target_db': 'TGT',
            'source_id': ['FT0', 'FT1', 'FT5']
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertMappingEqual(response.data[0], self.mappings[0])
        self.assertMappingEqual(response.data[1], self.mappings[1])
        self.assertMappingEqual(response.data[2], self.mappings[5])

    def test_admin(self):
        # Test that only an admin can access the endpoint.
        response = self.client.get(reverse('resolwebio-api:mapping-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Authenticate as normal user.
        normal_user = User.objects.create_user('tester', 'tester@genialis.com', 'tester')
        self.client.force_authenticate(user=normal_user)
        response = self.client.get(reverse('resolwebio-api:mapping-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Authenticate as admin.
        admin_user = User.objects.create_superuser('admin', 'admin@genialis.com', 'admin')
        self.client.force_authenticate(user=admin_user)

        # Test listing and detailed access mappings.
        response = self.client.get(reverse('resolwebio-api:mapping-list'), format='json')
        self.assertEqual(len(response.data), len(self.mappings))
        for data, mapping in zip(sorted(response.data, key=lambda x: x['id']), self.mappings):
            self.assertMappingEqual(data, mapping)

            detail = self.client.get(
                reverse('resolwebio-api:mapping-detail', kwargs={'pk': data['id']}),
                format='json'
            )
            self.assertMappingEqual(detail.data, mapping)

        # Test adding new mappings.
        response = self.client.post(
            reverse('resolwebio-api:mapping-list'),
            {
                'source_db': 'SRC',
                'source_id': 'MYSRCID',
                'target_db': 'TGT',
                'target_id': 'MYTGTID',
                'relation_type': Mapping.RELATION_TYPE_CROSSDB,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Mapping.objects.get(source_db='SRC', source_id='MYSRCID').target_id, 'MYTGTID')

        # Test duplicate insert (should automatically update).
        response = self.client.post(
            reverse('resolwebio-api:mapping-list'),
            {
                'source_db': 'SRC',
                'source_id': 'MYSRCID',
                'target_db': 'TGT',
                'target_id': 'MYTGTID',
                'relation_type': Mapping.RELATION_TYPE_ORTHOLOG,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Mapping.objects.get(source_db='SRC', source_id='MYSRCID').relation_type,
                         Mapping.RELATION_TYPE_ORTHOLOG)

        # Test missing source_id insert.
        response = self.client.post(
            reverse('resolwebio-api:mapping-list'),
            {
                'source_db': 'SRC',
                'target_db': 'TGT',
                'target_id': 'MYTGTID',
                'relation_type': Mapping.RELATION_TYPE_ORTHOLOG,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
