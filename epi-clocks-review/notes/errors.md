# Critiques of minor errors in the literature

A list of mistakes in the literature that I've found. I'll try to keep this updated as I find more.

## In [^1]

1. authors define a transformation from chronological age to relative age, $\text{relative age} = F(\text{chronological age})$. Their model is thus written as $$F(\text{chronological age})= b_0 + b_1 \text{CpG}_1 + \cdots + b_p\text{CpG}_p + \text{error},$$ but in including an additive error term, this form confuses the realized relative age with a random variable relative age. This is a minor, but confusing, error.

2. authors write
    > The DNAm Age estimate is estimated in two steps. First, one forms a weighted linear combination of the CpGs ... The formula assumes that the DNA methylation data measure "beta" values but the formula could be adapted to other ways of generating DNA methylation data.

    yet (1) they do not specify the second step and (2) do not provide details or theoretical justifications for how the formula could be adapted to other ways of generating DNA methylation data.

## In [^2]

1. authors write
    > We profiled 15,456 samples (Fig. 1A and table S1) using a methylation array platform that provides effective sequencing depth at highly conserved CpGs across mammalian species (5). This dataset is the product of the multinational Mammalian Methylation Consortium. In previous studies, we applied supervised machine learning methods to generate DNAm-based predictors of age called epigenetic clocks for numerous species (6-31).

    which points to references [6-31] for the epigenetic clocks. Looking at these references, it appears that all but 1 are for papers that each perform an identical analytical workflow, but in a different species. They were all published in 2021, 2022, or 2023. This strikes me as an egregious polluting of the primary literature with redundant papers, and it undercuts any novelty from the Science meta-analysis paper.

2. authors do not define "relative age".

## In [^3]

1. in the associated code repository, the corresponding author responds to an issue request with[^4]
    > Hi Ellie
    Are you a team member from my collaborators?
    I have shared an important Dropbox folder with them….
    Steve

    This response does not help non-"team member" software users.

## In [^5]

1. authors write very naively about statistical modeling,

    > Box 2 Statistical strategies for building DNA methylation-based estimators of biological age
    >
    > The development of a DNA methylation-based (DNAm) age estimator requires three major decisions: the statistical prediction method (for example, penalized regression), the outcome measure (that is, a surrogate marker of biological age) and the covariates (a subset of CpGs). **Alternative statistical methods are not likely to lead to substantial improvements because both theoretical and empirical studies show that elastic net regression works extremely well** when the number of predictors ($p$) is much larger than the number of observations ($n$).
    >
    > Larger sets of CpGs should in theory result in more accurate biomarkers. However, our empirical studies indicate that relatively little is gained by looking at ever larger sets of CpGs. **The reason for this phenomenon of diminishing returns is probably because DNAm biomarkers of ageing measure global properties of the methylome that can be characterized by moderate numbers of CpGs.**
    >
    > The multi-tissue DNAm age estimator uses chronological age as a surrogate for biological age because chronological age is highly correlated with biological age and is arguably a near-optimal surrogate of biological age during development. However, other outcome measures can lead to substantial improvements in regard to mortality and morbidity prediction in adults, as can be seen from the success of the DNAm phenotypic age (PhenoAge) estimator. **Defining biologically meaningful surrogate measures of biological age, beyond chronological age, is conceptually challenging because of the dangers of confounding.**
    >
    > Another strategy for developing more powerful DNAm estimators of organismal age consists of aggregating the DNAm age estimates of multiple organs. Future research should explore how to define powerful composite biomarkers of ageing on the basis of DNAm age estimates of different accessible tissues such as skin, buccal epithelium, and adipose tissue or fluids such as blood or urine.

    where emphasis is mine and footnotes have been omitted for clarity. Some of the errors here:

    - "covariates" is used incorrectly
    - "surrogate" is used incorrectly
    - general statements about high-dimensional learning are used to make strong, specific claims about a particular dataset
    - "diminishing returns" is not the correct description for lesser decreases in prediction error in high-dimensional learning
    - Confounding is only dangerous within a causal inference framework, which is not the framework used here. Confounding is not dangerous in a predictive framework. Causal inference considerations are immaterial to definitions of a "surrogate" unless an additional assumption is made about the instrumentation of the surrogate.

## In [^6]

1. The keyword "Penalize Regression Model" should be "Penalized Regression Model".

## In [^7]

1. title claims the model is 'near the theoretical limit of accuracy,' a statement supported by correlations and RMSEs. However, this terminology is misleading. The 'theoretical limit' is defined by the authors as the actual age with an arbitrary uncertainty interval, lacking a rigorous statistical foundation. The claim of nearing a 'theoretical limit' traditionally requires a well-grounded statistical or mathematical framework, such as identifiable bounds on model bias and variance, the relationship between complexity and generalization, or the asymptotic behavior of an estimator. Without such grounding, the claim appears more heuristic than theoretical, risking a misrepresentation of the model's capabilities.

2. authors write
    > Owing to the fact that the public data were generated in multiple laboratories ..., we expected noisy data with a strong batch effect. Indeed, the results ... resulted in a mediocre model with an r2 of 0.78, a Pearson correlation of 0.89 (p = 2.82e-304), a Spearman correlation of 0.86 (p = 9.97e-258), a mean absolute error (MAE) of 1.02 days, a median absolute deviation (MAD) of 0.71 days, and a root-mean-square-error (RMSE) of 1.51 days. ... In order to mitigate this increase in variance, we developed a novel approach and binarized the transcriptome data by setting the value of each gene to 1, if the CPM is bigger than the median CPM of the corresponding sample and 0 otherwise (see Methods for details), thereby reducing the noise, but retaining the information whether a gene is strongly transcribed or not. After this binarization, we trained an elastic net regression model with nested cross-validation to obtain the best parameter setting and optimal set of genes (see Methods for details) that predict the biological age remarkably well with an r2 of 0.96, a Pearson correlation of 0.98 (p<1e-304), a Spearman correlation of 0.96 (p<1e-304), a mean absolute error of 0.46 days, a median absolute error of 0.33 days, and a RMSE of 0.66 days (Figure S1b).

    - Ambiguity in Understanding Noise and Variance: The authors' expectation of "noisy data" and their effort to "mitigate this increase in variance" lack clear definition and connection. Without explicitly describing what constitutes noise, how it is quantified, and how it relates to the observed "increase in variance," their treatment of these concepts becomes unclear. Do they consider all non-batch-related variation as noise? How do they isolate the batch effect from other sources of variability? Is this increase in variance due to the noise, or are they referring to a different kind of variance (e.g., variance in model predictions)? The methodological choices stemming from this vague understanding may not be well-justified, and the results may be susceptible to biases or misinterpretations.
    - mediocre model is not a technical term and not obviously reflective of the performance metrics
    - there is not an increase in variance, but an increase in error relative to a non-existent ground truth
    - changing the continuous expression data to binary data is not a "novel approach" and doesn't necessarily retain information
    - the authors do not provide a rationale for why they chose to use the median CPM as the threshold for binarization
    - data binarization whitens the true covariance among precdictors and so a penalized regression model will not behave as expected. Instead, the authors may as well group every "cluster" of "highly expressed" genes together and use a single indicator variable for each cluster. This would be a more parsimonious model and may not require the use of a penalized regression model.

[^1]: Horvath S, Haghani A, Zoller JA et al. (2022). Epigenetic clock and methylation studies in marsupials: opossums, Tasmanian devils, kangaroos, and wallabies. See `Supplementary file2`. [[paper](https://doi.org/10.1007/s11357-022-00569-5)].
[^2]: Haghani A et al. (2023). DNA methylation networks underlying mammalian traits. [[paper](https://doi.org/10.1126/science.abq5693)].
[^3]: Lu AT, Fei Z et al. (2023). Universal DNA methylation age across mammalian tissues.
[^4]: `shorvath/MammalianMethylationConsortium`. [[issue](https://github.com/shorvath/MammalianMethylationConsortium/issues/2#issuecomment-1205801443)].
[^5]: Horvath S and Raj K (2018). DNA methylation-based biomarkers and the epigenetic clock theory of ageing. [[paper](https://www.nature.com/articles/s41576-018-0004-3)]
[^6]: Horvath S (2013). DNA methylation age of human tissues and cell types. [[paper](https://doi.org/10.1186/gb-2013-14-10-r115)].
[^7]: Meyer DH and Schumacher B (2021). BiT age: A transcriptome-based aging clock near the theoretical limit of accuracy. [[paper](https://doi.org/10.1101/2021.11.01.466051)].
