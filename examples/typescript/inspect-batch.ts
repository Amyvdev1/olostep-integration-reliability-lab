// Node 24: node examples/typescript/inspect-batch.ts BATCH_ID
// Single read only; the complete retry and pagination workflow is in Python.
const key = process.env.OLOSTEP_API_KEY;
const batch = process.argv[2];
if (!key || !batch || !/^[\w-]+$/.test(batch)) {
  console.error('Set OLOSTEP_API_KEY privately and supply a batch ID.');
  process.exitCode = 2;
} else {
  try {
    const response = await fetch(`https://api.olostep.com/v1/batches/${batch}`, {
      headers: { Authorization: `Bearer ${key}` }, redirect: 'error',
      signal: AbortSignal.timeout(10000)
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json() as {status?: string};
    console.log({status: data.status ?? 'unknown'});
  } catch {
    console.error('Read failed. Verify credentials, batch ID and connectivity.');
    process.exitCode = 2;
  }
}
export {};
