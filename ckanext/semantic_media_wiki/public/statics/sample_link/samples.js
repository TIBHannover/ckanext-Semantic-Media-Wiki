$(document).ready(function(){
      $(".sample_dropdown").select2();
    
      /**
       * Show the modal when a sample selected
       * 
       */
    
      $('.sample_dropdown').change(function(){         
          let id = $(this).attr('id');
          id = id[id.length - 1];
          $('#sample_name_' + id).val($.trim($(this).select2('data').text));   
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
    $('#sample_box_id_1').show();
    $('#add-another-sample-box').click(function(){
      let all_visible = false;
      for(let i=1; i <= $('.sample-box').length; i++){
        if ($('#sample_box_id_' + i).is(':hidden')){
          $('#sample_box_id_' + i).fadeIn();
          all_visible = true;
          break;
        }
      }
      if(!all_visible){
        $(this).hide();
      }
    });

    /**
     * click the select all box
     * 
     */
    $('.select-all-resources').click(function(){
        let id = $(this).attr('id');
        id = id[id.length - 1];
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
    $('.refModalAdd').click(function(){
        let id = $(this).attr('id');
        id = id[id.length - 1];
        let boxes = $('.resource-checkbox-input' + id);
        let resourceCount = 0;
        for (let i=0; i < boxes.length; i++){
            if($(boxes[i]).prop('checked') == true){
                resourceCount += 1;
            }
        }
        if(resourceCount !== 0){
          $('#sample_resource_count-' + id).text(resourceCount);
          $('#sample_resource_count-message-box_' + id).show();
        }
        else{
          $('#sample_resource_count-' + id).text(0);
          $('#sample_resource_count-message-box_' + id).hide();
          $("#samples_dropdown_" + id).select2("val", "0"); // none selected
        }
    });

    /**
     * remove sample
     * 
     */
    $('.sample-remove-anchor').click(function(){
        let id = $(this).attr('id');
        id = id[id.length - 1];
        let checkBoxes = $('.resource-checkbox-input' + id);
        for(let i=0; i < checkBoxes.length; i++){
            if($(checkBoxes[i]).prop('checked') == true){
              $(checkBoxes[i]).click();
            }
        }
        if($('#select-all-resources-' + id).prop('checked') == true){
          $('#select-all-resources-' + id).click();
        }
        $('#sample_resource_count-' + id).text('0');
        $('#sample_resource_count-message-box_' + id).hide();
        $('#sample_box_id_' + id).fadeOut();
        
    });

    /**
     * click the edit mark on the resource count box
     * 
     */

    $('.resource_count_edit').click(function(){
      let id = $(this).attr('id');
      id = id[id.length - 1];
      $('#resourcesModal' + id).modal({
        backdrop: 'static',
        keyboard: false
       });
      $('#resourcesModal' + id).modal('show'); 
    });

    
});