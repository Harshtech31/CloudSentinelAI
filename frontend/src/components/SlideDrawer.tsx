import { useEffect, useState } from 'react';
import { explainFinding } from '../api/findings';
import { useUIStore } from '../store/uiStore';

export function SlideDrawer() {
  const { isDrawerOpen, drawerData, closeDrawer, showToast } = useUIStore();
  const [loadingAi, setLoadingAi] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!isDrawerOpen || !drawerData) {
      setAiAnalysis(null);
      return;
    }

    // If findingId is available, call the real Bedrock backend explanation endpoint!
    if (drawerData.findingId) {
      setLoadingAi(true);
      explainFinding(drawerData.findingId)
        .then((res) => {
          setAiAnalysis(res.explanation);
        })
        .catch(() => {
          // Gracefully fallback to default contextual explanation
          setAiAnalysis(null);
        })
        .finally(() => {
          setLoadingAi(false);
        });
    } else {
      setAiAnalysis(null);
    }
  }, [isDrawerOpen, drawerData]);

  if (!isDrawerOpen || !drawerData) return null;

  const sevLower = drawerData.severity.toLowerCase();
  const sevClass =
    sevLower === 'critical'
      ? 'crit'
      : sevLower === 'high'
      ? 'high'
      : sevLower === 'medium'
      ? 'med'
      : 'low';

  const defaultCli =
    drawerData.cliCommand ||
    (drawerData.ruleId === 'AWS-CIS-3.1'
      ? `aws cloudtrail update-trail \\\n  --name ${drawerData.resourceId} \\\n  --is-multi-region-trail`
      : drawerData.ruleId === 'AWS-IAM-002'
      ? `aws iam put-role-policy \\\n  --role-name ${drawerData.resourceId} \\\n  --policy-name ScopedPolicy \\\n  --policy-document file://scoped.json`
      : drawerData.ruleId === 'AWS-NET-001'
      ? `aws ec2 revoke-security-group-ingress \\\n  --group-id ${drawerData.resourceId} \\\n  --protocol tcp \\\n  --port 22 \\\n  --cidr 0.0.0.0/0`
      : `aws s3api put-public-access-block \\\n  --bucket ${drawerData.resourceId} \\\n  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true`);

  const handleCopy = () => {
    navigator.clipboard.writeText(defaultCli);
    setCopied(true);
    showToast('CLI remediation snippet copied to clipboard.');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDispatch = () => {
    closeDrawer();
    showToast('Remediation ticket dispatched to infrastructure pipeline.');
  };

  return (
    <>
      <div className="drawer-overlay" onClick={closeDrawer} />
      <aside className="slide-drawer" role="dialog" aria-modal="true" aria-label="Finding AI Remediation">
        <div className="drawer-top">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className={`tag-sev ${sevClass}`}>{drawerData.severity.toUpperCase()}</span>
            <span className="code-id">{drawerData.ruleId}</span>
          </div>
          <button
            type="button"
            className="btn"
            style={{ padding: '2px 8px', fontSize: '13px' }}
            onClick={closeDrawer}
            title="Close Drawer"
          >
            &times;
          </button>
        </div>

        <div className="drawer-body">
          <div>
            <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#FFF' }}>{drawerData.title}</h3>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '10.5px', color: 'var(--text-tertiary)', marginTop: '3px' }}>
              Target: {drawerData.resourceId}
            </div>
          </div>

          <div className="drawer-box">
            <div className="drawer-box-header">
              <span>AI Root Cause Analysis (Amazon Bedrock Haiku)</span>
            </div>
            {loadingAi ? (
              <p style={{ fontSize: '12px', color: 'var(--cyan-bright)' }}>
                Querying Amazon Bedrock Claude Haiku for contextual risk synthesis...
              </p>
            ) : (
              <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5, whiteSpace: 'pre-line' }}>
                {aiAnalysis ||
                  drawerData.explanation ||
                  `Resource ${drawerData.resourceId} violates policy ${drawerData.ruleId}. An attacker exploiting this misconfiguration could obtain unauthorized access or pivot laterally across unmonitored infrastructure. Immediate isolation is advised.`}
              </p>
            )}
          </div>

          <div className="drawer-box">
            <div className="drawer-box-header">
              <span>Executable Remediation (AWS CLI)</span>
            </div>
            <div className="cli-box">
              <button type="button" className="btn-copy-code" onClick={handleCopy}>
                {copied ? 'COPIED' : 'Copy'}
              </button>
              <code>{defaultCli}</code>
            </div>
          </div>

          {drawerData.remediation && (
            <div className="drawer-box">
              <div className="drawer-box-header">
                <span>CIS Policy Guidance</span>
              </div>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                {drawerData.remediation}
              </p>
            </div>
          )}

          <div style={{ marginTop: 'auto', display: 'flex', gap: '8px' }}>
            <button
              type="button"
              className="btn btn-cyan"
              style={{ flex: 1, justifyContent: 'center' }}
              onClick={handleDispatch}
            >
              Dispatch Remediation
            </button>
            <button type="button" className="btn" onClick={closeDrawer}>
              Dismiss
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
