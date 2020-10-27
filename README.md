# Youtube-content-analysis

Input : YouTube link of Product Making Videos and Product Review Videos

Process:
1.Extracting all YouTube videos threw link 
2.Converting all Video files to audio files in required format 
3.1 Creating a Custom speech to text Model using Coginitive services
3.1.1 Create a resource group in azure for speech services
3.1.2 Extract hidden service key and hidden subcription key 
3.1.3 Make a training data of audio (chunk file) in specified formats.
Formats:
1.each audio file must be chunked into minute wav file
2.each chunk file's sampling rate should 16,000Hz
3.each chunk file's channel should be mono
4.each chunk file's must be encoded with bit size of 16
3.1.4 Training Data passed to model for Model Training
3.1.5 In model training pretrained speech model will be as a base line model,top of that trained model will be working
3.1.6 Inspect Word Error Rate
3.1.7 Test model with sample audio files
3.1.8 Model which has good accuracy are deployed
3.1.9 After deploying endpoint id will generated automatically
4. Subcription key,serivce key and endpoint id paased on to continous function of speech recogonisation
5. Text output passed to custom spacy model for extracting out ingredients entiites 
6. Output updated in Databse and PowerBi dashboard
