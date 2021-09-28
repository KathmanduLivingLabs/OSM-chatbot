
# OSM Chatbot
A chatbot that answers OpenStreetMap related queries. It is powered by Rasa Open Source.


## Acknowledgements
[RASA](https://rasa.com/)

[Missing Maps](https://www.missingmaps.org/)

[Tag Finder](https://tagfinder.herokuapp.com/)

## Contributing

Contributions are always welcome!

To contribute to this project you can add/update Natural Language Understanding Data and bot responses.

Clone this project
```bash
git clone https://github.com/Aadesh-Baral/OSM-chatbot.git
```
Go to the project directory
```bash
cd OSM-chatbot
```
Rasa Open Source uses YAML as a unified and extendable way to manage all training data, including NLU data, stories and rules.
You can split the training data over any number of YAML files, and each file can contain any combination of NLU(Natural Language Understanding) data, stories, and rules. The training data parser determines the training data type using top level keys.

To add training data you must have to add intent on one of the nlu files inside data folder. For example if i want to add chatbot support for iD editor info:

- Open faq.yml located inside data folder
- Add intent as ```faq/iDeditor_info``` where ```faq``` is our retrieval intent. [What is retreival intent?](https://rasa.com/docs/rasa/glossary#retrieval-intent)
- Add at least 5 examples for this intent. This is where our model learns to predict user intent (e.g. What is iDeditor?)
- Add response for this intent on ```responses.yml``` present inside ```/data/resposnes``` and on ```domain.yml``` file.


## Run Locally

Clone the project

```bash
  git clone https://github.com/Aadesh-Baral/OSM-chatbot.git
```

Go to the project directory

```bash
  cd OSM-chatbot
```
Create virtual environment
```bash
    python3 -m venv 
```
Activate environment
```bash
    source venv/bin/activate
```
Install dependencies

```bash
    pip install -r requirements.txt
```
To train model
```bash
    rasa train
```
To run bot on command line 
```bash
    rasa shell
```

Custom action server are required to fetch dynamic response from api's or web scrapping. We have used custom actions to fetch user statistics and tag information in this project.

To run custom action server
```bash
  rasa run actions
```
To run on interactive mode on web browser:

- Make sure you have install Rasa X on your environment,
Then run
```bash
rasa x
```

  
