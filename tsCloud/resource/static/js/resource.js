var Resource = {};

Resource.Submit = {};
Resource.List = {};
Resource.Detail = {};
Resource.Elements = {};
Resource.Utils = {};

Resource.Submit.onLoad = function(e) {
    // Redirect to the URL with specific category
    $('#id_category').change(function(e) {
        var categorySlug = $(this).val();
        if (categorySlug) {
            window.location.href = '../' + categorySlug + '/';
        } else {
            alert('The category is not availabel so far');
            e.preventDefault();
        }
    });
    
    // Disable specific elements
    (function() {
        var storageTypeSelect = $('#id_storage_type'),
            disableStorageElements = function() {
                var value = storageTypeSelect.val();
                switch(value) {
                    case "remote":
                        $('#id_download_url').removeAttr('disabled');
                        $('#id_package_file').attr('disabled', 'true');
                        break;
                    case "local":
                        $('#id_download_url').attr('disabled', 'true');
                        $('#id_package_file').removeAttr('disabled');
                        break;
                }
            };

        if (storageTypeSelect) {
            storageTypeSelect.change(disableStorageElements);
            disableStorageElements();
        }
    })();
}

Resource.List.onLoad = function(e) {
    
}

Resource.Detail.onLoad = function(e) {
    Resource.Elements.generateShortURLPopover($('.btnShortUrl'));
}

Resource.Elements.generateShortURLPopover = function($elements) {
    $elements.each(function() {
        $element = $(this);
        var $form = $('<form>').submit(function(e) {
            e.preventDefault();
            var $result = $form.find('.result');
            $result.html($('<div class="progress progress-indeterminate"> \
                <div class="win-ring small"></div> \
            </div>'));
            Resource.Utils.generateShortURL(
                $element.attr('data-slug'),
                $form.find('input[name="source"]').val(),
                {
                    'success': function(returnObj) {
                        var shortUrl = returnObj['data']['url'];
                        $result.html($('<a>').attr('href', shortUrl).text(shortUrl))
                    }
                }
            )
        });
        $('<input type="text" name="source" placeholder="Source" />').appendTo($form);
        $('<input type="submit" value="Generate" />').appendTo($form);
        $('<span class="result"></span>').appendTo($form);

        $($element).popover({
            'html': true,
            'placement': 'bottom',
            'content': $form
        })
    })
}

Resource.Utils.generateShortURL = function(slug, source, callbacks) {
    $.ajax({
        'url': '../../resource/api/' + slug + '/generate_short_url.json',
        'dataType':'json',
        'data': {
            'source': source
        },
        'success': callbacks['success'] || function(returnObj) {
            alert(returnObj['data']['url']);
        },
        'error': callbacks['error'] || function(xhr, status, error) {
            alert(xhr.responseText);
            return false;
        }
    })
}
