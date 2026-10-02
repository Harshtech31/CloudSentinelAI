import gcpLogo from '../assets/icons/providers/gcp.svg';
import awsLogo from '../assets/icons/providers/aws.svg';
import azureLogo from '../assets/icons/providers/azure.svg';

const PROVIDER_LOGOS = {
  aws: awsLogo,
  gcp: gcpLogo,
  azure: azureLogo,
} as const;

export type CloudProviderId = keyof typeof PROVIDER_LOGOS;

interface CloudProviderIconProps {
  provider: CloudProviderId;
  /** Rendered height in px; width follows the logo's aspect ratio. */
  size?: number;
  title?: string;
}

/**
 * Official provider brand mark (AWS / Google Cloud / Microsoft Azure).
 * Wordmark logos are not square, so height is fixed and width stays
 * proportional. Sources and usage terms: assets/icons/README.md.
 */
export function CloudProviderIcon({ provider, size = 16, title }: CloudProviderIconProps) {
  const src = PROVIDER_LOGOS[provider];
  if (!src) return null;
  return (
    <img
      src={src}
      alt={title ?? `${provider} logo`}
      style={{ height: size }}
      className="brand-icon"
    />
  );
}
