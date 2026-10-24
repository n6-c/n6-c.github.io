// Screenshots a list of jobs with Playwright: node tools/midia/render.cjs jobs.json
// job: {url, out, w, h, dsf?, quality?, wait?}  (out .jpg -> JPEG, .png -> PNG)
const PW = process.env.PLAYWRIGHT || '/Users/macos/Documents/Developer/acesa/node_modules/playwright';
const { chromium } = require(PW);
const jobs = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
(async () => {
  const b = await chromium.launch();
  const ctxs = {};
  for (const j of jobs) {
    const key = `${j.w}x${j.h}@${j.dsf || 1}`;
    if (!ctxs[key]) ctxs[key] = await b.newContext({ viewport: { width: j.w, height: j.h }, deviceScaleFactor: j.dsf || 1, locale: 'pt-BR' });
    const p = await ctxs[key].newPage();
    await p.goto(j.url, { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(j.wait || 150);
    const jpg = j.out.endsWith('.jpg');
    await p.screenshot({ path: j.out, type: jpg ? 'jpeg' : 'png', quality: jpg ? (j.quality || 88) : undefined });
    await p.close();
  }
  await b.close();
  console.log('rendered', jobs.length);
})().catch(e => { console.error(e); process.exit(1); });
