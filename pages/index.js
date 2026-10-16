import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';

export default function Home() {
  return (
    <Layout title="Roblox instance archival" description="CompleteSaveInstance API, preset catalog, and diagnostic guides for authorized Roblox instance archival.">
      <main className="csi-home">
        <section className="csi-hero">
          <div>
            <div className="csi-eyebrow">CompleteSaveInstance / Developer documentation</div>
            <h1>Accessible data.<br /><span>Visible limits.</span></h1>
            <p>Explore the API, choose a preset, and understand what your export actually contains. A clearer foundation for Roblox instance archival.</p>
            <div className="csi-actions">
              <Link className="button button--primary" to="/docs/intro">Get started</Link>
              <Link className="button button--outline" to="/api/CompleteSaveInstance">Explore the API &rarr;</Link>
            </div>
          </div>
          <img src={useBaseUrl('/logo.png')} width="390" height="390" alt="CompleteSaveInstance archive cube logo" />
        </section>
        <section className="csi-section">
          <div className="csi-section-label">Find your starting point</div>
          <div className="csi-grid">
            <article><h2>API reference</h2><p>Option types, defaults, aliases, and examples extracted directly from the primary Luau source.</p><Link to="/api/CompleteSaveInstance">Read the reference &rarr;</Link></article>
            <article><h2>Script Presets</h2><p>Four configurations for initial diagnosis, map content, authorized scripts, and maximum coverage.</p><Link to="/docs/PRESETS">Choose a preset &rarr;</Link></article>
            <article><h2>Evidence first</h2><p>Follow the file-writing checks and troubleshooting guide before treating an output as a usable backup.</p><Link to="/docs/TROUBLESHOOTING">Diagnose an export &rarr;</Link></article>
          </div>
        </section>
        <section className="csi-section csi-focus">
          <div><div className="csi-eyebrow">Current development target / Experimental</div><h2>UltraCompleteSveInstance</h2><p>The preset we are improving for the widest accessible place coverage. Full selection, advanced property access, scripts, and nil instances. Runtime compatibility and Studio results remain unverified.</p></div>
          <Link className="button button--outline" to="/docs/PRESETS#ultracompletesveinstance">Explore Ultra &rarr;</Link>
        </section>
        <div className="csi-section csi-note">For experiences you own or are authorized to archive. Public source under AGPL-3.0; inherited credits are preserved. Independent project with no Roblox affiliation.</div>
      </main>
    </Layout>
  );
}
