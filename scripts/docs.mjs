// Adapt the pinned Moonwave build through its configuration, without patching dependencies.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
import { prepareProject } from '../node_modules/moonwave/dist/prepareProject.js';
import { getBinaryPath } from '../node_modules/moonwave/dist/binary.js';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
process.chdir(root);
const mode = process.argv[2] || 'build';
if (!['build', 'dev'].includes(mode)) throw new Error('Expected build or dev');
const run = (exe, args, cwd=root) => new Promise((resolve, reject) => {
  const child = spawn(exe, args, {cwd, stdio: 'inherit'});
  child.on('error', reject);
  child.on('exit', code => code === 0 ? resolve() : reject(new Error(`${exe} exited with ${code}`)));
});
await run('python', ['scripts/generate_option_index.py', '--check']);
const {tempDir} = prepareProject(root, {
  codePaths: ['saveinstance.luau'], fresh: true, binaryPath: await getBinaryPath(),
});
const componentDir = path.join(tempDir, 'src', 'csp');
await fs.cp(path.join(root, 'website'), componentDir, {recursive: true});
const configPath = path.join(tempDir, 'docusaurus.config.js');
const originalConfig = await fs.readFile(configPath, 'utf8');
const alias = path.join(tempDir, 'node_modules/docusaurus-plugin-moonwave/src/components/LuaClass.js') + '$';
const replacement = path.join(componentDir, 'ApiReference.jsx');
await fs.writeFile(configPath, originalConfig + `;
module.exports.themeConfig.colorMode = {defaultMode: 'dark', disableSwitch: true, respectPrefersColorScheme: false};
module.exports.plugins.push(function cspApiExplorer() {
  return {name: 'csp-api-explorer', configureWebpack() {
    return {resolve: {alias: {${JSON.stringify(alias)}: ${JSON.stringify(replacement)}}}};
  }};
});
`);
const cli = path.join(tempDir, 'node_modules/@docusaurus/core/bin/docusaurus.mjs');
await run(process.execPath, [cli, 'swizzle', 'docusaurus-lunr-search', 'SearchBar', '--eject', '--danger'], tempDir);
await run(process.execPath, [cli, mode === 'build' ? 'build' : 'start',
  ...(mode === 'build' ? ['--out-dir', path.join(root, 'build')] : [])], tempDir);
