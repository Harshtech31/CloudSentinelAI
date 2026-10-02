# Cloud Provider & Service Icons

Official vendor icon assets used across the console UI.

## Sources

| Folder | Contents | Source | Usage |
|---|---|---|---|
| `providers/aws.svg` | AWS logo (wordmark) | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Amazon_Web_Services_Logo.svg) (AWS brand) | Subject to [AWS trademark policy](https://aws.amazon.com/trademark/) |
| `providers/gcp.svg` | Google Cloud logo | [cloud.google.com/icons](https://cloud.google.com/icons) icon package | Google brand guidelines apply |
| `providers/azure.svg` | Microsoft Azure logo | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Microsoft_Azure.svg) (Microsoft brand) | [Microsoft trademark guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks) |
| `aws/*.svg` | AWS architecture service & resource icons (IAM, EC2, S3, VPC, RDS, CloudTrail, Config, Lambda, Secrets Manager, Internet, User, Firewall) | [AWS Architecture Icons toolkit](https://aws.amazon.com/architecture/icons/), Q1-2023 asset package | AWS permits use in diagrams and product materials per the toolkit terms |

## Notes

- AWS has no dedicated "Security Group" resource icon in the toolkit;
  `aws/security-group.svg` is the official generic Firewall resource
  icon (`Res_Firewall_48_Light.svg`) used as the closest match.
- Files are used as-is (colors included); sizing is handled in CSS so
  future re-downloads of updated icon packs drop in cleanly.
- Brand logos are wordmarks, not squares — render them with fixed
  height and proportional width (`CloudProviderIcon`).
