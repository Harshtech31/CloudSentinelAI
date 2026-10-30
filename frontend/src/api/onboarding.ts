import { api } from './client';

export interface ValidateAwsPayload {
  aws_access_key_id: string;
  aws_secret_access_key: string;
  aws_session_token?: string;
  region: string;
}

export interface ValidateAwsResult {
  is_valid: boolean;
  account_id?: string;
  arn?: string;
  user_id?: string;
  error_message?: string;
}

export interface ValidateAiPayload {
  provider: 'bedrock' | 'openai' | 'anthropic' | 'default';
  api_key?: string;
  model?: string;
  aws_region?: string;
}

export interface ValidateAiResult {
  is_valid: boolean;
  provider: string;
  model?: string;
  error_message?: string;
}

export interface SaveOnboardingPayload {
  aws_access_key_id?: string;
  aws_secret_access_key?: string;
  aws_session_token?: string;
  aws_default_region: string;
  ai_provider: 'bedrock' | 'openai' | 'anthropic' | 'default';
  openai_api_key?: string;
  openai_model?: string;
  anthropic_api_key?: string;
  anthropic_model?: string;
  trigger_initial_scan?: boolean;
}

export interface OnboardingStatus {
  is_onboarded: boolean;
  aws_configured: boolean;
  aws_account_id?: string;
  aws_default_region: string;
  ai_provider: string;
  openai_configured: boolean;
  anthropic_configured: boolean;
  bedrock_configured: boolean;
  recommended_iam_policy?: Record<string, unknown>;
}

export async function getOnboardingStatus(): Promise<OnboardingStatus> {
  const { data } = await api.get<OnboardingStatus>('/onboarding/status');
  return data;
}

export async function getIamPolicy(): Promise<Record<string, unknown>> {
  const { data } = await api.get<Record<string, unknown>>('/onboarding/iam-policy');
  return data;
}

export async function validateAwsCredentials(payload: ValidateAwsPayload): Promise<ValidateAwsResult> {
  const { data } = await api.post<ValidateAwsResult>('/onboarding/validate-aws', payload);
  return data;
}

export async function validateAiCredentials(payload: ValidateAiPayload): Promise<ValidateAiResult> {
  const { data } = await api.post<ValidateAiResult>('/onboarding/validate-ai', payload);
  return data;
}

export async function completeOnboarding(payload: SaveOnboardingPayload): Promise<OnboardingStatus> {
  const { data } = await api.post<OnboardingStatus>('/onboarding/complete', payload);
  return data;
}
