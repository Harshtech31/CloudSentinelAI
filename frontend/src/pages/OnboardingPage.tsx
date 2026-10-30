import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
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
  const { user, logout, setIsOnboarded, isOnboarded } = useAuth();

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

  // Step 2 Next Guard
  const handleStep2Next = () => {
    if (!awsResult?.is_valid) {
      handleTestAws();
      return;
    }
    setStep(3);
  };

  // Step 3 Next Guard
  const handleStep3Next = () => {
    if (aiProvider === 'openai' && !openaiKey.trim()) {
      setAiResult({ is_valid: false, provider: 'openai', error_message: 'OpenAI API Key is required.' });
      return;
    }
    if (aiProvider === 'anthropic' && !anthropicKey.trim()) {
      setAiResult({ is_valid: false, provider: 'anthropic', error_message: 'Anthropic API Key is required.' });
      return;
    }
    setStep(4);
  };

  // Final submission
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
      setIsOnboarded(true);
      navigate(triggerScan ? '/scan' : '/');
    } catch (err: any) {
      setSubmitError(err.response?.data?.detail || err.message || 'Could not complete onboarding.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#0B0F19', display: 'flex', flexDirection: 'column' }}>
      {/* Standalone Brand Header */}
      <header
        style={{
          height: '56px',
          borderBottom: '1px solid var(--border-subtle)',
          background: 'rgba(15, 23, 42, 0.75)',
          backdropFilter: 'blur(12px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 24px',
          position: 'sticky',
          top: 0,
          zIndex: 40,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '28px',
              height: '28px',
              borderRadius: '6px',
              background: 'linear-gradient(135deg, rgba(0, 229, 255, 0.2), rgba(0, 229, 255, 0.05))',
              border: '1px solid rgba(0, 229, 255, 0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--cyan-bright)',
            }}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.8">
              <path d="M12 2L3 7v6c0 5.5 3.8 10.7 9 12 5.2-1.3 9-6.5 9-12V7l-9-5z" />
            </svg>
          </div>
          <span style={{ fontWeight: 700, fontSize: '15px', color: '#FFF', letterSpacing: '-0.02em' }}>
            CloudSentinel AI
          </span>
          <span
            style={{
              background: 'rgba(0, 229, 255, 0.1)',
              border: '1px solid rgba(0, 229, 255, 0.25)',
              color: 'var(--cyan-bright)',
              fontSize: '10px',
              fontWeight: 600,
              padding: '2px 8px',
              borderRadius: '4px',
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
            }}
          >
            Account Onboarding
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {isOnboarded && (
            <button
              type="button"
              className="btn btn-cyan"
              style={{ fontSize: '11.5px', padding: '5px 12px' }}
              onClick={() => navigate('/')}
            >
              &larr; Back to Dashboard
            </button>
          )}
          <div
            style={{
              fontSize: '12px',
              color: 'var(--text-secondary)',
              background: 'rgba(255, 255, 255, 0.04)',
              padding: '4px 10px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
            }}
          >
            {user?.email || 'User Session'}
          </div>
          <button
            type="button"
            className="btn"
            style={{ fontSize: '11px', padding: '5px 10px' }}
            onClick={logout}
          >
            Sign out
          </button>
        </div>
      </header>

      {/* Main Wizard Content Area */}
      <div style={{ flex: 1, padding: '32px 16px', display: 'flex', justifyContent: 'center' }}>
        <div style={{ width: '100%', maxWidth: '860px', animation: 'tabFade 0.2s ease-out' }}>
          {/* Header Title */}
          <div style={{ marginBottom: '28px', textAlign: 'center' }}>
            <h1 style={{ fontSize: '26px', fontWeight: 700, color: '#FFF', margin: '0 0 8px 0', letterSpacing: '-0.02em' }}>
              Connect Your AWS Cloud &amp; AI Provider
            </h1>
            <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
              CloudSentinel requires least-privilege read-only AWS audit access and an AI model connection to perform posture evaluations.
            </p>
          </div>

          {/* Stepper Progress Bar */}
          <div style={{ display: 'flex', gap: '8px', marginBottom: '28px' }}>
            {[
              { num: 1, label: '1. IAM Policy & Download' },
              { num: 2, label: '2. AWS Credentials' },
              { num: 3, label: '3. AI Provider' },
              { num: 4, label: '4. Verify & Run' },
            ].map((s) => (
              <div
                key={s.num}
                style={{
                  flex: 1,
                  padding: '10px 12px',
                  borderRadius: 'var(--radius-sm)',
                  background: step === s.num ? 'rgba(0, 229, 255, 0.12)' : 'var(--bg-panel)',
                  border: `1px solid ${step === s.num ? 'var(--cyan-bright)' : 'var(--border-subtle)'}`,
                  color: step === s.num ? 'var(--cyan-bright)' : 'var(--text-tertiary)',
                  fontSize: '12px',
                  fontWeight: step === s.num ? 600 : 400,
                  textAlign: 'center',
                  transition: 'all 0.15s ease',
                }}
              >
                {s.label}
              </div>
            ))}
          </div>

          {/* Step 1: IAM Policy Guidance & Download */}
          {step === 1 && (
            <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '28px' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px', marginBottom: '18px' }}>
                <span style={{ fontSize: '22px' }}>🛡️</span>
                <div>
                  <h2 style={{ fontSize: '16px', fontWeight: 600, color: '#FFF', margin: '0 0 4px 0' }}>
                    Step 1: Create a Dedicated Audit IAM User in AWS
                  </h2>
                  <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
                    Never use root or administrative keys. We recommend creating an IAM user named{' '}
                    <code style={{ color: 'var(--cyan-bright)', background: 'rgba(0, 229, 255, 0.08)', padding: '2px 6px', borderRadius: '4px' }}>
                      cloudsentinel-auditor
                    </code>{' '}
                    with programmatic access, and attaching this read-only policy.
                  </p>
                </div>
              </div>

              <div style={{ background: 'rgba(255, 179, 0, 0.08)', border: '1px solid rgba(255, 179, 0, 0.25)', borderRadius: 'var(--radius-sm)', padding: '14px 18px', marginBottom: '22px', fontSize: '12px', color: '#ffca28', lineHeight: 1.5 }}>
                <strong>Why this is safe:</strong> The policy below grants strictly read-only inspection permissions (<code style={{ color: '#FFF' }}>Get*</code>, <code style={{ color: '#FFF' }}>List*</code>, <code style={{ color: '#FFF' }}>Describe*</code>) across IAM, EC2, S3, RDS, VPC, CloudTrail, and Config. It has zero mutation or resource destruction permissions.
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <span style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 600 }}>
                  Least-Privilege Policy JSON
                </span>
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
                    title="Download cloudsentinel_audit_iam_policy.json file to upload to AWS"
                  >
                    ⬇ Download Policy (.json)
                  </button>
                </div>
              </div>

              <pre
                style={{
                  background: '#07090e',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '16px',
                  fontSize: '11.5px',
                  color: 'var(--cyan-dim)',
                  maxHeight: '280px',
                  overflowY: 'auto',
                  fontFamily: 'var(--font-mono)',
                  lineHeight: 1.5,
                }}
              >
                {iamPolicyText}
              </pre>

              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '24px' }}>
                <button
                  type="button"
                  className="btn btn-cyan"
                  onClick={() => setStep(2)}
                  style={{ padding: '10px 24px', fontSize: '13px', fontWeight: 600 }}
                >
                  I've Attached the Policy &rarr; Enter Keys
                </button>
              </div>
            </div>
          )}

          {/* Step 2: AWS Credentials Input & Test */}
          {step === 2 && (
            <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '28px' }}>
              <h2 style={{ fontSize: '16px', fontWeight: 600, color: '#FFF', margin: '0 0 6px 0' }}>
                Enter AWS Access Credentials
              </h2>
              <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', margin: '0 0 22px 0' }}>
                Provide the Access Key ID and Secret Access Key generated for your dedicated auditor. Keys are verified via AWS STS before saving.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '18px', marginBottom: '18px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '11.5px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                    AWS Access Key ID <span style={{ color: 'var(--sev-crit)' }}>*</span>
                  </label>
                  <input
                    type="text"
                    className="input"
                    placeholder="AKIAIOSFODNN7EXAMPLE"
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
                    AWS Secret Access Key <span style={{ color: 'var(--sev-crit)' }}>*</span>
                  </label>
                  <input
                    type="password"
                    className="input"
                    placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                    value={secretAccessKey}
                    onChange={(e) => {
                      setSecretAccessKey(e.target.value);
                      setAwsResult(null);
                    }}
                    style={{ width: '100%', fontFamily: 'var(--font-mono)', fontSize: '12px' }}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '18px', marginBottom: '22px' }}>
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
                    STS Session Token <span style={{ color: 'var(--text-tertiary)' }}>(Optional - for temporary credentials)</span>
                  </label>
                  <input
                    type="password"
                    className="input"
                    placeholder="AQoDYXdzEJr1... (leave empty for permanent IAM user)"
                    value={sessionToken}
                    onChange={(e) => setSessionToken(e.target.value)}
                    style={{ width: '100%', fontFamily: 'var(--font-mono)', fontSize: '12px' }}
                  />
                </div>
              </div>

              {/* AWS Test Result Feedback */}
              {awsResult && (
                <div
                  style={{
                    padding: '14px 18px',
                    borderRadius: 'var(--radius-sm)',
                    marginBottom: '22px',
                    fontSize: '12px',
                    background: awsResult.is_valid ? 'rgba(0, 230, 118, 0.08)' : 'rgba(255, 23, 68, 0.08)',
                    border: `1px solid ${awsResult.is_valid ? 'var(--sev-low)' : 'var(--sev-crit)'}`,
                    color: awsResult.is_valid ? 'var(--sev-low)' : 'var(--sev-crit)',
                  }}
                >
                  {awsResult.is_valid ? (
                    <div>
                      <strong>✓ AWS STS Identity Verified!</strong>
                      <div style={{ marginTop: '4px', fontSize: '11.5px', opacity: 0.9 }}>
                        Account ID: <b>{awsResult.account_id}</b> · Principal: <code>{awsResult.arn}</code>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <strong>✕ AWS Verification Failed (Cannot Proceed):</strong>
                      <div style={{ marginTop: '4px', fontSize: '11.5px', opacity: 0.9 }}>
                        {awsResult.error_message}
                      </div>
                    </div>
                  )}
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <button type="button" className="btn" onClick={() => setStep(1)} style={{ fontSize: '12px' }}>
                  &larr; Back
                </button>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button
                    type="button"
                    className="btn"
                    onClick={handleTestAws}
                    disabled={isTestingAws || !accessKeyId.trim() || !secretAccessKey.trim()}
                    style={{ fontSize: '12px' }}
                  >
                    {isTestingAws ? 'Verifying with AWS STS…' : 'Test Credentials'}
                  </button>
                  <button
                    type="button"
                    className="btn btn-cyan"
                    onClick={handleStep2Next}
                    style={{ fontSize: '12px', padding: '8px 20px', fontWeight: 600 }}
                  >
                    {awsResult?.is_valid ? 'Continue &rarr;' : 'Verify & Continue &rarr;'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: AI Provider Setup */}
          {step === 3 && (
            <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '28px' }}>
              <h2 style={{ fontSize: '16px', fontWeight: 600, color: '#FFF', margin: '0 0 6px 0' }}>
                Select AI Remediation Provider
              </h2>
              <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', margin: '0 0 22px 0' }}>
                CloudSentinel supports Amazon Bedrock, OpenAI, Anthropic, or deterministic rule evaluation.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '22px' }}>
                {[
                  { id: 'bedrock', title: 'Amazon Bedrock', desc: 'Claude 3.5 via AWS', badge: 'AWS Native' },
                  { id: 'openai', title: 'OpenAI', desc: 'GPT-4o / GPT-4o-mini', badge: 'API Key' },
                  { id: 'anthropic', title: 'Anthropic', desc: 'Direct Claude API', badge: 'API Key' },
                  { id: 'default', title: 'Deterministic', desc: 'Offline Rulebook', badge: 'No Key' },
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
                      padding: '14px',
                      cursor: 'pointer',
                      background: aiProvider === p.id ? 'rgba(0, 229, 255, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <span style={{ fontSize: '13px', fontWeight: 600, color: aiProvider === p.id ? '#FFF' : 'var(--text-secondary)' }}>
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

              {/* Conditional AI Key Inputs */}
              {aiProvider === 'openai' && (
                <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '18px', marginBottom: '22px' }}>
                  <label style={{ display: 'block', fontSize: '11.5px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                    OpenAI API Key <span style={{ color: 'var(--sev-crit)' }}>*</span>
                  </label>
                  <input
                    type="password"
                    className="input"
                    placeholder="sk-proj-..."
                    value={openaiKey}
                    onChange={(e) => {
                      setOpenaiKey(e.target.value);
                      setAiResult(null);
                    }}
                    style={{ width: '100%', fontFamily: 'var(--font-mono)', fontSize: '12px', marginBottom: '14px' }}
                  />

                  <label style={{ display: 'block', fontSize: '11.5px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                    OpenAI Model
                  </label>
                  <select
                    className="input"
                    value={openaiModel}
                    onChange={(e) => setOpenaiModel(e.target.value)}
                    style={{ width: '100%', fontSize: '12px' }}
                  >
                    <option value="gpt-4o-mini">gpt-4o-mini (Fast &amp; Cost-Effective - Default)</option>
                    <option value="gpt-4o">gpt-4o (Maximum Capability)</option>
                  </select>
                </div>
              )}

              {aiProvider === 'anthropic' && (
                <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '18px', marginBottom: '22px' }}>
                  <label style={{ display: 'block', fontSize: '11.5px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                    Anthropic API Key <span style={{ color: 'var(--sev-crit)' }}>*</span>
                  </label>
                  <input
                    type="password"
                    className="input"
                    placeholder="sk-ant-api03-..."
                    value={anthropicKey}
                    onChange={(e) => {
                      setAnthropicKey(e.target.value);
                      setAiResult(null);
                    }}
                    style={{ width: '100%', fontFamily: 'var(--font-mono)', fontSize: '12px', marginBottom: '14px' }}
                  />

                  <label style={{ display: 'block', fontSize: '11.5px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                    Anthropic Claude Model
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

              {/* AI Test Feedback */}
              {aiResult && (
                <div
                  style={{
                    padding: '14px 18px',
                    borderRadius: 'var(--radius-sm)',
                    marginBottom: '22px',
                    fontSize: '12px',
                    background: aiResult.is_valid ? 'rgba(0, 230, 118, 0.08)' : 'rgba(255, 23, 68, 0.08)',
                    border: `1px solid ${aiResult.is_valid ? 'var(--sev-low)' : 'var(--sev-crit)'}`,
                    color: aiResult.is_valid ? 'var(--sev-low)' : 'var(--sev-crit)',
                  }}
                >
                  {aiResult.is_valid ? (
                    <div>✓ {aiResult.provider.toUpperCase()} AI credentials verified successfully!</div>
                  ) : (
                    <div>✕ AI Key Verification Failed: {aiResult.error_message}</div>
                  )}
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <button type="button" className="btn" onClick={() => setStep(2)} style={{ fontSize: '12px' }}>
                  &larr; Back
                </button>
                <div style={{ display: 'flex', gap: '10px' }}>
                  {(aiProvider === 'openai' || aiProvider === 'anthropic') && (
                    <button
                      type="button"
                      className="btn"
                      onClick={handleTestAi}
                      disabled={isTestingAi}
                      style={{ fontSize: '12px' }}
                    >
                      {isTestingAi ? 'Verifying Key…' : 'Test AI Key'}
                    </button>
                  )}
                  <button
                    type="button"
                    className="btn btn-cyan"
                    onClick={handleStep3Next}
                    style={{ fontSize: '12px', padding: '8px 20px', fontWeight: 600 }}
                  >
                    Review Setup &rarr;
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Review, Finalize & Run Audit */}
          {step === 4 && (
            <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '28px' }}>
              <h2 style={{ fontSize: '16px', fontWeight: 600, color: '#FFF', margin: '0 0 6px 0' }}>
                Finalize Configuration &amp; Begin Audit
              </h2>
              <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', margin: '0 0 22px 0' }}>
                Review your tenant parameters before unlocking dashboard access.
              </p>

              <div style={{ background: '#0a0d14', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '18px', marginBottom: '22px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', fontSize: '12px' }}>
                  <div>
                    <span style={{ color: 'var(--text-tertiary)', display: 'block', marginBottom: '4px' }}>Target AWS Account:</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--cyan-bright)' }}>
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

              <div style={{ marginBottom: '22px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', fontSize: '12.5px', color: '#FFF' }}>
                  <input
                    type="checkbox"
                    checked={triggerScan}
                    onChange={(e) => setTriggerScan(e.target.checked)}
                    style={{ accentColor: 'var(--cyan-bright)', width: '16px', height: '16px' }}
                  />
                  <span>Trigger Initial Multi-Service Security Audit Immediately (Recommended)</span>
                </label>
                <p style={{ margin: '4px 0 0 26px', fontSize: '11.5px', color: 'var(--text-tertiary)' }}>
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
                  style={{ fontSize: '13px', padding: '10px 26px', fontWeight: 600 }}
                >
                  {isSubmitting ? 'Starting Initial Audit…' : 'Complete Setup & Enter Dashboard 🚀'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
