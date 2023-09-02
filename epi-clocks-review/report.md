# Technical report on epigenetic clock theory

## Introduction

Aging manifests through a variety of phenotypes that emerge during late adulthood and senescence. The relationship between chronological age and the onset of these traits, however, remains complex and inconsistent. An older individual might present as clinically "younger" in some respects, while others may never exhibit certain signs of aging. Moreover, with the advent of anti-aging therapies, there is an unmet need to measure *biological* age instead of *chronological* age[^1]. In other words, a distinction must be made between ordinary clocks that measure age in linear time and biological clocks that measure senescence-associated phenotypes. DNA methylation-based age predictors (‘epigenetic clocks’) have emerged in the past decade to address the need for biological clocks[^2][^3].

The idea that a constant rate of molecular change can be used to measure time is among the oldest ideas in the field of molecular evolution[^4]. Similar to epigenetic clocks, evolutionary clocks were readily adopted and used extensively to date speciation events. As statistical genomics approaches matured, it became clear that many of the earliest findings based on these clocks were biased by inadequate methodologies[^5][^6]. Because epigenetic clocks measure individuals over a lifespan, as opposed to species over millions of years, they do not suffer from the same issues that beset early evolutionary clocks. Nevertheless, epigenetic clocks are still in their infancy and yet already have their own challenges[^7].

Epigenetic clocks have been widely embraced in aging research as the definitive measure of biological aging. While these clocks boast remarkable accuracy in predicting chronological age—and possibly biological age too—there remains scant underlying theory to substantiate this parlor trick. We have pinpointed three "overriding" challenges to epigenetic clock theory, cast as questions:

1. What do epigenetic clocks measure?
2. Are epigenetic clocks statistically sound?
3. Is the study and usage of epigenetic clocks justified?

The purpose of this report is to provide a technical overview of the theory behind epigenetic clocks through the lens of these three challenges. We begin with a brief summary of the emerging theory, followed by a review of the literature. We then introduce the notation and mathematical background necessary to understand the theory. We then describe the methods and approaches used to develop epigenetic clocks, including data sources and preprocessing, model development, and analysis techniques. We conclude with a discussion of the current state of the theory and future directions.

## Literature Review

Summary of epigenetic clocks, adapted from Table S1[^8]:

| Clock      | First Author, Year | Training phenotype | # of CpGs | Tissues            | Species           |
|------------|--------------------|--------------------|-----------|--------------------|-------------------|
| Bocklandt  | Bocklandt S, 2011  | Chronological age  | 1         | Saliva             | Human             |
| Garagnani  | Garagnani P, 2012  | Chronological age  | 1         | Whole blood        | Human             |
| Hannum     | Hannum G, 2013     | Chronological age  | 71        | Whole blood        | Human             |
| Horvath1   | Horvath S, 2013    | Chronological age  | 353       | Multi-tissue (51)  | Human             |
| Weidnera   | Weidner CI, 2014   | Chronological age  | 3         | Whole blood        | Human             |
| Vidal-Bralo| Vidal-Bralo L, 2016| Chronological age  | 8         | Whole blood        | Human             |
| Yang       | Yang Z, 2016       | Chronological age  | 385       | Whole blood        | Human             |
| PhenoAge   | Levine M, 2018     | Phenotypic Age     | 513       | Whole blood        | Human             |
| Horvath    | Horvath S, 2018    | Chronological age  | 391       | Skin               | Human             |
| Zhang1      | Zhang W, 2019      | Chronological age  | 515       | Multi-tissue (2)  | Human             |
| Zhang2      | Zhang W, 2019      | Chronological age  | N/A       | Multi-tissue (2)  | Human             |
| Haghani1   | Haghani A, 2023    | Chronological age  | 336       | Multi-tissue (59)  | Pan-species (348)  |
| Haghani2   | Haghani A, 2023    | Chronological age  | 817       | Multi-tissue (59)  | Pan-species (348)  |
| Haghani3   | Haghani A, 2023    | Chronological age  | 761       | Multi-tissue (59)  | Pan-species (348)  |

## Notation

### Definitions

***Age* vs. *Aging***: It can be challenging, theoretically and semantically, to distinguish between the natural language definition of age and the predictions from epigenetic clocks. For the purposes of this report, we draw the analogy

$$
\text{age}:\text{aging}::\text{lifespan}:\text{healthspan}
$$

and terms like "youthful" and "older" are used to quantify *aging*, the predicted age of an individual. When ambiguous, we will write *chronological age* to refer to *age*.

***Epigenome* vs. *Methylome***: We rarely draw a distinction between the epigenome and the methylome. We adopt conventions from the literature for referring to DNA methylation-based clocks as epigenetic clocks.

**Core (epigenetic) clocks**: We define the "core" epigenetic clocks as the three clocks from Horvath, Hannum, and PhenoAge (sometimes referred to as Levine's clock), per the definition used by the R package `methylCIPHER`[^9]. We discuss "non-core" clocks in *Other Clocks and a Model Zoo*.

**Relative age**: In this report, we refer to all transformations of chronological age as yielding a **relative age**. There are multiple definitions for the transformation functions that yield relative age, $f(\mathbf{y}^*): \mathbb{R}^\text{chron} \rightarrow \mathbb{R}^\text{rel}$, including

- $f_1$: log-transformation
- $f_2$: ratio of (log-transformed?) chronological age to maximum lifespan, within the range of $[0,1]$
- $f_3$: a function of age at sexual maturity and gestation time

Chronological age is always log-transformed, which reduces the linear space over old age. This transformation makes the original chronological age $\mathbf{y}^*$ linear with epigenetic age, since epigenetic clocks "tick faster" during development[^13].

In contrast to our usage, the literature only refers to the $f_2$- and $f_3$-transformed ages as relative[^10]. The purpose of relative ages is to enable comparisons between different species, which may have very different lifespans. The transformation $f_3$ was developed for when knowledge of maximum lifespan is unknown or suspected to be less accurate than that of landmark events.

### Symbols

| Symbol | Name | Description |
|-|-|-|
| $\mathbf{X}$ | Methylation data | Sample $\times$ probe matrix of beta values |
| $\mathbf{y}^*$ | Age | Chronological age |
| $\mathbf{y}$ | Relative age | Transformed chronological age |
| $\tilde{\mathbf{y}}$ | Phenotypic age | Modified age measure based on health phenotypes |
| $\hat{\mathbf{y}}$ | Epigenetic age | Clock-predicted age based on methylome |
| $\hat{\beta}$ | CpG weights | Estimated contribution of a single CpG to age |

## Methods and Approaches

### Data Sources: Preprocessing

The core clocks require

- an outcome variable, representing chronological age
- predictor variables, representing methylation data
- phenotype covariates

For the outcome variable, the core clocks use relative (chronological) age. Relative age, $\mathbf{y}$, is generated from chronological ages, $\mathbf{y}^*$, using a transformation function $f(\mathbf{y}^*)$ (see **Relative age** withing *Definitions*). The simplest and most common transformation is a log-transformation,

$$
\mathbf{y} = f_1(\mathbf{y}^*) = \log(\mathbf{y}^*).
$$

Unless otherwise specified, $\mathbf{y}$ is assumed to be generated using $f_1$. For PhenoAge, there is an additional step to calculate a modified age measure $\tilde{\mathbf{y}}$ based on relative age $\mathbf{y}$ and health phenotypes.

Different data sets of methylation data, $\mathbf{X}$, are used to train the core clocks. The data sets are summarized in the table below.

| Clock | Symbol | Description |
|-|-|-|
| Horvath | $\mathbf{X}_\text{MT}$ | Multi-tissue |
| Hannum | $\mathbf{X}_\text{blood}$ | Whole blood |
| PhenoAge | $\mathbf{X}_\text{InCHIANTI}$ | Whole blood[^11] |

### Data Sources: Missing Data

The most common missing data problem in epigenetic clocks is missing probe information in the methylation data. The probe may be missing because of how the array was designed, or from a lack of orthologs across species. In the original core clocks papers, there is no mention of how missing data is handled, because they have no missing data. Subsequent papers will either ignore that there is missing data, or impute the missing data using the mean or median of the probe.

### Model Development: Weighting CpGs

The core clocks all use the same objective function $F$,

$$
F(\mathbf{X},\mathbf{y}) = \underbrace{l(\hat{\mathbf{y}} \text{ vs. } \mathbf{y})}_{\text{age prediction error}} + \underbrace{\mathcal{P}_{\Omega}(\hat{\beta})}_{\text{select subset of CpGs}},
$$

where $l$ is the loss function, $\hat{\mathbf{y}}=\hat{r}(\mathbf{X})$ is the predicted epigenetic age (here, $\hat{r}(\mathbf{X})=\mathbf{X}\hat{\beta}$), and $P_{\Omega}(\hat{\beta})$ is the sparsity penalty on the coefficients per additional parameters $\Omega$. The sparsity penalty is meant to perform subset selection and shrinkage. Specifically, an elastic net penalty will shrink the absolute values of CpG weights of correlated CpGs toward each other and select correlated CpGs in groups[^12].

> ⚠️ **_Technical Note:_**
These models all use a least-squares loss $l(\hat{r}(\mathbf{X}), \mathbf{y}) = \sum_{i=1}^n \hat{\epsilon}_i^2$ for $n$ observations. where $\hat{\epsilon} = \mathbf{y} - \mathbf{X}\hat{\beta}$. The authors fit an intercept term, which we drop with the equivalent assumptions that either $\mathbf{X}$ contains a column of $1$ s or $\mathbf{y}$ and $\mathbf{X}$ have been centered. These models also all use an elastic net penalty, $\mathcal{P}_{\lambda, \alpha}(\hat{\beta}) = \lambda\left(\alpha \|\hat{\beta}\|_1 + \frac{1-\alpha}{2} \|\hat{\beta}\|_2^2\right).$

The preprocessing steps and training data constitute the primary differences among the core clocks (see Data Sources and Preprocessing),

$$
F(a, b) =
    \begin{cases}
        a=\mathbf{X}_\text{MT},&\quad b=\mathbf{y}, &\quad\text{if Horvath} \\
        a=\mathbf{X}_\text{blood},&\quad b=\mathbf{y}, &\quad\text{if Hannum} \\
        a=\mathbf{X}_\text{InCHIANTI},&\quad b=\tilde{\mathbf{y}}, &\quad\text{if PhenoAge},
    \end{cases}
$$

which leads to models with different numbers of non-zero CpG weights, but similar predictive results[^2].

### Model Development: Inference Algorithm

The core clocks all estimate CpG weights $\hat{\beta}_i$ for $i=1,2,\ldots,p$ by minimizing the objective function, $\min_{\beta \in \mathbb{R}^p} F(\mathbf{X},\mathbf{y})$, using coordinate descent.

> ⚠️ **_Technical Note:_**
Subgradient conditions for the core clock objective function $F$, given $l$ and $\mathcal{P}$, mean that path algorithms can calculate CpG weights exactly. The coordinate descent update is $$ \hat{\beta}_i = \begin{cases} 0 &\quad \text{if }\lvert \tilde{\beta}_i \rvert < \alpha \lambda; \\ \frac{\text{sign}(\tilde{\beta}_i)(\lvert \tilde{\beta}_i \rvert - \alpha \lambda)}{1+(1-\alpha)\lambda} &\quad \text{otherwise}. \end{cases} $$ for CpG $i$[^12].

### Model Development: Epigenetic Age Prediction

As discussed above, the core clocks define $\hat{\mathbf{y}}=\mathbf{X}\hat{\beta}$, so that the predicted epigenetic age is a linear combination of CpG weights and methylation data,
$$
\begin{align*}
    \hat{y}_i &= \mathbf{X}_i\hat{\beta} \\
    &= \hat{\beta}_1 x_{i,1} + \hat{\beta}_2 x_{i,2} + \cdots + \hat{\beta}_p x_{i,3} \\
\end{align*}
$$
for individual $i$. Note that all of the core clocks use the penalized coefficients as CpG weights for prediction.

> ⚠️ **_Technical Note:_**
Estimated CpG weights will be biased (or "shrunk") toward zero by the penalty term $\mathcal{P}$. The bias is non-uniform and partially independent of their true weights, $\beta$. It is true that shrinkage may reduce overfitting in high-dimensional settings, and so may make the epigenetic clocks more generalizable[^16]. However, shrinkage may be undesirable if the goal is to identify the most important CpGs and their true weights. Numerous approaches have been developed within the lasso linear model framework to de-bias estimates, and one of the simplest approaches uses a Lasso-OLS hybrid estimator that refits an OLS model on the subset of non-zero CpGs[^15].

### Other Clocks and a Model Zoo

We introduce new notation write each clock $\mathcal{M}$ and to summarize it in the context of all existings clocks, $\mathbb{M} = \{\mathcal{M}_\text{Horvath}, \mathcal{M}_\text{Hannum}, \ldots\}$:

$$
\begin{align*}
    \mathcal{M}_\text{Horvath} &= \{
             &\quad \mathbf{X}_\text{MT},
             &\quad \mathbf{y},
             &\quad \hat{r}_\text{dot},
             &\quad l_\text{RSS},
             &\quad \mathcal{P}_{\alpha, \lambda}
        \quad\} &\quad [\text{00}] \\

    \mathcal{M}_\text{Hannum} &= \{
             &\quad \mathbf{X}_\text{blood},
             &\quad \mathbf{y},
             &\quad \hat{r}_\text{dot},
             &\quad l_\text{RSS},
             &\quad \mathcal{P}_{\alpha, \lambda}
        \quad\} &\quad [\text{00}] \\

    \mathcal{M}_\text{PhenoAge} &= \{
             &\quad \mathbf{X}_\text{InCHIANTI},
             &\quad \tilde{\mathbf{y}},
             &\quad \hat{r}_\text{dot},
             &\quad l_\text{RSS},
             &\quad \mathcal{P}_{\alpha, \lambda}
        \quad\} &\quad [\text{00}] \\

    \mathcal{M}_\text{Zhang1} &= \{
             &\quad \mathbf{X}_\text{blood, saliva},
             &\quad \mathbf{y},
             &\quad \hat{r}_\text{dot},
             &\quad l_\text{RSS},
             &\quad \mathcal{P}_{\alpha, \lambda}
        \quad\} &\quad [\text{00}] \\

    \mathcal{M}_\text{Zhang2} &= \{
             &\quad \mathbf{X}_\text{blood, saliva},
             &\quad \mathbf{y},
             &\quad \hat{r}_\text{dot},
             &\quad l_\text{RSS},
             &\quad \text{BLUP}
        \quad\} &\quad [\text{00}] \\

    \mathcal{M}_\text{Haghani1} &= \{
             &\quad \mathbf{X}_\text{Zoo},
             &\quad \mathbf{y},
             &\quad \hat{r}_\text{dot},
             &\quad l_\text{RSS},
             &\quad \mathcal{P}_{\alpha, \lambda}
        \quad\} &\quad [\text{00}] \\

    \mathcal{M}_\text{Haghani2} &= \{
             &\quad \mathbf{X}_\text{Zoo},
             &\quad f_2(\mathbf{y}^*),
             &\quad \hat{r}_\text{dot},
             &\quad l_\text{RSS},
             &\quad \mathcal{P}_{\alpha, \lambda}
        \quad\} &\quad [\text{00}] \\

    \mathcal{M}_\text{Haghani3} &= \{
             &\quad \mathbf{X}_\text{Zoo},
             &\quad f_3(\mathbf{y}^*),
             &\quad \hat{r}_\text{dot},
             &\quad l_\text{RSS},
             &\quad \mathcal{P}_{\alpha, \lambda}
        \quad\} &\quad [\text{00}] \\

\end{align*}
$$

## Code Implementation

To fit the core clock models, the authors use optimization routines in the R software `glmnet`. Assuming that input data `X` and `y` are preprocessed per the respective clock, then the entire code base for these epigenetic clocks can be represented by a few lines of code

```R
library(glmnet)

# Make clock
mod_cv <- cv.glmnet(X, y, alpha = 0.5, nfolds = 10)
mod <- glmnet(X, y, alpha = 0.5, lambda = mod_cv$lambda.1se)

# Run clock
y_hat <- predict(mod, s = mod_cv$lambda, newx = X)
```

as described here [^14], for instance.

Historically, the lack of robust, standalone software for deriving or using the core epigenetic clocks has been glaring. Few of these clocks adhere to the SOLID principles of software design, a situation that might be attributed to the code's apparent simplicity. Some clocks are proprietary, some are found only in Microsoft Word documents, others are obscured behind user interfaces, and some are simply unavailable. Even when clocks are accessible, it's often unclear how to use the code to replicate the results from original studies.

This shortage of reliable software has likely spurred the creation of new epigenetic clocks. Researchers who put in the effort to write the code base for a clock may be less likely to use an existing one, opting to create their own instead, or more likely to make small adjustments. This creates a problem, as it's unclear whether new clocks offer improvements or are even needed. The growing number of new clocks complicates the field, making it difficult to compare results across studies and to know which clock to use.


### Existing Software for Building Clocks

Publishing software demands a meticulous approach to development. Perhaps it was the absence of this care that led to a significant error in the original paper for the Horvath clock[^13]. This "software coding error" remained uncorrected for 15 months after the paper's publication, only to be addressed in an extensive erratum[^99]. What adds intrigue is that the author knew about this issue before the paper was published[^999], though after it was accepted. Yet, those eager to use the clock had to navigate through scattered .txt files labeled as 'tutorials,' attempting to understand how to fit the clock and locate the error themselves.

Compounding this problem is the challenge of data availability. For instance, in an analysis of the impact of cell composition heterogeneity on methylation[^231], the authors explain:

> One study, Horvath et al.[^23114903], was not included in the manuscript because the GEO entry lacked raw data

This omission barred the study's inclusion in the analysis, highlighting another layer of complexity when replicating clock-building.

### Existing Software for Using Clocks

A recent piece of software, `methylCIPHER`[^9], has at least provided a way to *use* epigenetic clocks. The software is written in R and is available on GitHub. In its assets, `methylCIPHER` provides the CpGs needed by each clock. The software is well-documented and provides a simple interface for users to fit a large number of clocks to predict age.

## Discussion

### Challenge 1: What do epigenetic clocks measure?

The core clocks cannot disentangle changes in methylation from changes to the proportions of cells with differing methylomes. Using 'cellular heterogeneity probes'[^231], a study[^030484] found that many CpGs used by the core clocks are confounded by omitting cellular composition:

> The [Age acceleration residuals (AAR)]-associated probes from the age predictors of Horvath and Hannum were enriched in CpG sites showing DNA methylation heterogeneity across cell types, suggesting AAR from these predictors is affected by the variation in cellular composition. The sensitivity analysis confirmed that no significant (P < 0.05/4) associations were observed after adjusting for white blood cell counts (Table 2). This demonstrates that the difference in the cellular makeup of the samples in our test sets is a confounder in the association between AAR from the Hannum/Horvath age predictors and mortality. This result was not consistent with what has been reported by the previous study. ... More datasets with measured white blood cell counts are needed to increase detection power.

### Challenge 2: Are epigenetic clocks statistically sound?

Like evolutionary clocks, epigenetic clocks may also suffer from non-uniform (de)methylation rates over time. A study[^210414] reported that a number of CpG sites show longitudinal variation in methylation rates across individuals, a violation to the uniform-rate assumption of clocks.

### Challenge 3: Is the study and usage of epigenetic clocks justified?



### Popular Recommendations for Using Epigenetic Clocks



### Our Recommendations for Using Epigenetic Clocks

Don't.

## References

[^1]: López-Otín C et al. (2023). Hallmarks of aging: An expanding universe.
[^2]: Horvath S and Raj K (2018). DNA methylation-based biomarkers and the epigenetic clock theory of ageing. [[paper](https://www.nature.com/articles/s41576-018-0004-3)]
[^3]: Seale K, Horvath S, Teschendorff A, Eynon N, and Voisin S (2022). Making sense of the ageing methylome.
[^4]: Zuckerkandl E and Pauling LB (1962). Molecular disease, evolution, and genetic heterogeneity.
[^5]: Graur D and Martin W (2004). Reading the entrails of chickens: molecular timescales of evolution and the illusion of precision. [[paper](https://www.sciencedirect.com/science/article/pii/S0168952503003421)]
[^6]: Balding D, Moltke I, and Marioni J (2019). Handbook of Statistical Genomics. [[book](https://onlinelibrary.wiley.com/doi/book/10.1002/9781119487845)]
[^7]: Bell et al. (2019). DNA methylation aging clocks: challenges and recommendations.
[^8]: Liu Z et al. (2020). Underlying features of epigenetic aging clocks in vivo and in vitro. [[paper](https://doi.org/10.1111/acel.13229)]
[^9]: Thrush KL, Higgins-Chen AT, Liu Z, and Levine ME (2022). R methylCIPHER: A Methylation Clock Investigational Package for Hypothesis-Driven Evaluation & Research. [[paper](https://doi.org/10.1101/2022.07.13.499978)] [[code](https://github.com/MorganLevineLab/methylCIPHER)]
[^10]: Lu AT, Fei Z et al. (2023). Universal DNA methylation age across mammalian tissues.
[^11]: The InCHIANTI Study. [[link](https://www.nia.nih.gov/inchianti-study)].
[^12]: Efron B (2016). Computer Age Statistical Inference: Algorithms, Evidence, and Data Science.
[^13]: Horvath S (2013). DNA methylation age of human tissues and cell types. [[paper](https://doi.org/10.1186/gb-2013-14-10-r115)].
[^99]: Horvath S (2015). Erratum to: DNA methylation age of human tissues and cell types. [[paper](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-015-0649-6)].
[^999]: [[archived comments](https://genomebiology.biomedcentral.com/articles/10.1186/gb-2013-14-10-r115/comments)]
[^14]: Horvath S, Haghani A, Zoller JA et al. (2022). Epigenetic clock and methylation studies in marsupials: opossums, Tasmanian devils, kangaroos, and wallabies. See `Supplementary file2`. [[paper](https://doi.org/10.1007/s11357-022-00569-5)].
[^15]: Bühlmann P and van de Geer S (2011). Statistics for High-Dimensional Data: Methods, Theory and Applications.
[^16]: van Swet E and Cator E (2020). The Significance Filter, the Winner's Curse and the Need to Shrink. [[paper](https://arxiv.org/abs/2009.09440)]
[^210414]: Zhang Q et al. (2018). Genotype effects contribute to variation in longitudinal methylome patterns in older people. [[paper](https://genomemedicine.biomedcentral.com/articles/10.1186/s13073-018-0585-7)]
[^23114903]: Horvath S, Zhang Y, Langfelder P, Kahn RS, Boks MP, van Eijk K, van den Berg LH, Ophoff RA (2012). Aging effects on DNA methylation modules in human brain and blood tissue.
[^231]: Jaffe AE and Irizarry RA (2014). Accounting for cellular heterogeneity is critical in epigenome-wide association studies. [[paper](https://genomebiology.biomedcentral.com/articles/10.1186/gb-2014-15-2-r31)]
[^030484]: Zhang Q et al. (2019). Improved precision of epigenetic clock estimates across tissues and its implication for biological ageing.[[paper](https://genomemedicine.biomedcentral.com/articles/10.1186/s13073-019-0667-1)]
