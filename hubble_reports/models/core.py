from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
# To increase the pool size, use kwargs "engine_options=dict(pool_size=<no_of_worker>)"
