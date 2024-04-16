## Instructions to host locally

The backend and frontend need to be hosted separately. 

### Backend

The backend is a simple Flask app. It was tested with the following dependencies:
```
flask==2.2.5
flask-cors==4.0.0
pytorch==2.1.2+cu121
transformers==4.39.0.dev0
```

Once all the dependencies are satisfied, you can run the backend by running the following command:

```
cd backend
python app.py
```


### Frontend

Go to the frontend directory

```
cd frontend
```


#### Setup
Tested with npm version `10.5.0` and node version `20.12.2`
```
npm install
```

#### Running
```
npm run dev -- --host --port 3333
```

And, the frontend should be available at `http://localhost:3333/`. 

You can replace `localhost` with the IP address of the machine if you want to access it from another device on the same network.