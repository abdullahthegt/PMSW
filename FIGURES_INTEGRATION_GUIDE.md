# Distribution Visualizations Guide

## Overview

This document provides guidance on integrating the four illustrative figures showing random distributions into your project report. These figures address your professor's feedback to improve clarity on the statistical foundations of the Automotive DSS.

## Generated Figures

### Figure 1: Gamma Distribution (Story Points)
**File:** `figures/01_gamma_distribution_story_points.png`

**Purpose:** Illustrates the Gamma distribution (α=2.5, β=8.0) used for synthetic story point generation.

**What it shows:**
- Left panel: Histogram of 5000 simulated story points overlaid with theoretical PDF
- Right panel: Cumulative Distribution Function (CDF) comparison

**Where to include:** 
- In **VALIDATION_REPORT.md**, Section 1 (Data Generation Validation) after the Team Data section
- In **README.md**, within the "Synthetic Data Generator" module description
- In a dedicated "Statistical Methodology" appendix

**Suggested caption:** 
> Story points are generated using a Gamma distribution (α=2.5, β=8.0), which provides realistic positive-valued estimates matching automotive project characteristics. The histogram shows excellent fit between simulated data (5000 samples) and the theoretical distribution.

---

### Figure 2: Normal Distribution (Velocity Prediction)
**File:** `figures/02_normal_distribution_velocity.png`

**Purpose:** Demonstrates the Normal distribution N(μ=22.2, σ=9.7) used for velocity forecasting.

**What it shows:**
- Top-left: Probability density with sample histogram
- Top-right: Q-Q plot verifying normality assumption
- Bottom-left: Confidence intervals at 68%, 80%, 90%, 95%, and 99% levels
- Bottom-right: Percentile plot for risk assessment

**Where to include:**
- In **VALIDATION_REPORT.md**, Section 2 (Velocity Predictor Validation) near the "Prediction Accuracy" subsection
- In **README.md**, within the "Velocity Predictor" module description
- In problem statement or requirements section (shows "Flaw of Averages" motivation)

**Suggested caption:**
> Velocity predictions use a Normal distribution to quantify uncertainty beyond point estimates. The Q-Q plot confirms normality, while confidence intervals (68%-99%) show the range of likely outcomes. The percentile plot illustrates risk levels for sprint planning decisions.

---

### Figure 3: Monte Carlo Simulation
**File:** `figures/03_monte_carlo_simulation.png`

**Purpose:** Shows the results of Monte Carlo simulation (5000 samples) for velocity forecasting.

**What it shows:**
- Top-left: Distribution of simulated velocity outcomes with mean and median
- Top-right: Convergence plot showing estimate stability with increasing samples
- Bottom-left: Sprint completion probability curve (P(V ≥ planned))
- Bottom-right: Risk assessment percentiles (P10, P25, P50, P75, P90)

**Where to include:**
- In **VALIDATION_REPORT.md**, Section 2, "Monte Carlo Simulation" subsection
- In **ARCHITECTURE.md** or methodology sections
- In any discussions of risk management or decision support

**Suggested caption:**
> Monte Carlo simulation (5000 samples) quantifies velocity uncertainty and enables probabilistic sprint planning. The convergence plot demonstrates reliable estimation, while the completion probability curve guides capacity planning decisions. For example, planning 30 SP provides ~20% chance of completion versus ~60% for 20 SP.

---

### Figure 4: Trend and Volatility Forecast
**File:** `figures/04_trend_and_volatility_forecast.png`

**Purpose:** Visualizes velocity trends, forecast uncertainty, and confidence bands.

**What it shows:**
- Historical velocity data with linear trend line
- 3-sprint-ahead forecast with expanding uncertainty bands
- 68%, 80%, and 95% confidence intervals
- Clear visual demarcation of forecast boundary

**Where to include:**
- In **VALIDATION_REPORT.md**, Section 2, after prediction accuracy results
- In sprint planning methodology sections
- In decision support system workflow descriptions

**Suggested caption:**
> Historical velocity shows declining trend (-1.82 SP/sprint) with forecast confidence bands expanding with time. The 95% confidence interval indicates substantial uncertainty beyond the immediate next sprint, supporting conservative planning approaches for multi-sprint commitments.

---

## Integration Instructions

### Step 1: Copy Figures to Report Directory
```bash
# Create a figures directory in the Backend folder
mkdir figures

# Figures are already generated at: e:\Automotive Managment tool\automotive-dss\Backend\figures\
```

### Step 2: Update Markdown Files

#### In VALIDATION_REPORT.md
Add the figures in these sections:

1. **After "1. DATA GENERATION VALIDATION"** - Add Figure 1 (Gamma)
   ```markdown
   ![Story Points Distribution](../figures/01_gamma_distribution_story_points.png)
   *Figure X: Gamma distribution used for story point generation*
   ```

2. **In "2. VELOCITY PREDICTOR VALIDATION"** - Add Figures 2 & 3
   ```markdown
   ![Velocity Distribution](../figures/02_normal_distribution_velocity.png)
   *Figure X: Normal distribution for velocity prediction*

   ![Monte Carlo Results](../figures/03_monte_carlo_simulation.png)
   *Figure X: Monte Carlo simulation results (5000 samples)*
   ```

3. **After "Prediction Accuracy"** - Add Figure 4
   ```markdown
   ![Trend Analysis](../figures/04_trend_and_volatility_forecast.png)
   *Figure X: Velocity trend and forecast uncertainty*
   ```

#### In README.md
Add figures in module descriptions:

```markdown
### Synthetic Data Generator
[Description...]

![Gamma Distribution](../figures/01_gamma_distribution_story_points.png)

### Velocity Predictor
[Description...]

![Velocity Distribution](../figures/02_normal_distribution_velocity.png)
```

### Step 3: Create Figure Reference Section
Add a new section to your report:

```markdown
## Appendix: Statistical Distributions

This appendix illustrates the core probability distributions underlying the DSS.

### A.1 Story Point Distribution
[Include Figure 1 and explanation]

### A.2 Velocity Forecasting
[Include Figures 2-4 and explanation]

```

---

## Technical Details

### Distribution Parameters

| Distribution | Parameters | Use Case |
|--------------|-----------|----------|
| Gamma(α, β) | α=2.5, β=8.0 | Story points (positive, realistic skew) |
| Normal(μ, σ) | μ=22.2, σ=9.7 | Velocity prediction (symmetric uncertainty) |
| Monte Carlo | 5000 samples | Risk quantification and decision support |

### Figure Generation

All figures are generated at **300 DPI** (publication quality) using:
- **matplotlib** - Core plotting
- **seaborn** - Enhanced styling
- **scipy.stats** - Distribution functions
- **numpy** - Numerical computations

To regenerate figures:
```bash
python src/utils/distribution_visualizations.py
```

To customize parameters:
```python
from src.utils.distribution_visualizations import DistributionVisualizer

viz = DistributionVisualizer()

# Custom story points
fig1, samples = viz.plot_gamma_distribution_story_points(
    alpha=2.5,
    beta=8.0,
    max_sp=100
)

# Custom velocity prediction
fig2 = viz.plot_normal_distribution_velocity(
    mean=25.0,  # Your baseline
    std=10.0    # Your volatility
)

fig1.savefig("custom_gamma.png", dpi=300, bbox_inches="tight")
fig2.savefig("custom_velocity.png", dpi=300, bbox_inches="tight")
```

---

## Addressing Professor Feedback

✅ **Clarity on Random Distributions:**
- Figure 1 explains story point randomness with visual fit analysis
- Figure 2 justifies Normal distribution assumption with Q-Q plot
- Figure 3 demonstrates Monte Carlo impact on decision-making
- Figure 4 shows practical application in planning

✅ **Statistical Rigor:**
- All distributions fitted to actual data/theory
- Confidence intervals quantified with z-scores
- Convergence analysis shows simulation reliability
- Risk metrics properly visualized

✅ **Publication Quality:**
- 300 DPI resolution suitable for printing
- Professional color schemes and typography
- Clear legends and axis labels
- Comprehensive captions and explanations

---

## Next Steps

1. Copy figures to your report directory
2. Update VALIDATION_REPORT.md with appropriate figure references
3. Update README.md with figures in module descriptions
4. Consider creating a dedicated "Statistical Foundation" section
5. Update figure numbers and captions to match your document format

---

*Generated: 2026-04-19*
*Distribution Visualizer: src/utils/distribution_visualizations.py*
