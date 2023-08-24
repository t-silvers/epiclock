# Statistical models for epigenetic clocks

## Transformations to get relative age

- https://www.nature.com/articles/s43587-023-00462-6#Sec25
- "Construction We used a piecewise transformation, parameterized by Age of Sexual Maturity (A). The transformation is F(x), given by ..."

## Notation

| Symbol             | Name                     | Description                           |
|--------------------|--------------------------| --------------------------------------|
| $\mathbf{X}$              | Methylation data  | Sample $\times$ probe matrix of beta values
| $\mathbf{y}$              | Age               | Age, in linear time                   |
| $\tilde{\mathbf{y}}$      | Phenotypic age    | Modified age measure based on health phenotypes|
| $\hat{\mathbf{y}}$        | Epigenetic age    | Clock-predicted age based on methylome|
| $\hat{\beta}$                   | CpG weights       | Estimated contribution of a single CpG to age   |

## Clock models

The core methylation clocks from Horvath, Hannum, and PhenoAge (sometimes referred to as Levine's clock) use the same objective function $F$,

$$
F(\mathbf{X},\mathbf{y}) = \underbrace{l(\hat{\mathbf{y}} \text{ vs. } \mathbf{y})}_{\text{age prediction error}} + \underbrace{P_{\Omega}(\hat{\beta})}_{\text{select subset of CpGs}},
$$

where $l$ is the loss function, $\hat{\mathbf{y}}=\hat{r}(\mathbf{X})$ is the predicted epigenetic age (here, $\hat{r}(\mathbf{X})=\mathbf{X}\hat{\beta}$), and $P_{\Omega}(\hat{\beta})$ is the sparsity penalty on the coefficients per additional parameters $\Omega$. The sparsity penalty is meant to perform subset selection and shrink CpG weights.

> ⚠️ **_Technical Note:_**
These models all use a least-squares loss, $l(\hat{r}(\mathbf{X}), \mathbf{y}) = \sum_{i=1}^n \hat{\epsilon}_i^2$, for $n$ observations. where $\hat{\epsilon} = \mathbf{y} - \mathbf{X}\hat{\beta}$. The authors fit an intercept term, which we drop with the assumption that $\mathbf{X}$ contains a column of $1$ s. These models all also use an elastic net penalty,$ P_{\lambda, \alpha}(\hat{\beta}) = \lambda\left(\alpha \|\hat{\beta}\|_1 + \frac{1-\alpha}{2} \|\hat{\beta}\|_2^2\right).$

The differences among these models are in the preprocessing steps and training data,

$$
\begin{align*}
    F(\mathbf{X}_\text{MT}, \mathbf{y}) &\quad\text{[Horvath]} \\
    F(\mathbf{X}_\text{blood}, \mathbf{y}) &\quad\text{[Hannum]} \\
    F(\mathbf{X}_\text{InCHIANTI}, \tilde{\mathbf{y}}) &\quad\text{[PhenoAge]},
\end{align*}
$$

which leads to models with different numbers of non-zero predictors, but similar results. These models use the penalized coefficients as CpG weights for prediction.

They estimate CpG weights $\hat{\beta}$ by minimizing the objective function, $\min_{\beta} F(\mathbf{X},\mathbf{y})$, using coordinate descent. They implement their optimization using the R software `glmnet`. Assuming that input data `X` and `y` match their clocks and are suitably preprocessed, the entire code base for these epigenetic clocks can be represented by a few lines of code

```R
library(glmnet)

# Make clock
mod_cv <- cv.glmnet(X, y, alpha = 0.5, nfolds = 10)
mod <- glmnet(X, y, alpha = 0.5, lambda = mod_cv$lambda.1se)

# Run clock
y_hat <- predict(mod, s = mod_cv$lambda, newx = X)
```

as described here [^1], for instance.

[^1]: Horvath, S., Haghani, A., Zoller, J.A. et al. Epigenetic clock and methylation studies in marsupials: opossums, Tasmanian devils, kangaroos, and wallabies. GeroScience 44, 1825–1845 (2022). See `Supplementary file2`. [[link](https://doi.org/10.1007/s11357-022-00569-5)].
