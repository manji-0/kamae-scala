# ZIO

When ZIO is present:

- Model use cases as `ZIO[Env, UseCaseError, A]`
- Keep domain transitions pure and call them with `ZIO.fromEither`
- Provide layers only in the composition root
- Use typed errors in the error channel instead of `Throwable` for business failures

Domain packages should not depend on `zio` unless the project explicitly colocates effect types with application code.
