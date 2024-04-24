## Instructions to host locally

The backend and frontend need to be hosted separately. First, create a `config.yml` file in the root directory following the template in `config_demo.yml`.

### Backend

The backend is a simple Flask app. It was tested with the following dependencies:
```
flask==2.2.5
flask-cors==4.0.0
pytorch==2.1.2+cu121
transformers==4.39.0.dev0
dataclasses-json==0.6.4
baukit==0.0.1
```

Once all the dependencies are satisfied, you can run the backend by running the following command:

```
cd backend
python app.py
```

We tested the backend on Ubuntu 20.04.3 LTS with a A6000 GPU and CUDA 12.1. But a CPU should be able to easily handle a smaller model like `gpt2` or `gpt2-medium`.


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

If you changed the `config.yml`, you will want to chage the following lines in [`frontend/src/routes/InputPrompt.svelte`](frontend/src/routes/InputPrompt.svelte):

```javascript
const backendUrl = "localhost"; 
const backendPort = "5050"; 
```

Then run the following command to start the frontend:
```
npm run dev -- --host --port 3333
```

And, the frontend should be available at `http://localhost:3333/`. 

You can replace `localhost` with the IP address of the machine if you want to access it from another device on the same network.