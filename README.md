# P12_de_bontin
12th project of my formation OpenClassrooms


### Installing Django
- Create a new folder `mkdir my_folder`
- Enter your new folder `cd my_folder`
- Clone the repository `git clone https://github.com/likhardcore/P12_de_bontin.git`
- Enter the folder `cd P12_de_bontin`
- Create a virtual environement `python3 -m venv env`
- Activate the virtual environement `source env/bin/activate`
- Install the dependencies `pip install -r requirements.txt`
- Enter the app `cd crm_epic_event`
### Setting up the database
- Install PostGreSQL
- Install PGAdmin
- In the UX of PGAdmin, create a new database named `crm_epic_events`
- In the file `crm_epic_event/settings.py`, in the `DATABASE` dictionary, replace `USER` and `PASSWORD` by you own
- Make the migrations `python3 manage.py makemigrations` then `python3 manage.py migrate`

### Setting up the server
- Create a `superuser` to be able to use the API `python3 manage.py createsuperuser`
- Follow the steps
- Launch the server `python3 manage.py runserver`
- You can now interact with the endpoints via Postman, or any similar software

### Postman
- For the detailed documentation, click [here](https://documenter.getpostman.com/view/17381028/UVkgyeid)
- Don't forget to login with the `superuser` you created earlier to start create `MANAGER`, `SELLER` and `SUPPORT` and try the differents permissions and instances available as described in the Postman doc


### Notable points
- Signing a `contract` creates an `event`
- A `contract` written by a `seller` is automaticly linked to him
- Deleting a `contract` deletes the associated `event`
- Only the `MANAGER` can acces the `/users/` endpoint and his extentions
- Deleting a `user`, or a `customer` leaves the field in `contract` or `customer` empty
- Creating a `user` with the `role` field empty set him as `MANAGER`
- Some params can be added on `/customers/`, `/contracts/` or `/events/` when getting a list to filter the results
- Creating a `contract` changes the status of a `customer` if he was not `existing`
- Only a `SELLER` can sign a contract and therefore create an `event`
- A `MANAGER` isn't related ton any other instance
- A `SELLER` is in charge of `customers` and appears on `contracts`
- A `SUPPORT` appears on `contracts`. He is in charge of `events`, but since he is already in the contract, putting this information in the `event` table would have been redoundant
- Only a `SUPPORT` can update an event
- Once an `event` is finished, it is not updatable anymore