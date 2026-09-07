$(document).ready(function(){
    // One shared catalog for existing rows, new rows and range endpoints.
    var blank = $('.sample-box').last();
    var catalog = SampleRange.catalog(JSON.parse($('#sample-options').text()).map(function (sample) {
        return {id: sample.value, text: sample.text};
    }));
    var insertionAnchor = blank;
    var rowTemplate = blank.clone();
    rowTemplate.find('.sample_dropdown').empty();
    var templateId = blank.attr('id').split('sample_box_id_')[1];
    var nextId = parseInt($('#sample_count').val(), 10);
    function initializeSample(input) {
        input.select2({
            placeholder: 'None selected', allowClear: true,
            query: function (query) { query.callback(catalog.query(query.term, query.page)); },
            initSelection: function (element, callback) {
                var id = element.val();
                callback(catalog.byId[id] || {id: id, text: element.data('sample-text') || 'None selected'});
            }
        });
    }
    $('.sample_dropdown').each(function () { initializeSample($(this)); });

    function newRow(sample) {
        var id = nextId++;
        var row = rowTemplate.clone();
        row.find('*').addBack().each(function () {
            var element = $(this);
            ['id', 'name', 'class'].forEach(function (attribute) {
                var value = element.attr(attribute);
                if (value) element.attr(attribute, value.split(' ').map(function (token) {
                    return token.replace(new RegExp(templateId + '$'), id);
                }).join(' '));
            });
        });
        var select = row.find('.sample_dropdown');
        var input = $('<input>', {type: 'hidden', id: select.attr('id'), name: select.attr('name'),
            'class': 'sample_dropdown', style: 'width:100%', value: sample.id});
        select.replaceWith(input);
        row.append($('<input>', {type: 'hidden', id: 'sample_name_' + id,
            name: 'sample_name_' + id, value: sample.text}));
        insertionAnchor.after(row);
        insertionAnchor = row;
        initializeSample(input);
        $('#modalSampleName' + id).text(sample.text);
        $('#sample_count').val(nextId);
        row.show();
        return row;
    }

    var from = $('#sample-range-from'), to = $('#sample-range-to');
    [from, to].forEach(function (field) {
        field.select2({
            placeholder: field.data('placeholder'), allowClear: true,
            query: function (query) {
                query.callback(catalog.query(query.term, query.page, field === to ? from.val() : null));
            }
        });
    });
    $('#sample-range-resources').select2();
    $('#sample-range').prop('hidden', false);
    from.on('change', function () {
        to.select2('val', '');
        $('#sample-range-message').empty();
    });
    $('#sample-range-clear').on('click', function () {
        from.select2('val', '');
        to.select2('val', '');
        $('#sample-range-resources').select2('val', []);
        $('#sample-range-message').empty();
    });
    $('#sample-range-add').on('click', function () {
        var result = catalog.range(from.val(), to.val());
        var resources = $('#sample-range-resources').val() || [];
        var message = $('#sample-range-message');
        var errors = {
            empty: 'Choose both From and To samples.',
            unknown: 'Choose samples from the available list.',
            family: 'Choose samples with the same prefix and a numeric suffix.',
            reverse: 'To must not come before From in the sample list.'
        };
        if (result.error || !resources.length) {
            message.addClass('text-danger').text(result.error ? errors[result.error] : 'Choose at least one data resource.');
            return;
        }
        var rows = Object.create(null);
        $('.sample_dropdown').each(function () {
            if (this.value && this.value !== '0' && !rows[this.value]) rows[this.value] = $(this).closest('.sample-box');
        });
        var resourceSet = new Set(resources);
        result.items.forEach(function (sample) {
            var row = rows[sample.id] || newRow(sample);
            rows[sample.id] = row;
            row.find('.resource-box').each(function () {
                if (resourceSet.has(this.value.split('@@@')[0])) $(this).prop('checked', true);
            });
            row.find('.refModalAdd').trigger('click');
            row.show();
        });
        message.removeClass('text-danger').text(result.items.length + ' samples linked to the selected resources. Save the form to keep these changes.');
    });
    
      /**
       * Show the modal when a sample selected
       * 
       */
    
      $('#sample-form').on('change', '.sample_dropdown', function(event){
          let id = $(this).attr('id');
          id = id.split("samples_dropdown_")[1];
          var selected = $(this).select2('data');
          if (!selected || !selected.id || selected.id === '0') {
              $('#sample_box_id_' + id).find('.resource-box').prop('checked', false);
              $('#sample_resource_count-message-box_' + id).hide();
              return;
          }
          $('#sample_name_' + id).val($.trim(selected.text));
          $('#modalSampleName' + id).text($.trim($(this).select2('data').text));
          $('#resourcesModal' + id).modal({
            backdrop: 'static',
            keyboard: false
          });
          $('#resourcesModal' + id).modal('show');        
      }); 



    /**
     * Add another sample selection box
     * 
     */

    if ($('#isEditMode') && $('#isEditMode').val() == '1'){
      let sampleCount = $('#existed_samples_dropdown').val();
      for(let i=1; i <= parseInt(sampleCount); i++){
        $('#sample_box_id_' + i).show();
      }
    }
    else{
      $('#sample_box_id_1').show();
    }
    $('#add-another-sample-box').click(function(){
        var unused = $('.sample-box').filter(function () {
            var value = $(this).find('.sample_dropdown').val();
            return $(this).is(':hidden') && (!value || value === '0');
        }).first();
        if (unused.length) unused.show();
        else newRow({id: '0', text: 'None selected'});
    });


    /**
     * remove sample
     * 
     */
     $('#sample-form').on('click', '.sample-remove-anchor', function(event){
      let id = $(this).attr('id');
      event.preventDefault();
      id = id.split("sample-remove-anchor")[1];      
      let checkBoxes = $('.resource-checkbox-input' + id);
      for(let i=0; i < checkBoxes.length; i++){
          if($(checkBoxes[i]).prop('checked') == true){
            $(checkBoxes[i]).click();
          }
      }
      if($('#select-all-resources-' + id).prop('checked') == true){
        $('#select-all-resources-' + id).click();
      }
      $('#sample_resource_names-' + id).text('No resource selected');
      $('#sample_resource_count-message-box_' + id).parent().hide();
      $('#sample_resource_count-message-box_' + id).hide();
      $('#sample_box_id_' + id).fadeOut();
      $('#samples_dropdown_' + id).select2('val', '0');

      let removedElement = $('#sample_box_id_' + id);
      id = parseInt(id);
      for(let i=id + 1; i < $('.sample-box').length; i++ ){
          if(!$('#sample_box_id_' + i).is(':hidden')){
            $(removedElement).insertAfter($('#sample_box_id_' + i));
          }
      }
  });


    /**
     * click the select all box
     * 
     */
    $('#sample-form').on('click', '.select-all-resources', function(event){
        let id = $(this).attr('id');              
        id = id.split("select-all-resources-")[1];
        let checkBoxes = $('.resource-checkbox-input' + id);
        for(let i=0; i < checkBoxes.length; i++){
            if($(checkBoxes[i]).is(':visible')){
              if($(checkBoxes[i]).prop('checked') == !($(this).prop('checked'))){
                  $(checkBoxes[i]).click();
              }
            }
        }
    });


    /**
     * Click Add button on a modal
     * 
     */
    $('#sample-form').on('click', '.refModalAdd', function(event){
        let id = $(this).attr('id');        
        id = id.split("ref_modal_add_btn")[1];
        let boxes = $('.resource-checkbox-input' + id);
        let resourceNames = [];
        for (let i=0; i < boxes.length; i++){
            if($(boxes[i]).prop('checked') == true){
                resourceNames.push($(boxes[i]).data('resource-name'));
            }
        }
        if(resourceNames.length !== 0){
          $('#sample_resource_names-' + id).text(resourceNames.join(', '));
          $('#sample_resource_count-message-box_' + id).parent().show();
          $('#sample_resource_count-message-box_' + id).show();
        }
        else{
          $('#sample_resource_names-' + id).text('No resource selected');
          $('#sample_resource_count-message-box_' + id).parent().hide();
          $('#sample_resource_count-message-box_' + id).hide();
          $("#samples_dropdown_" + id).select2("val", "0"); // none selected
        }
    });

    

    /**
     * click the edit mark on the resource count box
     * 
     */

    $('#sample-form').on('click', '.resource_count_edit', function(event){
      let id = $(this).attr('id');      
      id = id.split("sample_resource_count_edit_")[1];
      $('#resourcesModal' + id).modal({
        backdrop: 'static',
        keyboard: false
       });
      $('#resourcesModal' + id).modal('show'); 
    });

    $('#sample_save_btn').click(function(){
      $('#sample-save-btn-spinner').css("display","inline-block");
    });

    $('#sample-form').submit(function(e){
      $('#next-step-loadin-animation').css('display', 'inline-block');            
    });

    
});
