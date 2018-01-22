# CROSBI tool

Tool used for uploading articles to CROSBI database.

## Getting Started

### Prerequisites

```
brew install geckodriver
git clone https://github.com/BenjaminMesic/CROSBItool.git
pip install -r requirements.txt 
```

## Running the code

### Getting the list of articles
1. Go to http://inspirehep.net
2. Get the list of articles by using following command (NOTE: change 2017-> year of interest)
``` find a brigljevic and cn cms and date 2017->2017 and ps p ```
3. Save the output to list_of_papers.bib
4. _1_prepare_input.py takes list_of_papers.bib as input and gives you json file with all the informations ready for uploading to CROSBI, additionaly all articles are downloaded as pdf from arxiv and stored in pdf directory. 
``` python _1_prepare_input.py ```

### Uploading to CROSBI
1. Set your username and password in _2_upload_files.py
2. python _2_upload_files.py

