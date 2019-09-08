# Decision tree for Hypothesis tests
Below is an overview of test that can be used to compare the average of a continuous dependent variable based on categorical independent variables.

### one factor, one level
* __independent measurements__
    * _parametric test_
        * t-test
        * python: scipy.stats.ttest_ind
        * R: t.test
    * _non-parametric test_
        * Mann Whitney U test
        * python: scipy.stats.mannwhitneyu
        * R: wilcox.test (Mann-Whitney-Wilcoxon Test)
* __dependent measurements__
    * _parametric test_
        * paired t-test
        * one-sample t-test on the differences
        * equivalent: GLM with random effects for each subject
        * python: scipy.stats.ttest_rel
        * R: t.test(paired=TRUE)
    * _non-parametric test_
        * Wilcoxon sum-rank test
        * python: scipy.stats.wilcoxon
        * R: wilcox.test(paired=TRUE) (Wilcoxon Signed-Rank Test)

### one factor, multiple levels
* __independent measurements__
    * _parametric test_
        * one-way ANOVA
        * python: statsmodels.formula.api.ols
        * python: scipy.stats.f_oneway
        * R: lm
    * _non-parametric test_
        * Kruskal-Wallis test
        * python: scipy.stats.kruskal
        * R: kruskal.test
* __dependent measurements__
    * _parametric test_
        * repeated-measures one-way ANOVA (with random effects)
        * python: statsmodels.stats.anova.AnovaRM  
          (only implemented for fully balanced within-subject designs)
        * R: lm
    * _non-parametric test_
        * Friedman test
        * python: scipy.stats.friedmanchisquare
        * R: friedman.test

### two factors, multiple levels
* __independent measurements__
    * _parametric test_
        * two-way ANOVA
        * statsmodels.formula.api.ols
        * R: lme4 (lmer)
        * R: aov (not recommended)
    * _non-parametric test_
        * Scheirer-Ray-Hare test
        * Python and R: not available
        * build a general linear mixed model by hand and do bootstrapping
* __dependent measurements__
    * _parametric test_
        * repeated measures two-way ANOVA
        * python: statsmodels.stats.anova import AnovaRM  
        (only implemented for fully balanced within-subject designs)
        * python: statsmodels.formula.api.mixedlm  
        (only implemented for fully balanced within-subject designs)
        * statsmodels does not support crossed random effects (i.e. only one group)
        * R: lme4 (lmer)
    * _non-parametric test_
        * build a general linear mixed model by hand and do bootstrapping

### more than two factors
* __independent measurements__
    * _parametric test_
        * n-way ANOVA
        * python and R, see above for two factors
        * non-parametric test
    * _non-parametric test_
        * build a general linear mixed model by hand and do bootstrapping
* __dependent measurements__
    * _parametric test_
        * n-way repeated measures ANOVA
        * python and R, see above for two factors
    * _non-parametric test_
        * python and R: not implemented
        * build a general linear mixed model by hand and do bootstrapping
