import requests
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
  random_poem = None
  try:
    response = requests.get('https://poetrydb.org/random/1')

    if response.status_code == 200:
      poetry_data = response.json()[0]

      # Filter for poems with 10 lines or less
      if len(poetry_data.get('lines', [])) <= 10:
        random_poem = {
            'title': poetry_data.get('title', 'Unknown Title'),
            'author': poetry_data.get('author', 'Unknown Author'),
            'lines': poetry_data.get('lines', ['No lines available'])
        }
      else:
        # If the poem is too long, try again
        return index()  # Recursively call the function to get a new poem

  except Exception as e:
    # You can log this error if you want to track issues
    pass

  return render_template('index.html', random_poem=random_poem)