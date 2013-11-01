from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from mptt.forms import TreeNodeChoiceField

import qiniu.conf, qiniu.rs, qiniu.io
import urllib, models

qiniu.conf.ACCESS_KEY = settings.QINIU_STORAGE_KEY
qiniu.conf.SECRET_KEY = settings.QINIU_STORAGE_SECRET

#################################################
# Admin forms
#################################################


form_class_name_choices = (
    ('ResourceBaseForm', 'ResourceBaseForm'),
    ('AppForm', 'AppForm'),
    ('OwnAppForm', 'OwnAppForm'),
    ('UCamResForm', 'UCamResForm'),
    ('YCameraResForm', 'YCameraResForm'),
    ('CrazyEmojiResForm', 'CrazyEmojiResForm'),
)

extra_image_type_choices = (
    ('', '-----------'),
    ('icon', _('Icon')),
    ('screenshot', _('Screenshot')),
    ('banner', _('Banner')),
)

class CategoryAdminForm(forms.ModelForm):
    form_class_name = forms.ChoiceField(choices=form_class_name_choices)

    class Meta:
        model = models.Category

class ExtraImageInlineForm(forms.ModelForm):
    type = forms.ChoiceField(choices=extra_image_type_choices)
    class Meta:
        model = models.ExtraImage

#################################################
# Foundation forms
#################################################

class ResourceBaseForm(forms.ModelForm):
    category = TreeNodeChoiceField(
        queryset=models.Category.objects.all(),
        level_indicator=u'+--',
        to_field_name='slug',
    )
    overwrite_exist_file = forms.BooleanField(
        label=('Overwrite exist file'),
        help_text=_('When then checkbox is on will not check the upload file is exist.'),
        required=False,
    )

    class Meta:
        model = models.Resource

    def __init__(self, *args, **kwargs):
        super(ResourceBaseForm, self).__init__(*args, **kwargs)
        self.__init_remote_storage__()

    def __init_remote_storage__(self, bucket_name='thundersoft'):
        policy = qiniu.rs.PutPolicy(bucket_name)
        self.STORAGE_BUCKET_NAME = bucket_name
        self.storage_upload_token = policy.token()

    def generate_download_url(self, filename):
        return 'http://%s.qiniudn.com/%s' % (
            self.STORAGE_BUCKET_NAME,
            urllib.quote(filename)
        )

    def check_remote_storage_file(self, filename):
        return qiniu.rs.Client().stat(
            self.STORAGE_BUCKET_NAME, filename
        )

    def upload_to_remote_storage(self, cleaned_data_field):
        if not self.cleaned_data['overwrite_exist_file']:
            ret, err = self.check_remote_storage_file(filename = cleaned_data_field.name)
            if ret or not err:
                raise forms.ValidationError(
                    _('The file name %s is exist in remote server.') % (
                        cleaned_data_field.name
                    )
                )

        # Upload the file to remote storage
        ret, err = qiniu.io.put(
            self.storage_upload_token,
            cleaned_data_field.name,
            cleaned_data_field.read(),
        )
        if err:
            raise forms.ValidationError(err)
        if not ret.get('key'):
            raise forms.ValidationError(
                _('No responsed file name from remote storage.')
            )
        return self.generate_download_url(ret['key'])


#################################################
# Extended forms
#################################################

app_type_choices = (
    ('remote', _('Remote URL')),
    ('local',  _('Upload local package'))
)

class AppForm(ResourceBaseForm):
    storage_type    = forms.ChoiceField(label=_('Type'), 
        help_text=_('Specific the package is store in remote server or local'), 
        choices=app_type_choices)
    download_url    = forms.URLField(label=_('Remote URL'), required=False)
    package_file    = forms.FileField(label=_('Package file'), required=False)
    icon            = forms.ImageField(label=_('Icon'), required=False)

    class Meta:
        model = models.Resource
        fields = [
            'category', 'name', 'version', 'desc', 'storage_type', 
            'download_url', 'package_file', 'icon', 'overwrite_exist_file',
        ]

    def clean(self, *args, **kwargs):
        super(AppForm, self).clean(*args, **kwargs)
        cleaned_data = self.cleaned_data
        if cleaned_data['storage_type'] == 'local':
            cleaned_data['download_url'] = self.upload_to_remote_storage(
                cleaned_data_field = cleaned_data['package_file']
            )

        # Upload icon to remote storage
        if cleaned_data.get('icon'):
            cleaned_data['icon_url'] = self.upload_to_remote_storage(
                cleaned_data_field = cleaned_data['icon']
            )
        return cleaned_data

    def save(self, *args, **kwargs):
        ret = super(AppForm, self).save(*args, **kwargs)
        if self.cleaned_data.get('icon_url'):
            self.instance.extraimage_set.create(
                type = 'icon',
                image_url = self.cleaned_data['icon_url'],
            )
        return ret

class OwnAppForm(AppForm):
    version_code    = forms.IntegerField()
    title           = forms.CharField(max_length=255, required=False)
    release_notes   = forms.CharField(widget=forms.Textarea, required=False)
    protocol_version= forms.IntegerField()
    poster          = forms.ImageField(required=False)

    class Meta:
        model = models.Resource
        fields = [
            'category', 'name', 'title', 'version', 'version_code',
            'protocol_version', 'desc', 'release_notes', 'storage_type',
            'download_url', 'package_file', 'icon', 'poster',
            'overwrite_exist_file',
        ]

    def clean(self, *args, **kwargs):
        super(OwnAppForm, self).clean(*args, **kwargs)
        cleaned_data = self.cleaned_data
        if cleaned_data.get('poster'):
            cleaned_data['poster_url'] = self.upload_to_remote_storage(
                cleaned_data_field = cleaned_data['poster']
            )
        return cleaned_data

    def save(self, *args, **kwargs):
        ret = super(OwnAppForm, self).save(*args, **kwargs)
        self.instance.ownappspec_set.create(
            version_code = self.cleaned_data['version_code'],
            protocol_version = self.cleaned_data['protocol_version'],
            title = self.cleaned_data['title'],
            release_notes = self.cleaned_data['release_notes'],
        )

        if self.cleaned_data.get('poster_url'):
            self.instance.extraimage_set.create(
                type = 'poster',
                image_url = self.cleaned_data['poster_url'],
            )
        return ret

#################################################
# App resources forms
#################################################

class AppResBaseForm(ResourceBaseForm):
    download_url    = forms.FileField(label=_('Resource file'))
    icon            = forms.ImageField(label=_('Icon'), required=False)

    class Meta:
        model = models.Resource
        fields = [
            'category', 'name', 'version', 'desc', 'download_url', 'icon',
            'overwrite_exist_file'
        ]

    def clean(self, *args, **kwargs):
        super(AppResBaseForm, self).clean(*args, **kwargs)
        cleaned_data = self.cleaned_data
        cleaned_data['download_url'] = self.upload_to_remote_storage(
            cleaned_data_field = cleaned_data['download_url']
        )

        # Upload icon to remote storage
        if cleaned_data.get('icon'):
            cleaned_data['icon_url'] = self.upload_to_remote_storage(
                cleaned_data_field = cleaned_data['icon']
            )
        return cleaned_data

    def save(self, *args, **kwargs):
        ret = super(AppResBaseForm, self).save(*args, **kwargs)
        if self.cleaned_data.get('icon_url'):
            self.instance.extraimage_set.create(
                type = 'icon',
                image_url = self.cleaned_data['icon_url'],
            )
        return ret

class UCamResForm(AppResBaseForm):
    def __init__(self, *args, **kwargs):
        super(UCamResForm, self).__init__(*args, **kwargs)
        self.__init_remote_storage__(bucket_name = 'ucam')
    

class YCameraResForm(AppResBaseForm):
    def __init__(self, *args, **kwargs):
        super(YCameraResForm, self).__init__(*args, **kwargs)
        self.__init_remote_storage__(bucket_name = 'ycamera')
    

class CrazyEmojiResForm(AppResBaseForm):
    poster          = forms.ImageField(required=False)

    class Meta:
        model = models.Resource
        fields = [
            'category', 'name', 'version', 'desc', 'download_url', 'icon',
            'poster', 'overwrite_exist_file'
        ]

    def __init__(self, *args, **kwargs):
        super(CrazyEmojiResForm, self).__init__(*args, **kwargs)
        self.__init_remote_storage__(bucket_name = 'cam001')

    def clean(self, *args, **kwargs):
        super(CrazyEmojiResForm, self).clean(*args, **kwargs)
        cleaned_data = self.cleaned_data
        if cleaned_data.get('poster'):
            cleaned_data['poster_url'] = self.upload_to_remote_storage(
                cleaned_data_field = cleaned_data['poster']
            )
        return cleaned_data

    def save(self, *args, **kwargs):
        ret = super(CrazyEmojiResForm, self).save(*args, **kwargs)
        if self.cleaned_data.get('poster_url'):
            self.instance.extraimage_set.create(
                type = 'poster',
                image_url = self.cleaned_data['poster_url'],
            )
        return ret

#################################################
# App recommendations forms
#################################################

class RecommendationForm(forms.Form):
    category = TreeNodeChoiceField(
        queryset=models.Category.objects.all(),
        level_indicator=u'+--',
        to_field_name='slug',
    )
