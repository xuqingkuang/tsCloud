import os.path
import urllib

from django.db import models

from django.core.files import File
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from tsCloud.core.storage import OverwriteStorage

class URLImageFieldFile(models.fields.files.ImageFieldFile):
    def __init__(self, instance, field, name):
        super(URLImageFieldFile, self).__init__(instance, field, name)
        self.url_validator = URLValidator()
        self.storage = OverwriteStorage()

    def download(self, url = None, name = None, overwrite=False):
        if not overwrite and os.path.isfile(self.path):
            return
        if not name:
            name = self.generate_filename(url)
        image_file = self.retrive(url = url)
        if not image_file:
            return
        self.save(name, File(open(image_file)))

    def generate_filename(self, filename = None):
        if not filename:
            filename = self.name
        filename = filename.split('/')[-1].split('#')[0].split('?')[0]
        return "".join([c for c in filename if c.isalpha() or c.isdigit() or c=='.']).rstrip()

    def name_is_url(self):
        try:
            self.url_validator(self.name)
            return True
        except ValidationError, e:
            return False

    def retrive(self, url = None):
        if not url and not self.name_is_url():
            return None
        if not url:
            url = self.name
        image_files = urllib.urlretrieve(url)
        if image_files:
            return image_files[0]
        return None

class URLImageField(models.ImageField):
    attr_class = URLImageFieldFile
