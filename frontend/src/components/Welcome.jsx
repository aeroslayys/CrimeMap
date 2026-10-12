import { ArrowRight, BarChart3, CheckCircle2, ClipboardCheck, Eye, FileDown, LockKeyhole, MapPinned, ShieldCheck, Sparkles } from 'lucide-react';
import ThemeToggle from './ThemeToggle.jsx';
import './Welcome.css';

const CAPABILITIES = [
  { Icon: MapPinned, index: '01', heading: 'See patterns on a map',
    description: 'Move from a list of fictional incidents to location markers, heatmaps and comparable spatial grids — with the underlying records always visible.' },
  { Icon: BarChart3, index: '02', heading: 'Turn records into context',
    description: 'Filter fictional incidents by category, time, status and demonstration zone. Explore distributions without pretending descriptive counts predict crime.' },
  { Icon: ClipboardCheck, index: '03', heading: 'Follow up on actions',
    description: 'Create human-reviewed prevention plans, record progress, and compare observed incident counts. A completed plan is not proof of effectiveness.' },
];

export default function Welcome({ onSignIn, onOpenWorkspace, theme, onToggleTheme, embedded = false }) {
  const enter = embedded ? onOpenWorkspace : onSignIn;
  return (
    <div className={`welcome-page ${embedded ? 'welcome-embedded' : ''}`}>
      {!embedded && <header className="welcome-topbar">
        <a href="#welcome-top" className="welcome-brand" aria-label="CrimeMap overview">
          <MapPinned size={25} aria-hidden="true" />
          <span>Crime<span className="welcome-brand-accent">Map</span></span>
        </a>
        <nav className="welcome-toplinks" aria-label="Landing navigation">
          <a href="#welcome-benefits">Why CrimeMap</a>
          <a href="#welcome-roadmap">What's next</a>
          <ThemeToggle theme={theme} onToggle={onToggleTheme} className="welcome-theme-toggle" />
          <button type="button" className="welcome-signin" onClick={enter}><LockKeyhole size={16}/> Sign in</button>
        </nav>
      </header>}
      <div id="welcome-top" className="welcome-body" role={embedded ? undefined : "main"}>
        <section className="welcome-hero" aria-labelledby="welcome-title">
          <div className="welcome-hero-copy">
            <div className="welcome-eyebrow"><span className="welcome-live-dot" /> PUDUCHERRY · GEOSPATIAL DECISION-SUPPORT DEMO</div>
            <h1 id="welcome-title">From incident records to <span>clearer decisions.</span></h1>
            <p className="welcome-lead">CrimeMap connects fictional incident records, interactive maps, analytics and human-reviewed prevention planning in one workspace — so a team can explore <strong>where issues cluster, how they change, and what actions were documented.</strong></p>
            <div className="welcome-cta-row">
              <button type="button" className="welcome-cta-primary" onClick={enter}>
                {embedded ? 'Open incident workspace' : 'Sign in to CrimeMap'} <ArrowRight size={18}/>
              </button>
              <a className="welcome-cta-secondary" href="#welcome-benefits">Explore capabilities <ArrowRight size={16}/></a>
            </div>
            <p className="welcome-synthetic"><ShieldCheck size={17}/> Hackathon prototype · 100% synthetic examples · No real police or complaint data</p>
          </div>
          <div className="welcome-visual" aria-label="Illustration of connected incident, map, analytics and prevention workflows">
            <div className="welcome-visual-cap">ONE CONNECTED WORKFLOW</div>
            <div className="welcome-flow-step"><span className="welcome-flow-symbol"><FileDown size={22}/></span><span><b>Record</b><small>Validated fictional reports</small></span><CheckCircle2 size={18}/></div>
            <div className="welcome-flow-track" aria-hidden="true"/>
            <div className="welcome-flow-step"><span className="welcome-flow-symbol"><MapPinned size={22}/></span><span><b>Map & analyse</b><small>Spatial patterns and time trends</small></span><CheckCircle2 size={18}/></div>
            <div className="welcome-flow-track" aria-hidden="true"/>
            <div className="welcome-flow-step"><span className="welcome-flow-symbol"><ClipboardCheck size={22}/></span><span><b>Plan & review</b><small>Human decisions, saved actions</small></span><CheckCircle2 size={18}/></div>
            <div className="welcome-visual-footer">Explore the evidence. Keep people in control.</div>
          </div>
        </section>

        <section className="welcome-content-section" id="welcome-benefits" aria-labelledby="welcome-benefits-title">
          <div className="welcome-section-header"><span className="welcome-kicker">WHY CRIMEMAP?</span><h2 id="welcome-benefits-title">More useful than scattered spreadsheets and maps.</h2>
            <p>CrimeMap puts exploration, recording and follow-up side by side. Its strength is linking each visual to the underlying fictional data and documenting what people decide to do next.</p></div>
          <div className="welcome-benefit-grid">{CAPABILITIES.map(({ Icon, index, heading, description }) => <article key={index} className="welcome-benefit">
            <span className="welcome-benefit-icon"><Icon size={22}/></span><span className="welcome-benefit-index">{index}</span>
            <h3>{heading}</h3><p>{description}</p>
          </article>)}</div>
        </section>

        <section className="welcome-proof" aria-label="Responsible design decisions">
          <div><Eye size={21}/><strong>Explainable</strong><span>Review the records behind each count.</span></div>
          <div><LockKeyhole size={21}/><strong>Role-aware</strong><span>Separate read-only, editing and administration.</span></div>
          <div><FileDown size={21}/><strong>Presentable</strong><span>Export combined PDF reports for review.</span></div>
        </section>

        <section className="welcome-roadmap" id="welcome-roadmap" aria-labelledby="welcome-roadmap-title">
          <div className="welcome-roadmap-heading"><span className="welcome-kicker">FUTURE DIRECTION · NOT YET IMPLEMENTED</span><h2 id="welcome-roadmap-title">What if residents could follow a complaint's progress?</h2>
            <p>Today, CrimeMap manages <strong>synthetic incident statuses and internal prevention plans</strong>. A possible future citizen-facing module could help someone who filed a complaint see the next verified step without repeatedly contacting a station. <strong>There is no public complaint portal or real-case lookup in this demo.</strong></p>
            <ul className="welcome-roadmap-list">
              <li>Private case reference and identity verification before displaying any details.</li>
              <li>Updates such as <b>received → assigned → under review → resolved</b>, with timestamps and authorized notes.</li>
              <li>Clear distinction between a staff update and a citizen-visible notification, with privacy and accessibility safeguards.</li>
            </ul>
          </div>
          <div className="welcome-future-card"><span className="welcome-future-icon"><Sparkles size={20}/></span>
            <span className="welcome-future-label">CONCEPT PREVIEW — NO LIVE CASES</span>
            <h3>Complaint progress</h3>
            <div className="welcome-future-timeline" aria-hidden="true">
              <div className="done"><i/> Received <span>01</span></div>
              <div className="done"><i/> Assigned <span>02</span></div>
              <div><i/> Under review <span>03</span></div>
              <div><i/> Resolved <span>04</span></div>
            </div>
            <p>Illustrative workflow only. This is not a real complaint, tracking code or promise of police response.</p>
          </div>
        </section>
        <footer className="welcome-footer">
          <span>CrimeMap · Hackathon demonstration · All incidents and locations are fictional.</span>
          {!embedded && <button type="button" onClick={enter}>Continue to sign in <ArrowRight size={15}/></button>}
        </footer>
      </div>
    </div>
  );
}
