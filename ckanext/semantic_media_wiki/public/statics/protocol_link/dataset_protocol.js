$(document).ready(function(){
    let dest_url = $('#dataset_protocol_link').val();
    get_protocol_link($('#protocolRowInTable') ,dest_url);
});

function get_protocol_link(target, url){    
    $.ajax({
        url: url,
        cache:false,   
        dataType: 'json',     
        type: "GET",
        success: function(result){              
            if(result){
                let block = ''; 
                Object.entries(result).map(([key, value]) => {
                    block += buildPortocolTag(value, key);
                });            
                $(target).append(block);
                $('.protocol-link').fadeIn();
            }           
        }
    });
}

function buildPortocolTag(url, name){
    let protocolName = '<div class="protocol-name-tag">' + name + '</div>';
    let anchor = '<a href="' + url + '" target="_blank" class="protocol-link">' + protocolName + '</a>';
    return '<span>' + anchor + '</span>';

}