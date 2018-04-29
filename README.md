# CSCI 4502 Project

## Project title:

### Short Term Credit Default
## Team members
- Spencer Hanson
- Benjamin Miller 
- Maxim Moghadam
- William Brickowski

## Description of the project

In this project we take Freddie Mac mortgage data during the peak quarters of the housing bubble, the last two quarters of 2008 and the first two quarters of 2009 to analyze which attributes correlated highly to default rates. The goal of the project is two fold. We aim to come up with an accurate prediction for default rates and also plan to analyze attributes that led to the growth and ultimate implosion of the housing bubble. The knowledge obtained from such analysis will prove useful in several settings. It can be applied in the credit rating sector to come up with more accurate predictions of credit risk. It can also be used to classify particular lending practices and particular attributes of loans that led to the housing crisis of 2008.

## Summary of the question(s) sought and the answers
### Can we develop a way to predict default?
Yes, we used four different models, Logisitic Regression, Gaussian Naive Bayes, Decision Tree and Random Forest.

### What attributes make a loan more likely to default?
- Channel: Where did the loan originate from? Broker, Retail, Correspondent, Unspecified
- Occupancy Status: Denotes whether the mortgage type is owner occupied, second home, or investment property.
- Debt To Income: Ratio of the amount of debt to the income
- Original Loan To Value: Dividing the original mortgage value over the secondary loan mortgage value disclosed by the seller.
- Original Interest Rate: The interest rate of the loan at time of origination

### What geographic regions are more prone to default?
Texas, California, Flordia, Illonis had the highest default rates.

## Application of this knowledge

### Application 1: Assessing risk in giving out a loan 
These methods can be used by credit rating agencies in the financial industry such as Moody’s Investors Services and Standard and Poor's in order to more accurately assess credit risk by quantifying the effects of certain attributes to gain a better measure of risk.

### Application 2: Predicting a market bubble before it happens
This could be used by an economist to look for a bubble in a market. Searching through different attributes in loans, there could be signs that could be useful. Such methods can also be used to analyze the types of loans that are being given out characterized by predicting a number of defaults above a particular threshold.

### Application 3: Large Scale Default Prediction
Once loans are made, the models we formed could be run to predict the rate of default on the set of loans made. That is, we can answer the question: "How many people out of the n I just gave a mortgage to are going to default?" This is the knowledge gained from the analysis, but this knowledge can be used by analysts to calculate a more accurate measure of risk for the company. Following from this, once a new level of risk has been calculated, assuming it is accurate it can be used to predict profit or loss on the set of loans made. Hence this knowledge can be used to maximize expected profit or minimize expected loss by estimating the proportion of people in a set of loans who will default.

### Application 4: Marginal Loan Denial
The methods we developed can be combined with pre-existing credit-score measurements to marginally increase their accuracy. For example, the random forest method had low recall, or true positive rate, but had even lower false negative rate. Because of this, we can use methods such as these to deny loans to a small amount of would-be defaulters, while denying loans only to an even smaller amount of non-defaulters.


## Link to the video demonstration
<a href="30_CreditScore_Part5.mp4"><p>Video</p></a>

## Link to your final project paper
<a href="30_CreditScore_Part4.pdf"><p>Paper</p></a>
