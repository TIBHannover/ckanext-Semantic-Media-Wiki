$(document).ready(function(){
    
    $('#protocol-add-form').submit(function(e){        
        validateFormBasedOnField('#protocol_name', e);
        validateFormBasedOnField('#protocol_url', e);    
    });



    $('#protocol_name').keydown(function(){
        $('#protocol_add_alert_box').hide();
        $(this).css('border', '');        
    });

    $('#protocol_name').change(function(){
        $('#protocol_add_alert_box').hide();        
        $(this).css('border', '');
    });

    $('#protocol_url').keydown(function(){
        $('#protocol_add_alert_box').hide();        
        $(this).css('border', '');
    });

    $('#protocol_url').change(function(){
        $('#protocol_add_alert_box').hide();        
        $(this).css('border', '');
    });


    $("#protocolModal").on("hidden.bs.modal", function(){
        resetField('#protocol_name');
        resetField('#protocol_url');
        $('#protocol_add_alert_box').hide();         
    });



});



function validateFormBasedOnField(fieldId, formEvent){
    let field = $(fieldId);
    if(field.val() === ''){
        field.css('border', '2px solid red');
        $('#protocol_add_alert_box').show();
        formEvent.preventDefault();
    }
}


function resetField(id){
    $(id).val('');
    $(id).css('border', '');
}