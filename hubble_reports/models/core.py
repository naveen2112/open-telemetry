from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy() #Toincrease the pool size use kwargs "engine_options=dict(pool_size=<no_of_worker>)"
