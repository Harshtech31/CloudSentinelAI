import configIcon from '../assets/icons/aws/config.svg';
import cloudtrailIcon from '../assets/icons/aws/cloudtrail.svg';
import ec2Icon from '../assets/icons/aws/ec2.svg';
import internetIcon from '../assets/icons/aws/internet.svg';
import iamIcon from '../assets/icons/aws/iam.svg';
import lambdaIcon from '../assets/icons/aws/lambda.svg';
import rdsIcon from '../assets/icons/aws/rds.svg';
import s3Icon from '../assets/icons/aws/s3.svg';
import secretsManagerIcon from '../assets/icons/aws/secrets-manager.svg';
import securityGroupIcon from '../assets/icons/aws/security-group.svg';
import userIcon from '../assets/icons/aws/user.svg';
import vpcIcon from '../assets/icons/aws/vpc.svg';

const SERVICE_ICONS: Record<string, string> = {
  iam: iamIcon,
  ec2: ec2Icon,
  s3: s3Icon,
  vpc: vpcIcon,
  rds: rdsIcon,
  cloudtrail: cloudtrailIcon,
  config: configIcon,
  lambda: lambdaIcon,
  'secrets-manager': secretsManagerIcon,
  'security-group': securityGroupIcon,
  internet: internetIcon,
  user: userIcon,
};

/** Resource-type aliases so graph node types map onto service icons. */
const TYPE_ALIASES: Record<string, string> = {
  iam_user: 'user',
  iam_role: 'iam',
  iam_policy: 'iam',
  ec2_instance: 'ec2',
  s3_bucket: 's3',
  security_group: 'security-group',
  vpc: 'vpc',
  subnet: 'vpc',
  rds_instance: 'rds',
  cloudtrail: 'cloudtrail',
  internet: 'internet',
};

interface AwsServiceIconProps {
  /** Service key (collector key) or AssetType value. */
  service: string;
  size?: number;
  title?: string;
}

/**
 * Official AWS architecture icon for a service or resource type
 * (square art, fixed width/height). Unknown keys render nothing so
 * callers never break on a missing icon.
 */
export function AwsServiceIcon({ service, size = 20, title }: AwsServiceIconProps) {
  const key = SERVICE_ICONS[service] ? service : TYPE_ALIASES[service];
  const src = key ? SERVICE_ICONS[key] : undefined;
  if (!src) return null;
  return (
    <img
      src={src}
      alt={title ?? `AWS ${service} icon`}
      width={size}
      height={size}
      className="service-icon"
    />
  );
}
