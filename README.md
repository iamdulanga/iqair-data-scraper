# AQI File Generation & Download Web App

This project is a web application that allows users to view and download air quality index (AQI) files (maps and charts) generated from a scheduled task. The files are stored in a GitHub repository and can be downloaded directly from the web interface.

## Features
- **Automated File Generation**: AQI files for Sri Lanka (charts and maps) are automatically generated and stored in a GitHub repository daily.
- **File Listing**: The app dynamically fetches and lists files stored in two folders on GitHub: `maps` and `charts`.
- **File Selection**: Users can select files they wish to download using checkboxes.
- **File Download**: Users can download selected files directly from the GitHub repository with a single click.

## Folder Structure

- **maps/**: Contains generated map files in HTML format for AQI data visualization.
- **charts/**: Contains generated chart files in Excel format containing AQI data for all cities and most polluted cities in Sri Lanka.

## Technologies Used

- **Python**: For generating AQI data, maps, and charts.
- **JavaScript**: For handling client-side interactions (file listing and downloading).
- **GitHub API**: To list files from the GitHub repository.
- **Vercel / Netlify**: To host the web app.

## Setup & Installation

1. **Clone the Repository**

   Clone the repository to your local machine:

   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   ```

2. **Setup Python Environment**

   - Install the required Python libraries by running the following command:

   ```bash
   pip install -r requirements.txt
   ```

   The dependencies include:
   - `requests`
   - `beautifulsoup4`
   - `pandas`
   - `folium`
   - `geopy`
   - `openpyxl`

3. **Set Up GitHub Actions**

   - The repository includes a GitHub Action defined in `.github/workflows/aqi_generator.yml` that runs daily at 12:00 PM to scrape the latest AQI data and generate the required files (maps and charts).
   - The generated files are stored in two folders (`maps` and `charts`) in the GitHub repository.

4. **Deploy the Web App**

   - You can deploy the web app to either **Vercel** or **Netlify**. Both services provide an easy way to deploy static sites by connecting your GitHub repository.
   
   - **For Vercel**:
     - Sign up for a Vercel account if you don't have one.
     - Connect your GitHub repository to Vercel.
     - Deploy the site by selecting the project from your dashboard.

   - **For Netlify**:
     - Sign up for a Netlify account.
     - Connect your GitHub repository to Netlify.
     - Deploy the site by selecting the project from your dashboard.

5. **Web App Functionality**

   - The web app automatically displays a list of files (charts and maps) stored in your GitHub repository.
   - Users can view the file names, select the files using checkboxes, and download the selected files by clicking the "Download Selected Files" button.

## How It Works

### Automated File Generation (GitHub Actions)

1. **Scheduled Task**: A GitHub Action runs every day at 12:00 PM to fetch the latest AQI data for Sri Lanka from the IQAir website.
2. **File Creation**:
   - **Charts**: The AQI data is saved in Excel files with two sheets: "All Cities" and "Most Polluted Cities."
   - **Maps**: A map showing the locations of the most polluted cities in Sri Lanka is generated and saved as an HTML file.
3. **File Upload**: The generated files are automatically uploaded to the `maps` and `charts` folders in the GitHub repository.

### Web App

1. The **index.html** page loads when accessed.
2. **Fetching Files**: The app uses the GitHub API to fetch files from the `maps` and `charts` folders in your GitHub repository.
3. **Displaying Files**: The app displays the files as checkboxes under "Maps" and "Charts" sections.
4. **Downloading Files**: Users can select files using the checkboxes and download them directly by clicking the "Download Selected Files" button.

### Example of GitHub API File List

The files in your repository's `maps` and `charts` folders are fetched via the GitHub API. For each file, the `download_url` is used to generate a direct download link.

## GitHub Repository Setup

### GitHub API Permissions

The app fetches files from the GitHub repository using the GitHub API. To ensure the app has access to the repository, make sure:

- The repository is **public** (or private with appropriate API access tokens configured).
  
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

### Notes for Developers

- **Future Enhancements**:
  - Consider adding features like file preview (for charts), real-time updates, or filtering files by date or name.
  - You could also extend the GitHub Action to send email notifications once new files are generated.
  
- **Security**:
  - If the repository is private, use GitHub API tokens with restricted access instead of public access.

---

## How the Map Works

- 📍 Cities with highest AQI in each province are marked on Sri Lanka.
- 🎨 Color-coded AQI levels:

- 🟢 Green (0-50) → Good
- 🟡 Yellow (51-100) → Moderate
- 🟠 Orange (101-150) → Unhealthy for Sensitive Groups
- 🔴 Red (151-200) → Unhealthy
- 🟣 Purple (201-300) → Very Unhealthy
- 🟤 Maroon (301+) → Hazardous
