# Setup Environment
```
sudo -H pip install pipenv
cd watchlist
pipenv install
pipenv install flask
pipenv install python-dotenv
pipenv install flask-sqlalchemy
pipenv install flask-login
```

# Initialize Database
```
pipenv shell
```
Then:
```
flask shell
from app import db
db.create_all()
db.drop_all()   # drop all database
```
OR
```
flask initdb
```
OR
```
flask initdb --drop
```
Finally,
```
exit
```
Save data into database manually:
```
flask forg
```

# Initialize Admin Account
```
pipenv shell
flask admin		# create admin user account
```

# Run
```
pipenv shell    # activate this project
flask run
http://localhost:5000
exit
```

```
python3 -m http.server 8000
localhost:8000/
```

# Reference
``` 
https://zhuanlan.zhihu.com/p/51530577 
```