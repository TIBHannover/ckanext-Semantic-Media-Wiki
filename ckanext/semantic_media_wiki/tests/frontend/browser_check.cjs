// Integration fixture using CKAN’s actual bundled jQuery, Bootstrap and Select2.
const http = require('node:http');
const fs = require('node:fs');
const {spawn} = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '../..') + '/';
const vendor = process.argv[2];
const browserPath = process.argv[3];
if (!vendor || !browserPath) {
    console.error('Usage: node browser_check.cjs CKAN_VENDOR_DIRECTORY CHROME_EXECUTABLE');
    process.exit(1);
}
const options = ['A0001', 'X0005', 'X0006', 'X0008', 'X0010', 'X0011', 'X0012', 'B0045'].map(text => ({value: 'https://wiki/' + text, text}));
function row(i, value='0') {return `<input type="hidden" id="sample_name_${i}" name="sample_name_${i}" value="A0001"><div class="row sample-box" id="sample_box_id_${i}"><input type="hidden" class="sample_dropdown" id="samples_dropdown_${i}" name="sample_link${i}" value="${value}" data-sample-text="A0001"><div id="resourcesModal${i}" class="modal"><div id="modalSampleName${i}"></div><input type="checkbox" id="select-all-resources-${i}" class="select-all-resources"><input type="checkbox" class="resource-box resource-checkbox-input${i}" name="sample_resources_list${i}" value="r1" data-resource-name="Resource 1" ${i===1?'checked':''}><input type="checkbox" class="resource-box resource-checkbox-input${i}" name="sample_resources_list${i}" value="r2" data-resource-name="Resource 2"><button type="button" id="ref_modal_add_btn${i}" class="refModalAdd">Save</button></div><div><div id="sample_resource_count-message-box_${i}"><span id="sample_resource_names-${i}"></span><i class="resource_count_edit" id="sample_resource_count_edit_${i}"></i></div></div><a href="#" class="sample-remove-anchor" id="sample-remove-anchor${i}">Remove</a></div>`;}
const html = `<!doctype html><html><head><style>.sample-box{display:none}.modal{display:none}</style></head><body><form id="sample-form"><input id="sample_count" name="sample_count" value="33" type="hidden"><input id="isEditMode" value="1" type="hidden"><input id="existed_samples_dropdown" value="1" type="hidden"><fieldset id="sample-range" hidden><input type="hidden" id="sample-range-from" data-placeholder="From"><input type="hidden" id="sample-range-to" data-placeholder="To"><select multiple id="sample-range-resources"><option value="r1">Resource 1</option><option value="r2">Resource 2</option></select><button type="button" id="sample-range-add">Add range</button><button type="button" id="sample-range-clear">Clear</button><p id="sample-range-message"></p></fieldset><script type="application/json" id="sample-options">${JSON.stringify(options)}</script>${row(1,options[0].value)}${Array.from({length:31},(_,i)=>row(i+2)).join('')}<button type="button" id="add-another-sample-box">Another</button></form><script src="/jquery.js"></script><script src="/bootstrap.js"></script><script src="/select2/select2.js"></script><script src="/sample_range.js"></script><script src="/samples.js"></script><script>
window.addEventListener('error', function(e){ fetch('/result',{method:'POST',body:'ERROR '+e.message}); });
$(function(){setTimeout(function(){try {
 const assert=(condition,message)=>{if(!condition)throw new Error(message);};
 const u=n=>'https://wiki/'+n;
 assert($('#samples_dropdown_1').select2('data').text==='A0001','existing label');
 $('#sample-range-add').click();
 assert($('.sample-box').length===32,'empty range changed rows');
 $('#sample-range-from').select2('data',{id:u('X0005'),text:'X0005'});
 $('#sample-range-to').select2('data',{id:u('X0012'),text:'X0012'});
 $('#sample-range-resources').select2('val',['r1']);
 $('#sample-range-add').click();
 assert($('.sample-box').length===38,'range row count '+$('.sample-box').length);
 assert($('#sample_count').val()==='39','count includes last row');
 const selected=()=>$('.sample_dropdown').map(function(){return this.value;}).get().filter(x=>x!=='0'&&x!=='');
 assert(selected().length===7,'selected range plus existing');
 assert(!selected().includes(u('X0007')),'fabricated ID');
 $('#sample-range-add').click();
 assert($('.sample-box').length===38,'duplicate rows');
 $('#sample-range-resources').select2('val',['r2']);
 $('#sample-range-add').click();
 assert($('#sample_box_id_33 .resource-box:checked').length===2,'merge resources');
 const values=$('#sample-form').serializeArray();
 assert(values.some(v=>v.name==='sample_link38'&&v.value===u('X0012')),'last URL submission');
 assert(values.some(v=>v.name==='sample_name_38'&&v.value==='X0012'),'last name submission');
 assert(values.filter(v=>v.name==='sample_resources_list38').length===2,'resource submission');
 $('#samples_dropdown_33').select2('data',{id:u('B0045'),text:'B0045'},true);
 assert($('#sample_name_33').val()==='B0045','manual edit of generated row');
 $('#sample-remove-anchor33').click();
 assert($('#samples_dropdown_33').val()==='0','remove generated row');
 assert($('#sample_box_id_33 .resource-box:checked').length===0,'remove resource choices');
 $('#sample-range-clear').click();
 assert(!$('#sample-range-from').val()&&!$('#sample-range-to').val(),'clear endpoints');
 assert(selected().includes(u('A0001')),'clear preserved stored selection');
 fetch('/result',{method:'POST',body:'PASS: existing selections, empty range, inclusive range, duplicates, resource merge, numbered submission, manual editing/removal and clear'});
} catch(e){fetch('/result',{method:'POST',body:'FAIL '+e.stack});}},100);});
</script></body></html>`;
let browser;
const profile = fs.mkdtempSync('/tmp/smw-chrome-');
process.on('exit', () => { browser?.kill(); fs.rmSync(profile, {recursive: true, force: true}); });
const server=http.createServer((req,res)=>{
 if(req.url==='/result'){let body=''; req.on('data',b=>body+=b);req.on('end',()=>{console.log(body);res.end('ok');process.exitCode=body.startsWith('PASS')?0:1; browser.kill();server.close();clearTimeout(timer);});return;}
 if(req.url==='/favicon.ico'){res.writeHead(204);res.end();return;}
 let data;
 if(req.url==='/')data=html;
 else if(['/samples.js','/sample_range.js'].includes(req.url))data=fs.readFileSync(root+'public/statics/sample_link'+req.url);
 else data=fs.readFileSync(vendor+req.url);
 res.end(data);
});
const timer=setTimeout(()=>{console.error('Browser timed out');browser?.kill();server.close();process.exitCode=1;},25000);
server.listen(0,'127.0.0.1',()=>{
 browser=spawn(browserPath,['--headless','--no-sandbox','--disable-gpu','--user-data-dir='+profile,'http://127.0.0.1:'+server.address().port],{stdio:['ignore','ignore','pipe']});
 browser.stderr.on('data',b=>process.stderr.write(b));
});
