# PureConfig

PureConfig reads configuration files, not domain commands.

## Config Case Classes Are Boundary Types

Load config into case classes with defaults documented explicitly, then validate into domain types.

## Secrets

Do not store secrets in plain config fields logged at startup. Use environment-specific secret providers and redacting wrappers.

See [`boundary-defense.md`](../boundary-defense.md).
