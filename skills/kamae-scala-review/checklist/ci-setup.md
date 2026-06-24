# CI Setup Checklist
Reference: [`../../kamae-scala/references/ci-setup.md`](../../kamae-scala/references/ci-setup.md).

## 11.1 Does CI run reviewer-critical checks? - Medium

Flag missing test and format jobs for domain-heavy repos.

## 11.2 Is the matrix representative? - Medium

Flag absent integration jobs when adapters are part of the change.

## 11.3 Are risk-tied jobs present? - Medium

Flag native/crypto/migration changes without dedicated checks.

## 11.4 Are advisory checks labeled? - Low

Flag noisy jobs whose failures are ignored without documentation.

## 11.5 Can contributors reproduce CI locally? - Low

Flag CI commands missing from development docs.
