import modules.database.user

DRIVER = modules.database.user.Driver
DRIVER.BASE.metadata.create_all(DRIVER.engine)