library(readr)
library(lme4)
library(lmerTest)

# read in data from 2-way ANOVA with between-subject factors
df_2way <- read_csv("df_2way.csv")
# fit linear model and get parameter estimates
my_model_fit <- lm(my_value ~ group * language, df_2way)
# display results of linear regression
summary(my_model_fit)
# display anova table
anova(my_model_fit)
# access underlying model
model_matrix = model.matrix(my_model_fit)
# inspect GLM
image(t(model_matrix))
# to change coding scheme
#model_fit <- lm(my_value ~ group * condition, df, contrasts = list(group = "contr.sum", condition = "contr.sum"))

# read in data from 2-way ANOVA with between-subject and within-subject factors
df_full <- read_csv("df_full.csv")
# get parameter estimates from a linear regression with random effects
my_model_fit <- lmer(my_value ~ group * language * task * condition + (1|sub_id), df_full)
# display results of linear regression
summary(my_model_fit)
# main and interaction effects
anova(my_model_fit)
# random effects
rand(my_model_fit)
# access underlying model for fixed effects
my_glm_fe = model.matrix(my_model_fit)
# access underlying model for random effects
my_glm_re = getME(my_model_fit, "Zt")
# inspect matrices
image(t(my_glm_fe))
image(t(my_glm_re))
