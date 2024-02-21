path:
.: run main.py to perform all functions of kernel.py, results will show in console and charts will be printed to ./Result. (some of the kernel functions have not been connected to front end yet, so we leave a main.py show all functions in kernal.py)
./nlp: Training code and data of NLP model.
./Result: charts.
./models: LSTM model.
./IQSRS: run manage.py to start the server. (But there may be some problem when loading pages and connect to database. First, I write absolute path to cite some elements, and if you want to connect to your local database, you need to change the DATABASES varible in ./IQSRS/IQSRS/settings.py) 
./IQSRS/IQSRS: modify settings.py to connect to your database. urls.py saves relationships between urls and functions in ./IQSRS/app01/views
./IQSRS/app01: kernal.py a same copy to the kernal.py in '.'. models.py saves the configuration of the database. 
./IQSRS/app01/templates: save all html files.
./IQSRS/app01/views: save all django backend codes.
./IQSRS/app01/utils: save ModelForm class.
./IQSRS/app01/middleware: save middleware functions as a template.
./IQSRS/models: LSTM model for website.

There are a folder called venv which saves third party libraries, but it's 1.7GB and I cannot upload it. I think if you want, you can download it using pip3.