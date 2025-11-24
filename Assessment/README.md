# Technical Assessment Task

This zip file contains workflow for data acquisition, LLM-based tagging, and regression analysis with Difference-in-differences OLS models on the impact of the number of AI-related papers after launch of GPT-3.

## Getting Started

### Dependencies 

* playwright
* google-genai
* statsmodels

### Executing Code

* requires Google API key in config.py
run extract.py to generate the raw files
run LLMtag.ipynb pointing to the raw file directory with Google API key configured to generate the response files
run analysis.ipynb pointing to the response files to reproduce the analysis