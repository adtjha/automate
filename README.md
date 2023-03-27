# automate

### Brief
Here's a chat with ChatGPT summarising this project.


## Steps to Run.

### Setup Visual_ChatGPT
1. Clone the visual_chatgpt, into local environment,
2. Install and run visual_chatgpt (set your openai_key as environment variable),
3. Once running, goto page: http://127.0.0.1:7868,
4. type in 'hi', should get a reply,
5. Open console, click on networking tab,
6. click on any one of the '/predict' api requests, find out the payload content,
7. Get the session_hash, we will require that to send api requests directly from the flask server.

### Setup Flask Server
1. If in windows, run this to setup the virtual environment,
```bash
> cd Scripts
> activate.bat
```
2. Once inside the virtual environment, run
```bash
flask run 
```
3. Once the backend is running, goto localhost:5000,
