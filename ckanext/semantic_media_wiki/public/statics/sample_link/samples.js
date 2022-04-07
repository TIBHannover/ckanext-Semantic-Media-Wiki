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
      let all_visible = false;
      let allSampleBoxes = $('.sample-box');
      console.info(allSampleBoxes);
      for(let i=1; i <= allSampleBoxes.length; i++){
        console.info($(allSampleBoxes[i]).attr('id'));
        if ($(allSampleBoxes[i]).is(':hidden')){
          $(allSampleBoxes[i]).fadeIn();
          all_visible = true;
          break;
        }
      }
      if(!all_visible){
        $(this).hide();
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

    $('#sample_save_btn').click(function(){
      $('#sample-save-btn-spinner').css("display","inline-block");
    });

    
});