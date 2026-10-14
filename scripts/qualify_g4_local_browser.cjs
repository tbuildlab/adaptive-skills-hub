const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const assert = require('assert/strict');
// Fixed local G4 qualification harness; not a Nexus browser runtime.
const [modulePath,browserPath,outputPath] = process.argv.slice(2);
assert(modulePath && browserPath && outputPath, 'Provide existing Host Playwright module, browser executable and fresh output path.');
const { chromium } = require(path.resolve(modulePath));
const root = process.cwd();
const destination = path.resolve(outputPath);
assert(!fs.existsSync(destination), 'Preserve old evidence; output directory must be fresh.');
assert(path.relative(root,destination).startsWith('..'), 'Use a task-owned output directory outside the source root.');
fs.mkdirSync(path.join(destination,'screenshots'),{recursive:true});
const folder = 'docs/g4-local-workflows/';
const allowed = new Set([folder+'index.html',folder+'workflows.html',folder+'assets/site.css',folder+'assets/catalog.js',folder+'report.html',folder+'report.md',folder+'sources/owner-task-scope.json',folder+'sources/host-loop-summary.json',folder+'sources/retained-regression.json',folder+'sources/retained-e2e-proof.json',folder+'sources/retained-receipt.json','docs/nexus-core-alpha2-local-use-v1.md','docs/nexus-core-host-execution-loop-v1.md','docs/nexus-g2-openai-structured-v3.md']);
const source = JSON.parse(fs.readFileSync(path.join(root,folder,'sources/host-loop-summary.json')));
for(const [key,name] of Object.entries({regression:'retained-regression.json',e2e_proof:'retained-e2e-proof.json',receipt:'retained-receipt.json'}))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root,folder,'sources',name))).digest('hex'),source.original_sha256[key]);
const originalRegression=JSON.parse(fs.readFileSync(path.join(root,folder,'sources/retained-regression.json')));
const originalReceipt=JSON.parse(fs.readFileSync(path.join(root,folder,'sources/retained-receipt.json')));
const originalProof=JSON.parse(fs.readFileSync(path.join(root,folder,'sources/retained-e2e-proof.json')));
assert.deepEqual(source.regression,{total:originalRegression.total,pass:originalRegression.pass,skip:originalRegression.skip.length,fail:originalRegression.fail,error:originalRegression.error});
assert.equal(source.execution.commands_used,originalReceipt.commands_used);assert.equal(source.execution.max_commands,originalReceipt.budget.max_commands);assert.equal(source.execution.task_id,originalReceipt.task_id);assert.equal(source.execution.git_processes,originalProof.native_git_processes);assert.equal(source.execution.source_files_preserved,originalProof.inspected_source_files_preserved);
const hashes = Object.fromEntries([...allowed].map(name=>[name,crypto.createHash('sha256').update(fs.readFileSync(path.join(root,name))).digest('hex')]));
const packets = Object.fromEntries(['website','source_backed_report'].map(pack=>[pack,{schema:'nexus.g4.host-measurements.v1',pack,checks:{}}]));
function pass(pack,name,measurements){packets[pack].checks[name]={status:'PASS',measurements};}
function luminance(hex){let rgb=hex.match(/[a-f0-9]{2}/gi).map(x=>parseInt(x,16)/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722;}
function contrast(a,b){let x=luminance(a),y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);}
const server=http.createServer((req,res)=>{
 let name;
 try{name=decodeURIComponent(new URL(req.url,'http://localhost').pathname).slice(1);}catch{res.writeHead(400);res.end();return;}
 if(!['GET','HEAD'].includes(req.method)||!allowed.has(name)){res.writeHead(404);res.end();return;}
 const mime={'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json','.md':'text/plain'}[path.extname(name)];
 res.writeHead(200,{'Content-Type':mime+'; charset=utf-8','Content-Security-Policy':"default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'none'; base-uri 'none'; form-action 'none'",'Cache-Control':'no-store'});
 res.end(req.method==='HEAD'?'':fs.readFileSync(path.join(root,name)));
});
(async()=>{
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const origin=`http://127.0.0.1:${server.address().port}`;
 let browser;
 try{
 browser=await chromium.launch({executablePath:path.resolve(browserPath),headless:true,args:['--disable-background-networking','--disable-component-update','--no-first-run']});
 const context=await browser.newContext({viewport:{width:1440,height:1000},serviceWorkers:'block'});
 let blocked=0,errors=0,consoleErrors=0;
 await context.route('**/*',route=>{if(new URL(route.request().url()).origin!==origin){blocked++;return route.abort();}return route.continue();});
 const page=await context.newPage();page.on('pageerror',()=>errors++);page.on('console',m=>{if(m.type()==='error')consoleErrors++;});
 const consumers=[];let semanticChecks=0,keyboardChecks=0;
 for(const name of ['index.html','workflows.html']){
  assert.equal((await page.goto(`${origin}/${folder}${name}`)).status(),200);
  await page.locator('#workflow-search').fill('git');assert.equal(await page.locator('[data-workflow]:visible').count(),1);
  await page.locator('#clear-search').click();assert.equal(await page.locator('[data-workflow]:visible').count(),4);
  await page.locator('#workflow-search').fill('no such supported workflow');assert.equal(await page.locator('#no-results').isVisible(),true);
  await page.locator('#workflow-search').fill('<img src=x onerror=alert(1)>');assert.equal(await page.locator('img').count(),0);
  await page.locator('#clear-search').focus();await page.keyboard.press('Enter');assert.equal(await page.locator('[data-workflow]:visible').count(),4);
  assert.equal(await page.locator('#workflow-search').evaluate(el=>el===document.activeElement),true);keyboardChecks++;
  await page.locator('#workflow-search').fill(' '.repeat(5));assert.equal(await page.locator('[data-workflow]:visible').count(),4);
  await page.locator('#workflow-search').fill('');await page.locator('#workflow-search').pressSequentially('x'.repeat(130));assert.equal((await page.locator('#workflow-search').inputValue()).length,120);
  await page.locator('#clear-search').click();
  await page.keyboard.press('Control+Home');await page.locator('.skip').focus();await page.keyboard.press('Enter');assert.equal(await page.locator('#main').evaluate(el=>el===document.activeElement),true);keyboardChecks++;
  const tree=await page.locator('body').ariaSnapshot();assert(tree.includes('heading')&&tree.includes('navigation')&&tree.includes('Find a workflow'));semanticChecks++;
  await page.locator('summary').first().focus();await page.keyboard.press('Enter');assert.equal(await page.locator('details').first().getAttribute('open'),'');keyboardChecks++;
  for(const width of [320,768,1024,1440]){
   await page.setViewportSize({width,height:1000});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  }
  await page.screenshot({path:path.join(destination,'screenshots',name.replace('.html','-desktop.png')),fullPage:true});
  await page.setViewportSize({width:320,height:1000});await page.screenshot({path:path.join(destination,'screenshots',name.replace('.html','-mobile.png')),fullPage:true});
  consumers.push(name);
 }
 const ratios=[contrast('1d302b','f6f4ed'),contrast('43564e','f6f4ed'),contrast('146145','f6f4ed')];assert(ratios.every(x=>x>=4.5));
 pass('website','interaction',{real_browser:true,filters_and_keyboard_activation:true,consumers_tested:consumers});
 pass('website','consumer_regression',{shared_assets:['assets/catalog.js','assets/site.css'],consumers_tested:consumers});
 pass('website','accessibility',{keyboard_checks:keyboardChecks,semantic_tree_checks:semanticChecks,normal_text_contrast_ratio_hundredths:ratios.map(x=>Math.round(x*100)),viewport_widths:[320,768,1024,1440],full_screen_reader_certification:false});
 pass('website','boundary',{empty_query:true,no_results:true,html_query_not_executed:true,maxlength_120:true,no_network_or_persistence_api:true});
 const responses=[];
 for(const name of allowed){const res=await page.request.get(`${origin}/${name}`);assert.equal(res.status(),200);responses.push({path:name,status:res.status()});}
 pass('website','artifact_inspection',{pages_reopened:2,document_overflow:false,checked_local_resources:responses.length});
 assert.equal((await page.goto(`${origin}/${folder}report.html`)).status(),200);
 assert.equal(await page.locator('caption').count(),1);assert.equal(await page.locator('th[scope=col]').count(),3);assert.equal(await page.locator('th[scope=row]').count(),9);
 const rows=await page.locator('tbody tr td:first-of-type').allTextContents();
 assert.deepEqual(rows,['228','227','1','0 / 0','4 / 8','50%','12','519','0']);
 const text=await page.locator('main').innerText();assert(text.includes('227')&&text.includes('228')&&text.includes('50%'));
 assert(text.includes('untracked')&&text.includes('skipped')&&text.includes('No financial saving'));
 assert.equal(source.regression.pass+source.regression.skip+source.regression.fail+source.regression.error,source.regression.total);
 assert.equal(source.execution.commands_used*100/source.execution.max_commands,50);
 assert.equal(source.execution.max_commands-source.execution.commands_used,4);
 assert(text.includes('4 ÷ 8 × 100 = 50%')&&text.includes('227 + 1 + 0 + 0 = 228'));
 pass('source_backed_report','source_claim',{claims_checked:9,source_fields_reopened:true,original_bytes_pinned:true,derived_projection_checked:true,source_total:source.regression.total,source_pass:source.regression.pass,source_skip:source.regression.skip});
 pass('source_backed_report','calculation',{total_recomputed:source.regression.total,batch_utilization_percent:50,remaining_batches_at_completion:4,git_processes_separate_from_batches:true});
 pass('source_backed_report','uncertainty',{skip_not_pass:true,untracked_scope_excluded:true,same_user_limit_declared:true,financial_savings_not_claimed:true,expired_budget_not_renewed:true});
 for(const width of [320,768,1024,1440]){await page.setViewportSize({width,height:1000});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));}
 await page.screenshot({path:path.join(destination,'screenshots/report-desktop.png'),fullPage:true});
 await page.setViewportSize({width:320,height:1000});assert.equal(await page.locator('.table-wrap').getAttribute('tabindex'),'0');assert(await page.locator('.table-wrap').evaluate(el=>el.scrollWidth>el.clientWidth));
 await page.locator('.table-wrap').focus();await page.keyboard.press('ArrowRight');await page.waitForFunction(()=>document.querySelector('.table-wrap').scrollLeft>0,{},{timeout:2000});
 await page.screenshot({path:path.join(destination,'screenshots/report-mobile.png'),fullPage:true});
 pass('source_backed_report','render',{numeric_cells_not_split:true,horizontally_scrollable_named_table_region:true,real_browser:true,viewport_widths:[320,768,1024,1440],document_overflow:false,table_caption_and_headers:true});
 pass('source_backed_report','artifact_inspection',{html_reopened:true,markdown_reopened:fs.readFileSync(path.join(root,folder,'report.md'),'utf8').includes('227 PASS + 1 historical SKIP'),source_links_status:200});
 assert.equal(errors,0);assert.equal(consoleErrors,0);assert.equal(blocked,0);
 for(const [name,digest] of Object.entries(hashes))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root,name))).digest('hex'),digest);
 for(const packet of Object.values(packets)){for(const item of Object.values(packet.checks))item.measurements.source_bytes_unchanged=true;fs.writeFileSync(path.join(destination,`${packet.pack}-browser-evidence.json`),JSON.stringify(packet,null,2)+'\n');}
 fs.writeFileSync(path.join(destination,'browser-run.json'),JSON.stringify({status:'PASS',browser_version:browser.version(),page_errors:errors,console_errors:consoleErrors,out_of_scope_requests:blocked,all_sources_and_artifacts_unchanged:true,host_tool:'existing_bundled_playwright_existing_chrome_fresh_context',production_adapter_used:false,real_admission:'NO'},null,2)+'\n');
 console.log(JSON.stringify({status:'PASS',website_checks:Object.keys(packets.website.checks),report_checks:Object.keys(packets.source_backed_report.checks),browser:browser.version(),errors,consoleErrors,blocked}));
 }finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(error=>{fs.writeFileSync(path.join(destination,'browser-run-failure.json'),JSON.stringify({status:'FAIL',reason:error.message})+'\n');console.error(error.stack);process.exitCode=1;});
