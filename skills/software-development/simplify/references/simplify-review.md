# Simplify review checklist

Ask these questions before final review:

- Can this be narrower without losing correctness?
- Did the implementation add compatibility or migration behavior not requested by the plan?
- Are tests checking the contract directly?
- Are there duplicated helpers that create drift risk?
- Are guardrails protecting security/data integrity rather than cosmetic assumptions?
- Would this cleanup make review easier without changing behavior?
