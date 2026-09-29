# SPEC: reconcile a synthetic statement

*The spec the three candidate implementations were generated from.*
*SYNTHETIC PLACEHOLDER DATA ONLY.*

## Signature

```python
def reconcile(lines: Sequence[str], expected_total: str) -> Reconciliation
```

`lines` are monetary amounts as **strings**, exactly as they arrive from a statement
file. `expected_total` is likewise a string.

## Reconciliation

| Field | Type | Meaning |
|---|---|---|
| `variance` | `Decimal` | The sum of `lines` minus `expected_total`, **exactly**, quantised to two decimal places |
| `matched` | `bool` | `True` if and only if `variance` is **exactly** zero |

## Rules

1. All arithmetic is exact. A binary float anywhere in the calculation is a defect.
2. `matched` is `True` **only** on an exact zero variance. There is no tolerance. A
   one-penny discrepancy is a discrepancy.
3. An empty statement has `variance == -expected_total` and `matched == False`, unless
   `expected_total` is `"0.00"`, in which case `matched` is `True`.
4. `variance` is always quantised to two decimal places.
