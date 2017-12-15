from redash import create_app, myscheduler

app = create_app()

# Starting flask apscheuler
# Bad idea to start scheduler here because flask development runserver
# does not use this file. So it scheduler will not start for dev
# server. will have to think about it and override a common function
# which we use to start both dev and production server.
myscheduler.start()
