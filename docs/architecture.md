# Data Quality Guardrail Architecture

## Service Overview

Data Quality Guardrail models a dataset validation layer for teams that need to identify reliability drift before bad inputs infect revenue, growth, lifecycle, or executive decisioning systems.

It represents the sort of backend service operations and analytics teams use to surface:

- schema drift
- stale dataset loads
- critical null spikes
- duplicate collisions
- range violations

## Processing Flow

1. A dataset contract and payload are loaded into a typed request.
2. Validation checks are executed across the incoming records.
3. Severity scores are assigned to each detected issue family.
4. A consolidated report is emitted with evidence and next actions.

## Current Output Modes

- JSON API response
- terminal summary

## Validation Families

### Schema Drift

- missing required fields
- unexpected columns
- type expectation mismatches

### Freshness Lag

- dataset age beyond allowed reporting window
- stale operational snapshots

### Null Spike

- critical field completeness failure
- identity or metric gaps in the dataset

### Duplicate Collision

- repeated primary keys
- duplicate event or opportunity identifiers

### Range Violation

- values outside expected numeric thresholds
- obviously invalid rates or monetary values
