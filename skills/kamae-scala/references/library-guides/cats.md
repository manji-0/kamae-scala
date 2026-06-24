# Cats and Cats Effect

When `cats` or `cats-effect` is present:

- Use `Monad`, `Functor`, and `ApplicativeError` constraints in use-case traits when appropriate
- Keep domain transitions free of `F[_]` unless there is a compelling reason
- Map adapter errors with `attempt`/`handleErrorWith` at infrastructure boundaries
- Prefer `IO`/`F` deferral for I/O; do not block inside `flatMap` chains without `blocking`

For error channels, `Either` in pure domain code and `F[Either[E, A]]` or `ApplicativeError[F, E, *]` in application code are both acceptable when used consistently.
