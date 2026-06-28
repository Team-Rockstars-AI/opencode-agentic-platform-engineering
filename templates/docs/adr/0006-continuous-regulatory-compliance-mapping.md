# ADR 0006: Continuous Regulatory Compliance Mapping

## Status
Accepted

## Date
2026-06-28

## Context
Organizations operating in highly regulated sectors (e.g., Finance, Government, Healthcare) must demonstrate compliance with various regulatory frameworks such as DORA (Digital Operational Resilience Act), Dutch BIO (Baseline Informatiebeveiliging Overheid), and GDPR. Traditionally, compliance is a manual, point-in-time audit process that is disconnected from the actual technical implementation.

## Decision
We will implement a continuous regulatory compliance mapping engine (`/compliance`) that directly maps technical configurations in Infrastructure-as-Code (IaC) and pipelines to specific regulatory articles.

1.  **Codified Mapping:** The mapping between technical controls (e.g., Key Vault Purge Protection) and regulatory articles (e.g., DORA Art. 12) will be codified in the `compliance` skill.
2.  **Automated Scanning:** The `@security-auditor` agent will scan the workspace and apply this mapping to generate a real-time compliance posture.
3.  **Auditor-Ready Reporting:** The system will generate a structured `COMPLIANCE_READINESS_REPORT.md` that can be directly presented to auditors, providing a clear trail from regulatory requirement to technical implementation.

## Consequences
- **Positive:** Reduces audit preparation time and effort.
- **Positive:** Identifies compliance gaps early in the development lifecycle (Shift-Left Compliance).
- **Positive:** Provides a common language between technical teams and compliance officers.
- **Negative:** Requires ongoing maintenance of the mapping matrix as regulations evolve.
- **Negative:** Automated scanning may not cover all qualitative aspects of compliance.

## References
- [DORA (Digital Operational Resilience Act)](https://eur-lex.europa.eu/eli/reg/2022/2554/oj)
- [Dutch BIO (Baseline Informatiebeveiliging Overheid)](https://www.informatiebeveiligingsdienst.nl/product/baseline-informatiebeveiliging-overheid-bio/)
- [GDPR (General Data Protection Regulation)](https://gdpr-info.eu/)
