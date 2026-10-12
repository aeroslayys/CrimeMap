import { useState } from 'react';
import { CheckCircle2, DatabaseZap, RefreshCw, ShieldAlert } from 'lucide-react';
import { applyDemoRedistribution, previewDemoRedistribution } from '../../api';

/** Never runs a migration on mount. Only an administrator can explicitly apply. */
export default function DemoRedistributionPanel({ onUpdated }) {
  const [preview, setPreview] = useState(null);
  const [confirmed, setConfirmed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  async function inspect() {
    setBusy(true);
    setError('');
    setSuccess('');
    setConfirmed(false);
    try {
      setPreview(await previewDemoRedistribution());
    } catch (reason) {
      setError(reason.message || 'Could not check stored demo locations.');
    } finally {
      setBusy(false);
    }
  }

  async function apply() {
    if (!confirmed || !preview?.ready_to_move || busy) return;
    setBusy(true);
    setError('');
    try {
      const result = await applyDemoRedistribution();
      setConfirmed(false);
      setPreview(null);
      setSuccess(`Updated ${result.updated} canonical synthetic incident locations. ${result.skipped_custom} modified or unrecognized demo IDs skipped. No imported or user-created records changed.`);
      onUpdated?.();
    } catch (reason) {
      setError(reason.message || 'Could not redistribute demo locations.');
    } finally {
      setBusy(false);
    }
  }

  return <details className="panel demo-redistribution">
    <summary><DatabaseZap size={18} /> Administrator · Spread existing demo incidents</summary>
    <p>The downloaded sample and map code do not move records already saved in Cloud SQL. Check how many original <code>DEMO-0001</code>–<code>DEMO-0100</code> incidents still use previous coordinates, then explicitly update those unchanged records only. Other incidents and edited coordinates are preserved.</p>
    <button type="button" className="button subtle" onClick={inspect} disabled={busy}>
      <RefreshCw size={16} /> {busy ? 'Checking…' : preview ? 'Recheck demo coordinates' : 'Preview database changes'}
    </button>
    {preview && <div className="demo-redistribution-counts" role="status">
      <span><strong>{preview.ready_to_move}</strong> unchanged seed pins ready to spread</span>
      <span><strong>{preview.already_current}</strong> already distributed</span>
      <span><strong>{preview.skipped_custom}</strong> edited/unrecognized IDs skipped</span>
      <span><strong>{preview.missing}</strong> missing IDs</span>
    </div>}
    {preview?.ready_to_move > 0 && <div className="demo-redistribution-confirm">
      <label><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} disabled={busy} />
        I reviewed the preview and have a database backup. Update only the original unchanged fictional DEMO coordinates.
      </label>
      <button type="button" className="button primary" onClick={apply} disabled={!confirmed || busy}>
        <DatabaseZap size={16} /> {busy ? 'Applying…' : `Spread ${preview.ready_to_move} demo incidents`}
      </button>
    </div>}
    {preview?.ready_to_move === 0 && <p className="demo-redistribution-ok"><CheckCircle2 size={17} /> No original demo coordinates require redistribution.</p>}
    {success && <p className="demo-redistribution-ok" role="status"><CheckCircle2 size={17} /> {success}</p>}
    {error && <p className="demo-redistribution-error" role="alert"><ShieldAlert size={17} /> {error}</p>}
    <small>Synthetic demonstration data only. This cannot migrate imported UUID incidents, reset accounts, or change record status and descriptions.</small>
  </details>;
}
