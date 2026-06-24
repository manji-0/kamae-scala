# Scaladoc Checklist
Reference: [`../../kamae-scala/references/scaladoc.md`](../../kamae-scala/references/scaladoc.md).

## 10.1 Do public domain APIs document invariants? - Medium

Flag new public types or transitions without Scaladoc in published libraries.

## 10.2 Are error cases documented? - Medium

Flag public methods returning `Either` without describing left cases.

## 10.3 Are examples lawful? - Low

Flag Scaladoc examples using `.get` or invalid fixture data.

## 10.4 Are related types linked? - Low

Flag state machines documented without links between states and events.

## 10.5 Is Scaladoc scope appropriate? - Low

Flag missing docs on aggregate roots while internal helpers are over-documented.
