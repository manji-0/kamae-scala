# Application Wiring Checklist
Reference: [`../../kamae-scala/references/application-wiring.md`](../../kamae-scala/references/application-wiring.md).

## 15.1 Are use cases wired through ports? - High

Flag use cases constructing JDBC/HTTP clients directly.

## 15.2 Is the composition root the only wiring site? - Medium

Flag adapter construction scattered across domain modules.

## 15.3 Are errors mapped at the edge? - Medium

Flag transport layers returning raw `Throwable` messages to clients.
