# cv_vac_match
This code gives the cosine similarity between 2 docx files in the browser using flask, dash, docker.

Second commit: Added feature to display the most important sentences of the two files that are uploaded.

Run without docker:
To run the app, download or clone this to a local repository.
Create an environment (using Conda for example).
Open up your terminal, navigate to the project.
Enter: set FLASK_APP=app.py and hit enter (this creates an environment path)
Then enter: flask run

browse to http://127.0.0.1:5000


Run with docker:
docker build --tag=cv_vac_match .  (Don't forget this dot at the end, this means 'all files').
docker run -p 8080:8080 cv_vac_match:latest

Your app will run on http://localhost:5000
