import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  getOnboardingStatus,
  getIamPolicy,
  validateAwsCredentials,
  validateAiCredentials,
  completeOnboarding,
  type ValidateAwsResult,
  type ValidateAiResult,
} from '../api/onboarding';

export default function OnboardingPage() {
  const navigate = useNavigate();

  // Wizard Step: 1 = IAM Policy, 2 = AWS Keys, 3 = AI Provider, 4 = Review & Audit
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);

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

  // Launch Scan Flag
  const [triggerScan, setTriggerScan] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // IAM Policy
  const [iamPolicyText, setIamPolicyText] = useState<string>('Loading policy...');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    getIamPolicy()
      .then((data) => setIamPolicyText(JSON.stringify(data, null, 2)))
      .catch(() => setIamPolicyText('// Error loading policy. Refer to docs/cloudsentinel_audit_iam_policy.json'));

    getOnboardingStatus().then((status) => {
      if (status.aws_default_region) setRegion(status.aws_default_region);
      if (status.ai_provider) setAiProvider(status.ai_provider as any);
    }).catch(() => {});
  }, []);

  const handleCopyPolicy = () => {
    navigator.clipboard.writeText(iamPolicyText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  // Test AWS Connection
  const handleTestAws = async () => {
    if (!accessKeyId.trim() || !secretAccessKey.trim()) {
      setAwsResult({
        is_valid: false,
        error_message: 'Access Key ID and Secret Access Key are required.',
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
    } catch (err: any) {
      setAwsResult({
        is_valid: false,
        error_message: err.response?.data?.detail || err.message || 'Failed to reach validation service.',
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
    } catch (err: any) {
      setAiResult({
        is_valid: false,
        provider: aiProvider,
        error_message: err.response?.data?.detail || err.message || 'AI validation failed.',
      });
    } finally {
      setIsTestingAi(false);
    }
  };

  // Submit & Save Onboarding
  const handleComplete = async () => {
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      await completeOnboarding({
        aws_access_key_id: accessKeyId.trim() || undefined,
        aws_secret_access_key: secretAccessKey.trim() || undefined,
        aws_session_token: sessionToken.trim() || undefined,
        aws_default_region: region,
        ai_provider: aiProvider,
        openai_api_key: openaiKey.trim() || undefined,
        openai_model: openaiModel,
        anthropic_api_key: anthropicKey.trim() || undefined,
        anthropic_model: anthropicModel,
        trigger_initial_scan: triggerScan,
      });
      navigate(triggerScan ? '/scan' : '/');
    } catch (err: any) {
      setSubmitError(err.response?.data?.detail || err.message || 'Could not complete onboarding.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: '860px', margin: '24px auto', padding: '0 16px', animation: 'tabFade 0.2s ease-out' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px', textAlign: 'center' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#FFF', margin: '0 0 8px 0', letterSpacing: '-0.02em' }}>
          Connect Your Cloud &amp; AI Provider
        </h1>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: 0 }}>
          Configure least-privilege AWS audit credentials and select your preferred LLM provider for live posture analysis.
        </p>
      </div>

      {/* Stepper Progress Bar */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '28px' }}>
        {[
          { num: 1, label: '1. IAM Policy' },
          { num: 2, label: '2. AWS Keys' },
          { num: 3, label: '3. AI Provider' },
          { num: 4, label: '4. Run Audit' },
        ].map((s) => (
          <div
            key={s.num}
            style={{
              flex: 1,
              padding: '8px 12px',
              borderRadius: 'var(--radius-sm)',
              background: step === s.num ? 'rgba(0, 229, 255, 0.12)' : 'var(--bg-panel)',
              border: `1px solid ${step === s.num ? 'var(--cyan-bright)' : 'var(--border-subtle)'}`,
              color: step === s.num ? 'var(--cyan-bright)' : 'var(--text-tertiary)',
              fontSize: '11.5px',
              fontWeight: step === s.num ? 600 : 400,
              textAlign: 'center',
            }}
          >
            {s.label}
          </div>
        ))}
      </div>

      {/* Step 1: IAM Policy Guidance */}
      {step === 1 && (
        <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
            <span style={{ fontSize: '18px' }}>🛡️</span>
            <div>
              <h2 style={{ fontSize: '15px', fontWeight: 600, color: '#FFF', margin: 0 }}>
                Best Practice: Create a Dedicated IAM User
              </h2>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
                Never provide AWS Root or Administrator keys. CloudSentinel only requires strictly read-only inspection permissions.
              </p>
            </div>
          </div>

          <div style={{ background: 'rgba(255, 179, 0, 0.08)', border: '1px solid rgba(255, 179, 0, 0.25)', borderRadius: 'var(--radius-sm)', padding: '12px 16px', marginBottom: '18px', fontSize: '11.5px', color: '#ffca28', lineHeight: 1.5 }}>
            <strong>Recommendation:</strong> In your AWS Console, create a new IAM user named <code>cloudsentinel-auditor</code> with <em>Programmatic access only</em> (no AWS Console login password), and attach the read-only policy below.
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Least-Privilege Audit Policy JSON
            </span>
            <button
              type="button"
              className="btn btn-cyan"
              style={{ fontSize: '11px', padding: '4px 10px' }}
              onClick={handleCopyPolicy}
            >
              {copied ? '✓ Copied to Clipboard!' : 'Copy Policy JSON'}
            </button>
          </div>

          <pre
            style={{
              background: '#0a0d14',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '14px',
              fontSize: '11px',
              color: 'var(--cyan-dim)',
              maxHeight: '260px',
              overflowY: 'auto',
              fontFamily: 'var(--font-mono)',
            }}
          >
            {iamPolicyText}
          </pre>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
            <button
              type="button"
              className="btn btn-cyan"
              onClick={() => setStep(2)}
              style={{ padding: '8px 20px', fontSize: '12px' }}
            >
              I Have Created the Keys &rarr; Continue to Step 2
            </button>
          </div>
        </div>
      )}

      {/* Step 2: AWS Credentials Input & Test */}
      {step === 2 && (
        <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '24px' }}>
          <h2 style={{ fontSize: '15px', fontWeight: 600, color: '#FFF', margin: '0 0 6px 0' }}>
            Enter AWS Access Credentials
          </h2>
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '0 0 20px 0' }}>
            Enter the Access Key ID and Secret Access Key generated for your dedicated audit user.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                AWS Access Key ID *
              </label>
              <input
                type="text"
                placeholder="AKIAIOSFODNN7EXAMPLE"
                value={accessKeyId}
                onChange={(e) => {
                  setAccessKeyId(e.target.value);
                  setAwsResult(null);
                }}
                style={{
                  width: '100%',
                  padding: '9px 12px',
                  background: 'var(--bg-base)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  color: '#FFF',
                  fontSize: '12px',
                  fontFamily: 'var(--font-mono)',
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                AWS Secret Access Key *
              </label>
              <input
                type="password"
                placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                value={secretAccessKey}
                onChange={(e) => {
                  setSecretAccessKey(e.target.value);
                  setAwsResult(null);
                }}
                style={{
                  width: '100%',
                  padding: '9px 12px',
                  background: 'var(--bg-base)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  color: '#FFF',
                  fontSize: '12px',
                  fontFamily: 'var(--font-mono)',
                }}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                Primary AWS Region
              </label>
              <select
                value={region}
                onChange={(e) => {
                  setRegion(e.target.value);
                  setAwsResult(null);
                }}
                style={{
                  width: '100%',
                  padding: '9px 12px',
                  background: 'var(--bg-base)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  color: '#FFF',
                  fontSize: '12px',
                }}
              >
                <option value="us-east-1">us-east-1 (N. Virginia)</option>
                <option value="us-east-2">us-east-2 (Ohio)</option>
                <option value="us-west-2">us-west-2 (Oregon)</option>
                <option value="ap-south-1">ap-south-1 (Mumbai)</option>
                <option value="eu-west-1">eu-west-1 (Ireland)</option>
                <option value="ap-southeast-1">ap-southeast-1 (Singapore)</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                STS Session Token (Optional - for temporary STS roles)
              </label>
              <input
                type="text"
                placeholder="Optional session token"
                value={sessionToken}
                onChange={(e) => setSessionToken(e.target.value)}
                style={{
                  width: '100%',
                  padding: '9px 12px',
                  background: 'var(--bg-base)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  color: '#FFF',
                  fontSize: '12px',
                  fontFamily: 'var(--font-mono)',
                }}
              />
            </div>
          </div>

          {/* Test AWS Connection Button */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '20px' }}>
            <button
              type="button"
              className="btn btn-cyan"
              onClick={handleTestAws}
              disabled={isTestingAws || !accessKeyId.trim() || !secretAccessKey.trim()}
              style={{ fontSize: '12px', padding: '8px 16px' }}
            >
              {isTestingAws ? 'Verifying with AWS STS…' : '⚡ Test AWS Connection'}
            </button>
            <span style={{ fontSize: '11.5px', color: 'var(--text-tertiary)' }}>
              Verifies account identity via <code>sts:GetCallerIdentity</code> before continuing.
            </span>
          </div>

          {/* Verification Results */}
          {awsResult && (
            <div
              style={{
                borderRadius: 'var(--radius-sm)',
                padding: '14px 18px',
                marginBottom: '20px',
                fontSize: '12px',
                lineHeight: 1.5,
                background: awsResult.is_valid ? 'rgba(0, 230, 118, 0.08)' : 'rgba(255, 23, 68, 0.08)',
                border: `1px solid ${awsResult.is_valid ? 'rgba(0, 230, 118, 0.3)' : 'rgba(255, 23, 68, 0.3)'}`,
                color: awsResult.is_valid ? 'var(--sev-low)' : 'var(--sev-crit)',
              }}
            >
              {awsResult.is_valid ? (
                <div>
                  <div style={{ fontWeight: 600, marginBottom: '4px' }}>✓ Connection Verified Successfully!</div>
                  <div style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
                    Account ID: <strong>{awsResult.account_id}</strong> &middot; Principal: {awsResult.arn}
                  </div>
                </div>
              ) : (
                <div>
                  <div style={{ fontWeight: 600, marginBottom: '4px' }}>✗ AWS Verification Failed (Cannot Proceed)</div>
                  <div>{awsResult.error_message}</div>
                  <div style={{ marginTop: '6px', fontSize: '11px', color: 'var(--text-tertiary)' }}>
                    Check that your Access Key ID and Secret Access Key match your IAM User and that no trailing spaces exist.
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Navigation Controls */}
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '24px' }}>
            <button type="button" className="btn" onClick={() => setStep(1)} style={{ fontSize: '12px' }}>
              &larr; Back to Policy
            </button>
            <button
              type="button"
              className="btn btn-cyan"
              disabled={!awsResult || !awsResult.is_valid}
              onClick={() => setStep(3)}
              style={{
                fontSize: '12px',
                padding: '8px 20px',
                opacity: (!awsResult || !awsResult.is_valid) ? 0.4 : 1,
                cursor: (!awsResult || !awsResult.is_valid) ? 'not-allowed' : 'pointer',
              }}
            >
              Credentials Verified &rarr; Choose AI Provider
            </button>
          </div>
        </div>
      )}

      {/* Step 3: AI Provider Selection & Testing */}
      {step === 3 && (
        <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '24px' }}>
          <h2 style={{ fontSize: '15px', fontWeight: 600, color: '#FFF', margin: '0 0 6px 0' }}>
            Select AI Remediation Engine
          </h2>
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '0 0 20px 0' }}>
            Choose the LLM provider to power automated root cause explanations and Infrastructure-as-Code Terraform fixes.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '20px' }}>
            {[
              { id: 'bedrock', title: 'Amazon Bedrock', desc: 'Claude Haiku 4.5 / Nova via your AWS region', badge: 'Recommended' },
              { id: 'openai', title: 'OpenAI API', desc: 'GPT-4o or GPT-4o-mini via direct API key', badge: 'BYO Key' },
              { id: 'anthropic', title: 'Direct Anthropic', desc: 'Claude 3.5 Sonnet direct API key', badge: 'BYO Key' },
              { id: 'default', title: 'Deterministic Rules', desc: 'Pre-computed static CIS remediation guides', badge: 'No AI Cost' },
            ].map((p) => (
              <div
                key={p.id}
                onClick={() => {
                  setAiProvider(p.id as any);
                  setAiResult(null);
                }}
                style={{
                  padding: '14px',
                  borderRadius: 'var(--radius-sm)',
                  cursor: 'pointer',
                  border: `1px solid ${aiProvider === p.id ? 'var(--cyan-bright)' : 'var(--border-subtle)'}`,
                  background: aiProvider === p.id ? 'rgba(0, 229, 255, 0.08)' : 'var(--bg-base)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontWeight: 600, fontSize: '13px', color: '#FFF' }}>{p.title}</span>
                  <span className="tag-sev low" style={{ fontSize: '10px' }}>{p.badge}</span>
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>{p.desc}</div>
              </div>
            ))}
          </div>

          {/* OpenAI Configuration */}
          {aiProvider === 'openai' && (
            <div style={{ background: 'var(--bg-base)', padding: '16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', marginBottom: '20px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                    OpenAI API Key (sk-...) *
                  </label>
                  <input
                    type="password"
                    placeholder="sk-proj-..."
                    value={openaiKey}
                    onChange={(e) => {
                      setOpenaiKey(e.target.value);
                      setAiResult(null);
                    }}
                    style={{
                      width: '100%',
                      padding: '9px 12px',
                      background: '#0a0d14',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      color: '#FFF',
                      fontSize: '12px',
                      fontFamily: 'var(--font-mono)',
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                    Model
                  </label>
                  <select
                    value={openaiModel}
                    onChange={(e) => setOpenaiModel(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '9px 12px',
                      background: '#0a0d14',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      color: '#FFF',
                      fontSize: '12px',
                    }}
                  >
                    <option value="gpt-4o-mini">gpt-4o-mini (Fast &amp; Cost-Effective)</option>
                    <option value="gpt-4o">gpt-4o (High Reasoning)</option>
                  </select>
                </div>
              </div>

              <div style={{ marginTop: '12px' }}>
                <button
                  type="button"
                  className="btn btn-cyan"
                  onClick={handleTestAi}
                  disabled={isTestingAi || !openaiKey.trim()}
                  style={{ fontSize: '11px', padding: '6px 12px' }}
                >
                  {isTestingAi ? 'Validating Key…' : '⚡ Test OpenAI Key'}
                </button>
              </div>
            </div>
          )}

          {/* Anthropic Configuration */}
          {aiProvider === 'anthropic' && (
            <div style={{ background: 'var(--bg-base)', padding: '16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', marginBottom: '20px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                    Anthropic API Key (sk-ant-...) *
                  </label>
                  <input
                    type="password"
                    placeholder="sk-ant-..."
                    value={anthropicKey}
                    onChange={(e) => {
                      setAnthropicKey(e.target.value);
                      setAiResult(null);
                    }}
                    style={{
                      width: '100%',
                      padding: '9px 12px',
                      background: '#0a0d14',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      color: '#FFF',
                      fontSize: '12px',
                      fontFamily: 'var(--font-mono)',
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                    Model
                  </label>
                  <select
                    value={anthropicModel}
                    onChange={(e) => setAnthropicModel(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '9px 12px',
                      background: '#0a0d14',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      color: '#FFF',
                      fontSize: '12px',
                    }}
                  >
                    <option value="claude-3-5-sonnet-20241022">claude-3-5-sonnet</option>
                    <option value="claude-3-5-haiku-20241022">claude-3-5-haiku</option>
                  </select>
                </div>
              </div>

              <div style={{ marginTop: '12px' }}>
                <button
                  type="button"
                  className="btn btn-cyan"
                  onClick={handleTestAi}
                  disabled={isTestingAi || !anthropicKey.trim()}
                  style={{ fontSize: '11px', padding: '6px 12px' }}
                >
                  {isTestingAi ? 'Validating Key…' : '⚡ Test Anthropic Key'}
                </button>
              </div>
            </div>
          )}

          {/* AI Validation Feedback */}
          {aiResult && (
            <div
              style={{
                borderRadius: 'var(--radius-sm)',
                padding: '12px 16px',
                marginBottom: '20px',
                fontSize: '12px',
                background: aiResult.is_valid ? 'rgba(0, 230, 118, 0.08)' : 'rgba(255, 23, 68, 0.08)',
                border: `1px solid ${aiResult.is_valid ? 'rgba(0, 230, 118, 0.3)' : 'rgba(255, 23, 68, 0.3)'}`,
                color: aiResult.is_valid ? 'var(--sev-low)' : 'var(--sev-crit)',
              }}
            >
              {aiResult.is_valid ? (
                <div>✓ AI Provider verified ({aiResult.provider} / {aiResult.model || 'active'})</div>
              ) : (
                <div>✗ {aiResult.error_message}</div>
              )}
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '24px' }}>
            <button type="button" className="btn" onClick={() => setStep(2)} style={{ fontSize: '12px' }}>
              &larr; Back to AWS Keys
            </button>
            <button
              type="button"
              className="btn btn-cyan"
              onClick={() => setStep(4)}
              disabled={(aiProvider === 'openai' && !openaiKey.trim()) || (aiProvider === 'anthropic' && !anthropicKey.trim())}
              style={{ fontSize: '12px', padding: '8px 20px' }}
            >
              Continue to Final Step &rarr;
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Review & Launch Live Audit */}
      {step === 4 && (
        <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '24px' }}>
          <h2 style={{ fontSize: '15px', fontWeight: 600, color: '#FFF', margin: '0 0 6px 0' }}>
            Review &amp; Launch First Real Audit
          </h2>
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '0 0 20px 0' }}>
            CloudSentinel will now run a read-only audit against your connected AWS account and populate real findings.
          </p>

          <div style={{ background: 'var(--bg-base)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '16px', marginBottom: '20px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', fontSize: '12px' }}>
              <div>
                <span style={{ color: 'var(--text-tertiary)', display: 'block', marginBottom: '4px' }}>Target Account ID:</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#FFF' }}>
                  {awsResult?.account_id || 'Connected Account'}
                </span>
              </div>
              <div>
                <span style={{ color: 'var(--text-tertiary)', display: 'block', marginBottom: '4px' }}>Audit Region:</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#FFF' }}>{region}</span>
              </div>
              <div>
                <span style={{ color: 'var(--text-tertiary)', display: 'block', marginBottom: '4px' }}>IAM Principal:</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-secondary)' }}>
                  {awsResult?.arn || 'cloudsentinel-auditor'}
                </span>
              </div>
              <div>
                <span style={{ color: 'var(--text-tertiary)', display: 'block', marginBottom: '4px' }}>AI Remediation Engine:</span>
                <span style={{ textTransform: 'capitalize', fontWeight: 600, color: 'var(--cyan-bright)' }}>
                  {aiProvider}
                </span>
              </div>
            </div>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', fontSize: '12px', color: '#FFF' }}>
              <input
                type="checkbox"
                checked={triggerScan}
                onChange={(e) => setTriggerScan(e.target.checked)}
                style={{ accentColor: 'var(--cyan-bright)', width: '16px', height: '16px' }}
              />
              <span>Trigger Initial Multi-Service Security Audit Immediately (Recommended)</span>
            </label>
            <p style={{ margin: '4px 0 0 26px', fontSize: '11px', color: 'var(--text-tertiary)' }}>
              Runs read-only collectors on IAM, EC2, S3, VPC, Security Groups, RDS, CloudTrail, and Config.
            </p>
          </div>

          {submitError && (
            <div style={{ background: 'rgba(255, 23, 68, 0.1)', border: '1px solid var(--sev-crit)', borderRadius: 'var(--radius-sm)', padding: '12px 16px', color: 'var(--sev-crit)', fontSize: '12px', marginBottom: '20px' }}>
              {submitError}
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <button type="button" className="btn" onClick={() => setStep(3)} style={{ fontSize: '12px' }}>
              &larr; Back
            </button>
            <button
              type="button"
              className="btn btn-cyan"
              onClick={handleComplete}
              disabled={isSubmitting}
              style={{ fontSize: '13px', padding: '10px 24px', fontWeight: 600 }}
            >
              {isSubmitting ? 'Starting Initial Audit…' : 'Complete Setup & Run Real Audit 🚀'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
