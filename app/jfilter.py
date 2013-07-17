from app import app

def datetimeformat(value, format='%B %dth, %Y'):
    return value.strftime(format)

app.jinja_env.filters['datetimeformat'] = datetimeformat
