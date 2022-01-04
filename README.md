# streamlit_link_extractor

An app to extract links from a webpage

Using wget to download all the links

```
wget -i file_list.txt
```

# Availability
The app is available on Heroku and Streamlit Share

- **heroku** https://streamlit-file-extractor.herokuapp.com/
- **streamlit share** https://share.streamlit.io/lgloege/streamlit-link-extractor/main/app.py

# Development and deployment
Initialize git
```
git init
```

Create app on Heroku
```
heroku create appName
```

Push changes to Heroku
```
git push heroku main
```

Push changes to GitHub (Streamlit Share reads directly from GitHub)
```
git push -u origin main
```

Rollback Heroku release
```
heroku releases
heroku rollback v2 # or which version you want
```




 
