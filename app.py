from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup
import requests

# Don't change this
matplotlib.use('Agg')
app = Flask(__name__)  # do not change this

# Insert the scraping here
url_get = requests.get('https://www.exchange-rates.org/exchange-rate-history/usd-idr')
soup = BeautifulSoup(url_get.content, "html.parser")
print(soup.prettify()[:500])

# Find your right key here
table = soup.find('table', attrs={'class': 'table table-striped table-hover table-hover-solid-row table-simple history-data'})

if table is not None:
    print(table.prettify()[1:500])
    rows = table.find_all('tr')

    temp = []  # initiating a list

    for row in rows:
        cols = row.find_all('td')
        if len(cols) == 2:
            period = cols[0].text.strip()
            temp.append(period)

    # Change into dataframe
    df = pd.DataFrame(temp, columns=['period'])
    df['period'] = pd.to_datetime(df['period'])
    df['period'] = df['period'].dt.date
    df.set_index('period', inplace=True)  # Set 'period' column as the index
    df.sort_index(ascending=True, inplace=True)  # Sort the dataframe by the index in ascending order
    df.head()
else:
    # Handle case when table is not found
    df = pd.DataFrame()

@app.route("/")
def index():
    if not df.empty:
        card_data = f'{df.index.mean().round(2)}'  # Calculate the mean of the index (period)

        # Generate plot
        ax = df.plot(figsize=(20, 9))  # Plot the dataframe
        
        # Rendering plot
        # Do not change this
        figfile = BytesIO()
        plt.savefig(figfile, format='png', transparent=True)
        figfile.seek(0)
        figdata_png = base64.b64encode(figfile.getvalue()).decode('utf-8')
        plot_result = str(figdata_png)

        # Render to HTML
        return render_template('index.html',
                               card_data=card_data,
                               plot_result=plot_result
                               )
    else:
        return render_template('error.html', error_message="Table not found")

if __name__ == "__main__":
    app.run(debug=True)
