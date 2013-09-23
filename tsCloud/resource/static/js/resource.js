var Resource = {};

Resource.Submit = {};
Resource.List = {};
Resource.Detail = {};
Resource.Recommendation = {};
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

Resource.Recommendation.onLoad = function(e) {
    // Redirect to the URL with specific category
    $('#id_category').change(function(e) {
        var categorySlug = $(this).val();
        if (categorySlug) {
            window.location.href = '../../' + categorySlug + '/edit/';
        } else {
            alert('The category is not availabel so far');
            e.preventDefault();
        }
    });
    
    // Binding autocomplete to the search box
    $('#appNameInput').autocomplete({
        source:function(query, process){
            Resource.Utils.searchResource(
                {'name__icontains': query},
                {
                    'success': function(respData){
                        return process(respData);
                    }
                }
            )
        },
        formatItem:function(item){
            return item["fields"]["name"]+"("+item["fields"]["version"]+") - "+item["fields"]["desc"];
        },
        setValue:function(item){
            return {'data-value': item["fields"]["name"], 'real-value':item["pk"]};
        }
    });
    
    // Add button clicked
    $("#addBtn").click(function(){
        var resourcePk = $("#appNameInput").attr("real-value") || "";
        if (!resourcePk) {
            alert('Something mistake');
            return false;
        }

        // Check the exist resource
        var inputs = $('#sortableRecommendationContainer').find('input[name="resourcePk"]');
        for (var i=0; i<inputs.length; i++) {
            $input = $(inputs[i]);
            if ($input.val() == resourcePk) {
                $input.parents('.listview-item').toggle("highlight");
                continue
            }
        }

        // Add element
        Resource.Utils.searchResource(
            {'pk__exact': resourcePk},
            {
                'success': function(returnObj) {
                    for (var i=0; i<returnObj.length; i++) {
                        Resource.Elements.generateSortableRecommendation(returnObj[i]).appendTo(
                            $('#sortableRecommendationContainer')
                        );
                        $('#sortableRecommendationContainer').sortable();
                    }
                }
            }
        )
    });

    // Delete button initial
    $('.deleteBtn').click(function(e) {
        $(this).parents('.listview-item').remove();
    });
    
    // Sortable list initial
    $('#sortableRecommendationContainer').sortable();
    
    // Uncheck all of checkboxes
    $('#deactiveRecomendation').click(function(e) {
        $('.checkboxActive').removeAttr('checked');
    })
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
        });
    });
}

Resource.Elements.generateSortableRecommendation = function(jsonObj) {
    var $html = $('<div class="listview-item bg-color-blue"> \
       <input type="hidden" name="resourcePk" value="" /> \
       <div class="pull-left"> \
          <img class="listview-item-object" data-src="{{ recommendation.get_icon_url }}"> \
       </div> \
       <div class="pull-right"> \
           <a href="javascript:void(0)" class="deleteBtn btn">Delete</a> \
       </div> \
       <div class="listview-item-body"> \
          <h4 class="listview-item-heading">{{ recommendation.resource }}</h4> \
          <h5 class="listview-item-subheading">{{ recommendation.resource.version }}</h5> \
          <p class="two-lines">{{ recommendation.get_desc }}</p> \
      </div> \
    </div>');

    $html.find('a.deleteBtn').click(function(e) {
        $html.remove();
    });
    $html.find('input[name="resourcePk"]').val(jsonObj['pk']);
    $html.find('img.listview-item-object').attr('data-src', jsonObj['extras']['get_icon_url']);
    $html.find('h4.listview-item-heading').text(jsonObj['fields']['name']);
    $html.find('h5.listview-item-subheading').text(jsonObj['fields']['version']);
    $html.find('p.two-lines').text(jsonObj['fields']['desc']);
    return $html
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
    });
}

Resource.Utils.searchResource = function(queryJSON, callbacks) {
    $.ajax({
        'url': '../../../../resource/api/get_resources.json',
        'dataType':'json',
        'data': {
            'q': JSON.stringify(queryJSON)
        },
        'success': callbacks['success'] || function(returnObj) {
            alert(returnObj);
        },
        'error': callbacks['error'] || function(xhr, status, error) {
            alert(xhr.responseText);
            return false;
        }
    });
}
