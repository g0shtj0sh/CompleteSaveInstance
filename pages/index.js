import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';
import data from '@site/src/csi/api-data.json';

export default function Home() {
  return (
    <Layout title="Developer hub" description="CompleteSaveInstance API Explorer, presets, and export diagnostics.">
      <main className="csi-home">
        <section className="csi-hero">
          <div>
            <div className="csi-release"><i/> v{data.version} <span>/</span> THE DEVELOPER HUB</div>
            <h1>Your place.<br />Every accessible<br /><span>detail.</span></h1>
            <p>A focused toolkit for Roblox instance archival. Explore the options, choose your configuration, and follow the evidence behind each export.</p>
            <div className="csi-actions">
              <Link className="button button--primary" to="/api/CompleteSaveInstance">Open API Explorer ↗</Link>
              <Link className="button button--outline" to="/docs/intro">Quick start →</Link>
            </div>
            <div className="csi-portal-stats"><div><strong>{data.options.length}</strong><span>API OPTIONS</span></div><div><strong>{data.presets.length}</strong><span>SCRIPT PRESETS</span></div><div><strong>Luau</strong><span>PRIMARY ENGINE</span></div></div>
          </div>
          <div className="csi-archive-visual"><div className="csi-orbit csi-orbit-one"/><div className="csi-orbit csi-orbit-two"/><img src={useBaseUrl('/logo.png')} width="340" height="340" alt="CompleteSaveInstance archive cube logo"/><div className="csi-visual-label"><i/> COMPLETE SAVE INSTANCE<span>INSTANCE ARCHIVAL / v{data.version}</span></div><div className="csi-visual-code"><span>01</span> local report = completeSaveInstance(options)<br/><span>02</span> <b>-- inspect the output in Studio</b></div></div>
        </section>
        <section className="csi-section">
          <div className="csi-section-label">01 — BUILD YOUR WORKFLOW</div><h2 className="csi-home-section-title">Everything in one workspace.</h2>
          <div className="csi-grid">
            <article><span className="csi-resource-icon">{'{ }'}</span><h2>API Explorer</h2><p>Search every setting. Compare defaults with preset values. Copy a configuration.</p><Link to="/api/CompleteSaveInstance">Explore {data.options.length} options ↗</Link></article>
            <article><span className="csi-resource-icon">⌘</span><h2>Script Presets</h2><p>Start with a purpose: diagnose, archive a map, inspect scripts, or push coverage with Ultra.</p><Link to="/docs/PRESETS">Choose your preset ↗</Link></article>
            <article><span className="csi-resource-icon">◈</span><h2>Export diagnostics</h2><p>Missing geometry? Read the report, identify omitted properties, and narrow down the cause.</p><Link to="/docs/GEOMETRY">Investigate the result ↗</Link></article>
          </div>
        </section>
        <section className="csi-section csi-focus">
          <div><div className="csi-eyebrow">IN DEVELOPMENT</div><h2>Go further with Ultra.</h2><code>UltraCompleteSveInstance</code><p>Full selection, special properties, scripts, and nil instances — with a diagnostic report to help identify gaps. Runtime compatibility and Studio results require testing.</p></div>
          <Link className="button button--outline" to="/docs/PRESETS#ultracompletesveinstance">Explore Ultra &rarr;</Link>
        </section>
        <div className="csi-section csi-note">For experiences you own or are authorized to archive. Public source under AGPL-3.0; inherited credits are preserved. Independent project with no Roblox affiliation.</div>
      </main>
    </Layout>
  );
}
