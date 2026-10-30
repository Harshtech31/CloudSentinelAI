import { useEffect, useState } from 'react';
import {
  getIamPolicy,
  getOnboardingStatus,
  validateAiCredentials,
  validateAwsCredentials,
  completeOnboarding,
  type OnboardingStatus,
  type ValidateAiResult,
  type ValidateAwsResult,
} from '../api/onboarding';
import { useAuth } from '../contexts/AuthContext';
import { useUIStore } from '../store/uiStore';

export default function SettingsPage() {
  const { refreshOnboarding } = useAuth();
  const showToast = useUIStore((s) => s.showToast);

  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<OnboardingStatus | null>(null);

  // AWS Credentials State
  const [accessKeyId, setAccessKeyId] = useState('');
  const [secretAccessKey, setSecretAccessKey] = useState('');
  const [sessionToken, setSessionToken] = useState('');
  const [region, setRegion] = useState('us-east-1');
  const [isTestingAws, setIsTestingAws] = useState(false);
  const [awsResult, setAwsResult] = useState<ValidateAwsResult | null>(null);

  // AI Provider State
  const [aiProvider, setAiProvider] = useState<'bedrock' | 'openai' | 'anthropic' | 'default'>('bedrock');
  const [openaiKey, setOpenaiKey] = useState('');
  const [openaiModel, setOpenaiModel] = useState('gpt-4o-mini');
  const [anthropicKey, setAnthropicKey] = useState('');
  const [anthropicModel, setAnthropicModel] = useState('claude-3-5-sonnet-20241022');
  const [isTestingAi, setIsTestingAi] = useState(false);
  const [aiResult, setAiResult] = useState<ValidateAiResult | null>(null);

  // IAM Policy State
  const [iamPolicyText, setIamPolicyText] = useState('Loading policy...');
  const [copied, setCopied] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getOnboardingStatus(), getIamPolicy()])
      .then(([st, policy]) => {
        setStatus(st);
        setIamPolicyText(JSON.stringify(policy, null, 2));
        if (st.aws_default_region) setRegion(st.aws_default_region);
        if (st.ai_provider) setAiProvider(st.ai_provider as any);
        setLoading(false);
      })
      .catch((err) => {
        setSaveError(err.message || 'Failed loading settings.');
        setLoading(false);
      });
  }, []);

  const handleCopyPolicy = () => {
    navigator.clipboard.writeText(iamPolicyText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleDownloadPolicy = () => {
    const blob = new Blob([iamPolicyText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cloudsentinel_audit_iam_policy.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('IAM policy JSON downloaded');
  };

  // Test AWS Connection
  const handleTestAws = async () => {
    if (!accessKeyId.trim() || !secretAccessKey.trim()) {
      setAwsResult({
        is_valid: false,
        error_message: 'Please provide both an Access Key ID and Secret Access Key to test.',
      });
      return;
    }
    setIsTestingAws(true);
    setAwsResult(null);
    try {
      const res = await validateAwsCredentials({
        aws_access_key_id: accessKeyId.trim(),
        aws_secret_access_key: secretAccessKey.trim(),
        aws_session_token: sessionToken.trim() || undefined,
        region,
      });
      setAwsResult(res);
      if (res.is_valid) {
        showToast(`AWS account ${res.account_id} verified`);
      }
    } catch (err: any) {
      setAwsResult({
        is_valid: false,
        error_message: err.response?.data?.detail || err.message || 'AWS authentication check failed.',
      });
    } finally {
      setIsTestingAws(false);
    }
  };

  // Test AI Connection
  const handleTestAi = async () => {
    setIsTestingAi(true);
    setAiResult(null);
    try {
      const res = await validateAiCredentials({
        provider: aiProvider,
        api_key: aiProvider === 'openai' ? openaiKey.trim() : aiProvider === 'anthropic' ? anthropicKey.trim() : undefined,
        model: aiProvider === 'openai' ? openaiModel : aiProvider === 'anthropic' ? anthropicModel : undefined,
        aws_region: region,
      });
      setAiResult(res);
      if (res.is_valid) {
        showToast(`${res.provider.toUpperCase()} AI verified`);
      }
    } catch (err: any) {
      setAiResult({
        is_valid: false,
        provider: aiProvider,
        error_message: err.response?.data?.detail || err.message || 'AI credential check failed.',
      });
    } finally {
      setIsTestingAi(false);
    }
  };

  // Save changes
  const handleSaveChanges = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveError(null);
    setSaveSuccess(null);

    try {
      const updated = await completeOnboarding({
        aws_access_key_id: accessKeyId.trim() || undefined,
        aws_secret_access_key: secretAccessKey.trim() || undefined,
        aws_session_token: sessionToken.trim() || undefined,
        aws_default_region: region,
        ai_provider: aiProvider,
        openai_api_key: openaiKey.trim() || undefined,
        openai_model: openaiModel,
        anthropic_api_key: anthropicKey.trim() || undefined,
        anthropic_model: anthropicModel,
        trigger_initial_scan: false,
      });

      setStatus(updated);
      setSaveSuccess('Configuration updated successfully! New credentials are active.');
      showToast('Cloud & AI settings saved successfully');
      await refreshOnboarding();
      // Clear sensitive secret inputs after successful save
      setSecretAccessKey('');
      setSessionToken('');
      setOpenaiKey('');
      setAnthropicKey('');
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Failed saving settings.';
      setSaveError(msg);
      showToast(msg);
    } finally {
      setIsSaving(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', minHeight: '60vh', alignItems: 'center', justifyContent: 'center' }}>
        <div className="spinner-cyan" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1000px', margin: '0 auto', animation: 'tabFade 0.2s ease-out' }}>
      {/* Page Header */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '22px', fontWeight: 700, color: '#FFF', margin: '0 0 6px 0', letterSpacing: '-0.02em' }}>
          Cloud &amp; AI Integration Settings
        </h1>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: 0 }}>
          Edit and update your AWS tenant connection, adjust scan target regions, configure AI remediation keys, and download the audit IAM policy.
        </p>
      </div>

      {saveSuccess && (
        <div style={{ background: 'rgba(0, 230, 118, 0.1)', border: '1px solid var(--sev-low)', borderRadius: 'var(--radius-sm)', padding: '12px 16px', color: 'var(--sev-low)', fontSize: '12.5px', marginBottom: '20px' }}>
          ✓ {saveSuccess}
        </div>
      )}

      {saveError && (
        <div style={{ background: 'rgba(255, 23, 68, 0.1)', border: '1px solid var(--sev-crit)', borderRadius: 'var(--radius-sm)', padding: '12px 16px', color: 'var(--sev-crit)', fontSize: '12.5px', marginBottom: '20px' }}>
          ✕ {saveError}
        </div>
      )}

      <form onSubmit={handleSaveChanges}>
        {/* Card 1: Connected AWS Account Info & Edit */}
        <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '24px', marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h2 style={{ fontSize: '15px', fontWeight: 600, color: '#FFF', margin: '0 0 4px 0' }}>
                Edit AWS Target Credentials
              </h2>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: 0 }}>
                {status?.aws_account_id
                  ? `Currently connected to AWS Account: ${status.aws_account_id} (${status.aws_default_region})`
                  : 'Configure audit credentials for your AWS account.'}
              </p>
            </div>
            {status?.aws_account_id && (
              <span
                style={{
                  background: 'rgba(0, 230, 118, 0.1)',
                  border: '1px solid rgba(0, 230, 118, 0.3)',
                  color: 'var(--sev-low)',
                  fontSize: '11px',
                  fontWeight: 600,
                  padding: '3px 10px',
                  borderRadius: '12px',
                }}
              >
                ● Connected
              </span>
            )}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '11.5px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                AWS Access Key ID
              </label>
              <input
                type="text"
                className="input"
                placeholder={status?.aws_account_id ? 'Enter new Access Key ID to update' : 'AKIAIOSFODNN7EXAMPLE'}
                value={accessKeyId}
                onChange={(e) => {
                  setAccessKeyId(e.target.value);
                  setAwsResult(null);
                }}
                style={{ width: '100%', fontFamily: 'var(--font-mono)', fontSize: '12px' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '11.5px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                AWS Secret Access Key
              </label>
              <input
                type="password"
                className="input"
                placeholder={status?.aws_configured ? '•••••••••••••••••••••••• (Leave blank to keep current)' : 'Enter Secret Access Key'}
                value={secretAccessKey}
                onChange={(e) => {
                  setSecretAccessKey(e.target.value);
                  setAwsResult(null);
                }}
                style={{ width: '100%', fontFamily: 'var(--font-mono)', fontSize: '12px' }}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '11.5px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                Target Audit Region
              </label>
              <select
                className="input"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                style={{ width: '100%', fontSize: '12px' }}
              >
                <option value="us-east-1">US East (N. Virginia) us-east-1</option>
                <option value="us-east-2">US East (Ohio) us-east-2</option>
                <option value="us-west-1">US West (N. California) us-west-1</option>
                <option value="us-west-2">US West (Oregon) us-west-2</option>
                <option value="ap-south-1">Asia Pacific (Mumbai) ap-south-1</option>
                <option value="eu-west-1">Europe (Ireland) eu-west-1</option>
                <option value="eu-central-1">Europe (Frankfurt) eu-central-1</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '11.5px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                STS Session Token <span style={{ color: 'var(--text-tertiary)' }}>(Optional temporary token)</span>
              </label>
              <input
                type="password"
                className="input"
                placeholder="Leave blank unless using temporary STS credentials"
                value={sessionToken}
                onChange={(e) => setSessionToken(e.target.value)}
                style={{ width: '100%', fontFamily: 'var(--font-mono)', fontSize: '12px' }}
              />
            </div>
          </div>

          {awsResult && (
            <div
              style={{
                padding: '12px 16px',
                borderRadius: 'var(--radius-sm)',
                marginBottom: '16px',
                fontSize: '12px',
                background: awsResult.is_valid ? 'rgba(0, 230, 118, 0.08)' : 'rgba(255, 23, 68, 0.08)',
                border: `1px solid ${awsResult.is_valid ? 'var(--sev-low)' : 'var(--sev-crit)'}`,
                color: awsResult.is_valid ? 'var(--sev-low)' : 'var(--sev-crit)',
              }}
            >
              {awsResult.is_valid ? (
                <div>
                  <strong>✓ AWS STS Verified:</strong> Account {awsResult.account_id} ({awsResult.arn})
                </div>
              ) : (
                <div>
                  <strong>✕ Validation Error:</strong> {awsResult.error_message}
                </div>
              )}
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              type="button"
              className="btn"
              onClick={handleTestAws}
              disabled={isTestingAws || !accessKeyId.trim() || !secretAccessKey.trim()}
              style={{ fontSize: '12px' }}
            >
              {isTestingAws ? 'Verifying with AWS STS…' : 'Test Key Validity'}
            </button>
          </div>
        </div>

        {/* Card 2: AI Remediation Engine Configuration */}
        <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '24px', marginBottom: '24px' }}>
          <h2 style={{ fontSize: '15px', fontWeight: 600, color: '#FFF', margin: '0 0 4px 0' }}>
            Edit AI Remediation Engine
          </h2>
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '0 0 16px 0' }}>
            Choose which AI model generates deep contextual remediation steps and CIS benchmark summaries.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '20px' }}>
            {[
              { id: 'bedrock', title: 'Amazon Bedrock', desc: 'Claude 3.5 via AWS', badge: 'Active' },
              { id: 'openai', title: 'OpenAI', desc: 'GPT-4o / GPT-4o-mini', badge: 'API Key' },
              { id: 'anthropic', title: 'Anthropic', desc: 'Claude Sonnet / Haiku', badge: 'API Key' },
              { id: 'default', title: 'Deterministic', desc: 'Rulebook Catalog', badge: 'Offline' },
            ].map((p) => (
              <div
                key={p.id}
                onClick={() => {
                  setAiProvider(p.id as any);
                  setAiResult(null);
                }}
                style={{
                  border: `1px solid ${aiProvider === p.id ? 'var(--cyan-bright)' : 'var(--border-subtle)'}`,
                  borderRadius: 'var(--radius-sm)',
                  padding: '12px',
                  cursor: 'pointer',
                  background: aiProvider === p.id ? 'rgba(0, 229, 255, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                  transition: 'all 0.15s ease',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span style={{ fontSize: '12.5px', fontWeight: 600, color: aiProvider === p.id ? '#FFF' : 'var(--text-secondary)' }}>
                    {p.title}
                  </span>
                  <span style={{ fontSize: '9px', background: 'rgba(255,255,255,0.06)', padding: '2px 5px', borderRadius: '3px', color: 'var(--text-tertiary)' }}>
                    {p.badge}
                  </span>
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>{p.desc}</div>
              </div>
            ))}
          </div>

          {aiProvider === 'openai' && (
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '16px', marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '11.5px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                OpenAI API Key
              </label>
              <input
                type="password"
                className="input"
                placeholder={status?.openai_configured ? '•••••••••••••••••••••••• (Leave blank to keep current)' : 'sk-proj-...'}
                value={openaiKey}
                onChange={(e) => {
                  setOpenaiKey(e.target.value);
                  setAiResult(null);
                }}
                style={{ width: '100%', fontFamily: 'var(--font-mono)', fontSize: '12px', marginBottom: '12px' }}
              />

              <label style={{ display: 'block', fontSize: '11.5px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                Model
              </label>
              <select
                className="input"
                value={openaiModel}
                onChange={(e) => setOpenaiModel(e.target.value)}
                style={{ width: '100%', fontSize: '12px' }}
              >
                <option value="gpt-4o-mini">gpt-4o-mini (Fast &amp; Cost-Effective)</option>
                <option value="gpt-4o">gpt-4o (High Precision)</option>
              </select>
            </div>
          )}

          {aiProvider === 'anthropic' && (
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '16px', marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '11.5px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                Anthropic API Key
              </label>
              <input
                type="password"
                className="input"
                placeholder={status?.anthropic_configured ? '•••••••••••••••••••••••• (Leave blank to keep current)' : 'sk-ant-api03-...'}
                value={anthropicKey}
                onChange={(e) => {
                  setAnthropicKey(e.target.value);
                  setAiResult(null);
                }}
                style={{ width: '100%', fontFamily: 'var(--font-mono)', fontSize: '12px', marginBottom: '12px' }}
              />

              <label style={{ display: 'block', fontSize: '11.5px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                Model
              </label>
              <select
                className="input"
                value={anthropicModel}
                onChange={(e) => setAnthropicModel(e.target.value)}
                style={{ width: '100%', fontSize: '12px' }}
              >
                <option value="claude-3-5-sonnet-20241022">claude-3-5-sonnet-20241022 (Recommended)</option>
                <option value="claude-3-5-haiku-20241022">claude-3-5-haiku-20241022 (Fastest)</option>
              </select>
            </div>
          )}

          {aiResult && (
            <div
              style={{
                padding: '12px 16px',
                borderRadius: 'var(--radius-sm)',
                marginBottom: '16px',
                fontSize: '12px',
                background: aiResult.is_valid ? 'rgba(0, 230, 118, 0.08)' : 'rgba(255, 23, 68, 0.08)',
                border: `1px solid ${aiResult.is_valid ? 'var(--sev-low)' : 'var(--sev-crit)'}`,
                color: aiResult.is_valid ? 'var(--sev-low)' : 'var(--sev-crit)',
              }}
            >
              {aiResult.is_valid ? (
                <div>✓ {aiResult.provider.toUpperCase()} AI credentials verified successfully!</div>
              ) : (
                <div>✕ AI Key Check Failed: {aiResult.error_message}</div>
              )}
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            {(aiProvider === 'openai' || aiProvider === 'anthropic') && (
              <button
                type="button"
                className="btn"
                onClick={handleTestAi}
                disabled={isTestingAi}
                style={{ fontSize: '12px' }}
              >
                {isTestingAi ? 'Verifying Key…' : 'Test AI Connection'}
              </button>
            )}
          </div>
        </div>

        {/* Card 3: IAM Policy JSON Viewer & Downloader */}
        <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '24px', marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <div>
              <h2 style={{ fontSize: '15px', fontWeight: 600, color: '#FFF', margin: '0 0 4px 0' }}>
                Least-Privilege Audit IAM Policy JSON
              </h2>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: 0 }}>
                Attach this policy to your dedicated <code>cloudsentinel-auditor</code> user in AWS IAM.
              </p>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                type="button"
                className="btn"
                style={{ fontSize: '11.5px', padding: '5px 12px' }}
                onClick={handleCopyPolicy}
              >
                {copied ? '✓ Copied!' : 'Copy JSON'}
              </button>
              <button
                type="button"
                className="btn btn-cyan"
                style={{ fontSize: '11.5px', padding: '5px 14px', fontWeight: 600 }}
                onClick={handleDownloadPolicy}
                title="Download cloudsentinel_audit_iam_policy.json"
              >
                ⬇ Download JSON Policy
              </button>
            </div>
          </div>

          <pre
            style={{
              background: '#07090e',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '14px',
              fontSize: '11.5px',
              color: 'var(--cyan-dim)',
              maxHeight: '220px',
              overflowY: 'auto',
              fontFamily: 'var(--font-mono)',
              lineHeight: 1.5,
              margin: 0,
            }}
          >
            {iamPolicyText}
          </pre>
        </div>

        {/* Save Bar */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
          <button
            type="submit"
            className="btn btn-cyan"
            disabled={isSaving}
            style={{ padding: '10px 24px', fontSize: '13px', fontWeight: 600 }}
          >
            {isSaving ? 'Validating & Saving…' : 'Save & Update Credentials'}
          </button>
        </div>
      </form>
    </div>
  );
}
