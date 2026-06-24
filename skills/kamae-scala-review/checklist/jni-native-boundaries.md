# JNI and Native Boundaries Checklist
Reference: [`../../kamae-scala/references/jni-native-boundaries.md`](../../kamae-scala/references/jni-native-boundaries.md).

## 8.1 Is native code absent from domain logic? - High

Flag JNI/JNA/native calls in domain or transition code.

## 8.2 Are native wrappers small and safe? - High

Flag wide native APIs used directly from application code.

## 8.3 Are native invariants documented? - Medium

Flag native wrappers without documented input/output contracts.

## 8.4 Does native code bypass domain validation? - High

Flag adapters passing unvalidated external input to native libraries.

## 8.5 Are native boundaries tested? - Medium

Flag native integrations without adapter-level tests or fakes.
