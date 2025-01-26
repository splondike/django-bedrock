from procrastinate.contrib.django import app


@app.task
def background_task(msg):
    print("Task run: " + msg)
