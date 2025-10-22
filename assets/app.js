async function loadResult(){
  const out = document.getElementById('output');
  try{
    const resp = await fetch('/result.json', {cache: 'no-store'});
    if(!resp.ok){
      out.textContent = `Could not fetch result.json (HTTP ${resp.status}).\nEnsure CI has run and Pages deployed the file.`;
      return;
    }
    const data = await resp.json();
    out.textContent = JSON.stringify(data, null, 2);
  }catch(e){
    out.textContent = "Error fetching result.json: " + e;
  }
}
loadResult();
