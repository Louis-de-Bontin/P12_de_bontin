# P12_de_bontin
12th project of my formation OpenClassrooms


### Installing Django
- Create a new folder `mkdir my_folder`
- Enter your new folder `cd my_folder`
- Clone the repository `git clone https://github.com/likhardcore/P12_de_bontin.git`
- Enter the folder `cd P12_de_bontin`
- Create a virtual environement `python3 -m venv env`
- Install the dependencies `pip install -r requirements.txt`
- Enter the app `cd crm_epic_event`
### Setting up the database
- Install PostGreSQL
- Create a new database named `crm_epic_events`
- In the file `crm_epic_event/settings.py`, replace the user and the password by you own.
- Make the migrations `python3 anage.py makemigrations` then `python3 manage.py migrate`

### Setting up the server
- Launch the server `python3 manage.py runserver`

### Postman
- For the detail decomentation, follow this link : `https://documenter.getpostman.com/view/17381028/UVkgyeid`


### Notable points
- Signing a `contract` creates an `event`
- A `contract` written by a `seller` is automaticly linked to him
- Deleting a `contract` deletes the associated `event`
- Only the `MANAGER` can acces the `/users/` endpoint and his extentions
- Deleting a `user`, or a `customer` leave the field in `contract` or `customer` empty
- Creating a `user` with the `role` field empty set him as `MANAGER`
- Differents params can be used on `/customers/`, `/contracts/` or `/events/` to filter the results
- Creating a `contract` changes the status of a `customer` if he was not `existing`
- Only `SELLERS` can sign a contract and therefore create an `event`
- A `MANAGER` isn't related ton any other instance
- A `SELLER` is in charge of `customers` and appears on `contracts`
- A `SUPPORT` appears on contract. He is in charge of `events`, but since he is already in the contract, putting this information in the `event` table would have been redoundant
- Only a `SUPPORT` can update an event
- Once an `event` is finished, it is not updatable anymore