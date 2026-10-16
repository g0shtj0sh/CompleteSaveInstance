import React, {useState} from 'react';
import data from './api-data.json';

export function loader(id, profile='Universal') {
  const folder=profile==='Potassium'?'Executors/Potassium/Script%20Presets':'Script%20Presets';
  return 'loadstring(game:HttpGet(\n    "https://raw.githubusercontent.com/g0shtj0sh/CompleteSaveInstance/v'+data.version+'/'+folder+'/'+id+'.luau",\n    true\n))()';
}

export default function PresetLauncher({id, initialProfile='Universal', compact=false, onProfileChange}) {
  const [profile,setProfile]=useState(initialProfile);
  const [feedback,setFeedback]=useState('');
  const [failed,setFailed]=useState(false);
  const script=loader(id,profile);
  function choose(p) {setProfile(p);setFeedback('');setFailed(false);onProfileChange?.(p);}
  async function copy() {
    try {
      await navigator.clipboard.writeText(script);
      setFeedback('Copié !');setFailed(false);
    } catch {
      setFeedback('Copie indisponible : sélectionne le script ci-dessous.');setFailed(true);
    }
    setTimeout(()=>setFeedback(''),3000);
  }
  return <div className={'csi-launcher '+(compact?'csi-launcher-compact':'')} data-preset={id} data-profile={profile}>
    <div className="csi-launcher-top"><span>RUN THIS PRESET <small>v{data.version}</small></span><div className="csi-profile-picker" aria-label={'Executor profile for '+id}>{data.profiles.map(p=><button type="button" key={p} aria-pressed={profile===p} onClick={()=>choose(p)}>{p}</button>)}</div></div>
    <pre tabIndex="0" aria-label={profile+' '+id+' runnable script'}><code>{script}</code></pre>
    <div className="csi-launcher-bottom"><button type="button" className="csi-launch-copy" aria-label={'Copier le script '+profile+' '+id} onClick={copy}>{feedback==='Copié !'?feedback:'Copier le script'} <span aria-hidden="true">⧉</span></button><span className="csi-launch-feedback" role="status">{feedback==='Copié !'?'Prêt à coller dans ton exécuteur.':feedback}</span></div>
    {failed&&<textarea readOnly aria-label="Script à copier manuellement" value={script} onFocus={e=>e.target.select()}/>}
  </div>;
}
