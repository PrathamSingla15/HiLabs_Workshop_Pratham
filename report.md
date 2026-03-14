# Clinical NLP Entity Extraction Evaluation Report

## Executive Summary

- **Charts evaluated:** 30
- **Overall average error rate:** 0.3456 (Poor)
- **Event date accuracy:** 0.1875
- **Attribute completeness:** 0.5894

## Methodology

This evaluation uses a **two-pillar scoring approach**:

1. **Objective scoring (40% weight):** Rule-based heuristics including NegEx-style negation detection, INN drug suffix matching, heading-based temporality inference, and UI noise filtering.
2. **Subjective scoring (60% weight):** GPT-4o-mini via OpenRouter with logprobs-based weighted scoring, pass@3 with early stopping for high-confidence predictions.
3. **Score combination:** Weighted geometric mean of both pillars, converted to 0-1 error rates.

## Error Rates by Dimension

### Entity Type Classification

| Entity Type | Error Rate | Assessment |
|---|---|---|
| MEDICINE | 0.1954 | Fair |
| PROBLEM | 0.2183 | Fair |
| PROCEDURE | 0.6308 | Critical |
| TEST | 0.2924 | Fair |
| VITAL_NAME | 0.2475 | Fair |
| IMMUNIZATION | 0.4012 | Poor |
| MEDICAL_DEVICE | 0.4619 | Poor |
| MENTAL_STATUS | 0.4372 | Poor |
| SDOH | 0.4938 | Poor |
| SOCIAL_HISTORY | 0.4159 | Poor |

### Assertion Classification

| Assertion Type | Error Rate | Assessment |
|---|---|---|
| POSITIVE | 0.1629 | Fair |
| NEGATIVE | 0.4338 | Poor |
| UNCERTAIN | 0.4647 | Poor |

### Temporality Classification

| Temporality Type | Error Rate | Assessment |
|---|---|---|
| CURRENT | 0.3008 | Poor |
| CLINICAL_HISTORY | 0.2247 | Fair |
| UPCOMING | 0.4154 | Poor |
| UNCERTAIN | 0.5147 | Critical |

### Subject Attribution

| Subject Type | Error Rate | Assessment |
|---|---|---|
| PATIENT | 0.1444 | Good |
| FAMILY_MEMBER | 0.1100 | Good |

### Event Date Accuracy

- **Average accuracy:** 0.1875
- **Interpretation:** Needs improvement

### Attribute Completeness

- **Average completeness:** 0.5894
- **Interpretation:** Needs improvement

## Error Heatmap

Legend: `.` < 5% | `o` 5-10% | `O` 10-20% | `#` 20-35% | `X` > 35%

```
Entity Type          Ent.Type   Assert   Tempor  Subject
--------------------------------------------------------
MEDICINE                    O        X        X        O
PROBLEM                     #        X        X        O
PROCEDURE                   X        X        X        O
TEST                        #        X        X        O
VITAL_NAME                  #        X        X        O
IMMUNIZATION                X        X        X        O
MEDICAL_DEVICE              X        X        X        O
MENTAL_STATUS               X        X        X        O
SDOH                        X        X        X        O
SOCIAL_HISTORY              X        X        X        O
```

## Top Systemic Weaknesses

### 1. Entity type: PROCEDURE (error rate: 0.6308)

PROCEDURE entities show the highest error rate, likely due to UI noise (EMR navigation elements, fax headers, administrative text) being incorrectly classified as clinical procedures.

### 2. Temporality: UNCERTAIN (error rate: 0.5147)

This dimension shows a critical error rate, indicating significant room for improvement.

### 3. Entity type: SDOH (error rate: 0.4938)

This dimension shows a poor error rate, indicating significant room for improvement.

### 4. Assertion: UNCERTAIN (error rate: 0.4647)

This dimension shows a poor error rate, indicating significant room for improvement.

### 5. Entity type: MEDICAL_DEVICE (error rate: 0.4619)

This dimension shows a poor error rate, indicating significant room for improvement.

## Proposed Guardrails

1. **UI Noise Pre-filter:** Implement a pre-processing step to detect and exclude entities extracted from EMR navigation chrome, cover pages, fax headers, and template boilerplate. Key indicators: heading contains 'Cover Page' or 'X__page', entity text matches administrative patterns.
2. **NegEx Post-Processing Layer:** Apply NegEx-style assertion re-validation after initial extraction. Cross-check assertion labels against negation triggers (denies, without, no evidence of) in the surrounding text context.
3. **Heading-Temporality Consistency Check:** Validate that temporality labels are consistent with section headings (e.g., entities under 'Past Medical History' should be CLINICAL_HISTORY, not CURRENT).
4. **Family History Subject Auto-Correction:** Automatically set subject=FAMILY_MEMBER for all entities appearing under Family History headings, overriding the model's assignment.
5. **Attribute Completeness Enforcement:** For MEDICINE entities, require STRENGTH and FREQUENCY metadata when available in text. For TEST entities, require TEST_VALUE. Flag entities missing expected attributes for manual review.
6. **Confidence-Based Routing:** Use model confidence scores to route low-confidence extractions to human review rather than accepting them at face value.
7. **Template Detection:** Build a classifier to distinguish protocol/template language from patient-specific clinical text, preventing extraction of boilerplate content as patient entities.

## Per-Chart Summary

| Chart | Avg Error Rate | Date Accuracy | Attr Completeness | Worst Dimension |
|---|---|---|---|---|
| 019M72177_N991-796129_20241213 | 0.3584 | 0.0000 | 0.5749 | entity_type:SDOH (0.917) |
| 019W06677_J608-122479_20241212 | 0.3639 | 0.0721 | 0.6085 | entity_type:IMMUNIZATION (0.794) |
| 104W15947_J727-290663_20241213 | 0.2909 | 0.2323 | 0.5724 | entity_type:PROCEDURE (0.606) |
| 105W05861_J614-495637_20241217 | 0.3481 | 0.3984 | 0.5272 | entity_type:SOCIAL_HISTORY (0.800) |
| 161W10351_N993-588097_20241126 | 0.3385 | 0.4532 | 0.5476 | entity_type:PROCEDURE (0.725) |
| 218M89247_J736-108989_20241211 | 0.4035 | 0.0652 | 0.4952 | entity_type:MENTAL_STATUS (0.892) |
| 241W15237_N991-674329_20241216 | 0.2990 | 0.3850 | 0.6070 | assertion:UNCERTAIN (0.644) |
| 279W08692_N993-538576_20241223 | 0.3554 | 0.2334 | 0.5321 | entity_type:IMMUNIZATION (0.837) |
| 336W08434_J721-109845_20241127 | 0.4601 | 0.0326 | 0.5389 | entity_type:IMMUNIZATION (0.837) |
| 352M97319_J619-223143_20241126 | 0.3368 | 0.1631 | 0.5669 | entity_type:PROCEDURE (0.778) |
| 363M98433_J619-215908_20241128 | 0.3782 | 0.2851 | 0.6214 | subject:FAMILY_MEMBER (1.000) |
| 363W18752_J721-182830_20241128 | 0.3822 | 0.1676 | 0.5330 | assertion:NEGATIVE (0.882) |
| 371W13971_J722-244055_20241128 | 0.3510 | 0.2183 | 0.6136 | subject:FAMILY_MEMBER (1.000) |
| 400W00699_J619-210780_20241212 | 0.2905 | 0.2652 | 0.6279 | temporality:UPCOMING (0.683) |
| 410M88588_J736-100205_20241217 | 0.3811 | 0.0441 | 0.6312 | entity_type:SDOH (1.000) |
| 415M99841_J619-212434_20241204 | 0.3334 | 0.2500 | 0.6693 | entity_type:SOCIAL_HISTORY (0.837) |
| 415M99841_J619-212434_20241205 | 0.3466 | 0.1524 | 0.6691 | entity_type:SOCIAL_HISTORY (0.750) |
| 437M97350_J721-176825_20241211 | 0.3827 | 0.0000 | 0.5552 | temporality:UNCERTAIN (0.925) |
| 439W18516_J721-176816_20241211 | 0.3450 | 0.0719 | 0.5297 | entity_type:PROCEDURE (0.718) |
| 463W14981_N991-678203_20241205 | 0.3666 | 0.3933 | 0.5098 | entity_type:SOCIAL_HISTORY (0.794) |
| 579W03668_N991-799671_20241218 | 0.3159 | 0.0685 | 0.6454 | subject:FAMILY_MEMBER (1.000) |
| 612M65828_N991-802560_20241218 | 0.2923 | 0.3350 | 0.6042 | entity_type:IMMUNIZATION (0.750) |
| 630M74464_N991-796490_20241218 | 0.3114 | 0.2823 | 0.6142 | entity_type:IMMUNIZATION (0.808) |
| 712W12471_J721-133074_20241212 | 0.3439 | 0.0000 | 0.6443 | entity_type:IMMUNIZATION (0.794) |
| 735M97358_J619-210577_20241216 | 0.3641 | 0.4722 | 0.6323 | assertion:NEGATIVE (0.852) |
| 786W17536_J730-120682_20241219 | 0.2518 | 0.0357 | 0.6422 | entity_type:PROCEDURE (0.487) |
| 791M62215_N991-802622_20241219 | 0.2683 | 0.1310 | 0.6263 | entity_type:MEDICAL_DEVICE (0.659) |
| 819M83517_N991-755638_20241219 | 0.3116 | 0.3484 | 0.5665 | entity_type:IMMUNIZATION (0.837) |
| 943W19621_J727-317855_20241217 | 0.4224 | 0.0000 | 0.5791 | assertion:NEGATIVE (0.800) |
| 944W15109_J721-114759_20241205 | 0.3732 | 0.0694 | 0.5962 | entity_type:IMMUNIZATION (0.837) |
