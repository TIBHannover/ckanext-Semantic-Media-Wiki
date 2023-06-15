function formatState (state) {
    if (!state.id) {
      return $.trim(state.text);
    }    
    let image_url = $("div[value='" + $.trim(state.text) + "']").text(); 
    if(image_url === 'None' || image_url === ''){
      if(state.id !== '0'){
        let $state = $.trim(state.text) + '<br><div class="no-image-available">No Image Available</div><br>';
        return $state;
      }
      let $state = $.trim(state.text) + '<br><br>';
      return $state;
    }   
    var $state = $(
      '<span>' + $.trim(state.text) + '<br><img src="' + $.trim(image_url) + '"' + 'class="responsive">' + '</span>'
    );
    return $state;
  };

$(document).ready(function(){
         
    $("select.machine_dropdown").select2({
        formatResult: formatState
      });
    
      /**
       * Show the modal when a machine selected
       * 
       */
    $('.machine_dropdown').change(function(){
        let id = $(this).attr('id');
        id = id[id.length - 1];
        $('#machine_name_' + id).val($.trim($(this).select2('data').text));   
        $('#modalMachineName' + id).text($.trim($(this).select2('data').text));
        $('#resourcesModal' + id).modal({
          backdrop: 'static',
          keyboard: false
         });
        $('#resourcesModal' + id).modal('show');                   
    }); 

    /**
     * Add another machine selection box
     * 
     */
    $('#machine_box_id_1').show();
    $('#add-another-machine-box').click(function(){
      let all_visible = false;
      for(let i=1; i <= $('.machine-box').length; i++){
        if ($('#machine_box_id_' + i).is(':hidden')){
          $('#machine_box_id_' + i).fadeIn();
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
          $('#machine_resource_count-' + id).text(resourceCount);
          $('#machine_resource_count-message-box_' + id).show();
        }
        else{
          $('#machine_resource_count-' + id).text(0);
          $('#machine_resource_count-message-box_' + id).hide();
          $("#machines_dropdown_" + id).select2("val", "0"); // none selected
        }
    });

    /**
     * remove machine
     * 
     */
    $('.machine-remove-anchor').click(function(){
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
        $('#machine_resource_count-' + id).text('0');
        $('#machine_resource_count-message-box_' + id).hide();
        $('#machine_box_id_' + id).fadeOut();
        
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


    $('#machine-form').submit(function(e){
      $('#next-step-loadin-animation').css('display', 'inline-block');      
  });

    
});