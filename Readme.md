# **Job Scraper**
**[Live Demo: Job Scraping App](https://jobscraping.streamlit.app/)**

If the demo link does not work, it means I am upgrading the project.
---

## **Description**
### Job Scraper with Streamlit Visualization

This project is a job scraper that extracts job listings from various websites and visualizes the data using **Streamlit**.

The scraper fetches:
- **Job Titles**
- **Company Names**
- **Job Locations**
- **Job Descriptions**
- **Application Links**

---

## **Set Up Configuration**

1. **Open the Configuration File**
    - Locate and open the `config` file in the repository.

2. **Add Required Details**
    - Insert your **Gemini API key**.
    - Add the **URL of the job site** you want to scrape.

   Example configuration:
   ```yaml
   api_key: YOUR_GEMINI_API_KEY
   target_url: https://example.com/jobs
   ```  

---

## **Install Dependencies**

Ensure you have **Python** installed, then run:
```bash
pip install -r requirements.txt
```  

---

## **Run the Application**

Start the app using the following command:
```bash
streamlit run JobScrapy.py
```  

---

## **Access the Application**

After running the above command, open your browser and navigate to the URL provided by Streamlit, such as:
```  
http://localhost:8501
```  

---

## **Live Application**
**Try it now**: [Job Scraping App](https://jobscraping.streamlit.app/)

---

## **Technologies Used**

- **Python**: The backbone of the scraping logic
- **Streamlit**: For creating the interactive web application
- **BeautifulSoup** and **requests**: For efficient web scraping
- **JSON**: For handling and formatting the data extracted during web scraping

---

## **Contributing**
We welcome contributions! Feel free to fork the repository, submit issues, or suggest improvements. 😊  
