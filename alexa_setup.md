Setup: Alexa Skill
==================

* Log into [Alexa Developer Console](https://developer.amazon.com/edw/home.html#/)
* Click "Alexa Skills Kit"
* Add a new skill
* Tab "Skill Information"
* Name: Smart Camera
* Invocation Name: smart camera
* Click "Next"
* Tab "Interaction Model"
* Intent Schema: [Download here, then paste into field](https://raw.githubusercontent.com/ikk0/smartcam/master/alexa/intent_schema.json)
* Click "Add Slot Type", name it "LIST_OF_NAMES" and paste the contents of the following [name file](https://raw.githubusercontent.com/ikk0/smartcam/master/alexa/list_of_names.txt) into the list. 
* Sample Utterances: [Download here, then paste into field](https://github.com/ikk0/smartcam/blob/master/alexa/sample_utterances.txt)
* Click "Next"
* Tab "Configuration"
