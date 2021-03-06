
# Copyright (C) 2019 Intel Corporation
#
# SPDX-License-Identifier: MIT

from collections import OrderedDict
import os
import os.path as osp

from datumaro.components.extractor import DatasetItem, SourceExtractor, Importer
from datumaro.util.image import lazy_image


class ImageDirImporter(Importer):
    EXTRACTOR_NAME = 'image_dir'

    def __call__(self, path, **extra_params):
        from datumaro.components.project import Project # cyclic import
        project = Project()

        if not osp.isdir(path):
            raise Exception("Can't find a directory at '%s'" % path)

        source_name = osp.basename(osp.normpath(path))
        project.add_source(source_name, {
            'url': source_name,
            'format': self.EXTRACTOR_NAME,
            'options': dict(extra_params),
        })

        return project


class ImageDirExtractor(SourceExtractor):
    _SUPPORTED_FORMATS = ['.png', '.jpg']

    def __init__(self, url):
        super().__init__()

        assert osp.isdir(url)

        items = []
        for name in os.listdir(url):
            path = osp.join(url, name)
            if self._is_image(path):
                item_id = osp.splitext(name)[0]
                item = DatasetItem(id=item_id, image=lazy_image(path))
                items.append((item.id, item))

        items = sorted(items, key=lambda e: e[0])
        items = OrderedDict(items)
        self._items = items

        self._subsets = None

    def __iter__(self):
        for item in self._items.values():
            yield item

    def __len__(self):
        return len(self._items)

    def subsets(self):
        return self._subsets

    def get(self, item_id, subset=None, path=None):
        if path or subset:
            raise KeyError()
        return self._items[item_id]

    def _is_image(self, path):
        for ext in self._SUPPORTED_FORMATS:
            if osp.isfile(path) and path.endswith(ext):
                return True
        return False
