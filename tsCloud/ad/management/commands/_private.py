from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

class ADBaseCommand(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help='Overwrite existed images'),
        )
    url_validator = URLValidator()

    def valid_url(self, url):
        try:
            self.url_validator(url)
            return True
        except ValidationError, e:
            return False

    def handle(self, *args, **options):
        if options.get('overwrite'):
            self.stdout.write('==== Overwrite mode enabled, all of images will be re-download ===\n')
