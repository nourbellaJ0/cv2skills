# CV2Skills

CV2Skills is an intelligent CV analysis platform that uses artificial intelligence to extract, analyze, and organize professional skills and experiences from resume documents. Built with Flask and powered by Groq AI, it provides comprehensive CV parsing and skill extraction capabilities.

## Overview

CV2Skills automates the analysis of CVs in multiple formats (PDF, DOCX, DOC, TXT) to:
- Extract technical and soft skills with categorization
- Identify key professional experiences
- Parse contact and professional information
- Store and manage CV data in MongoDB
- Provide intelligent insights using AI-powered analysis

## Features

- Multi-format document support (PDF, DOCX, DOC, TXT)
- Intelligent text extraction and cleaning
- AI-powered skills and experience analysis using Groq API
- MongoDB integration for document storage and retrieval
- RESTful API for seamless integration
- Web-based user interface for easy document upload
- Real-time CV analysis and processing
- Structured data extraction with predefined schemas

## Technology Stack

- Backend Framework: Flask
- Database: MongoDB Atlas
- AI Engine: Groq API
- Document Processing: PyPDF2, docx2txt, Apryse SDK
- Server: Gunicorn
- Frontend: HTML5, CSS, JavaScript
- Language: Python 3.x

## Project Structure

```
cv2skills/
├── app.py                   # Main Flask application
├── Dockerfile               # Docker configuration
├── fly.toml                 # Fly.io deployment config
├── requirements.txt         # Python dependencies
├── template.docx           # Document template
├── exemple.json            # Example data structure
├── PDFNetC6/               # Apryse PDF SDK
├── static/
│   ├── index.html          # Web interface
│   ├── logo.png            # Application logo
│   └── wallpaper.jpg       # Background image
├── utils/
│   ├── file_detector.py    # File format detection
│   └── extractor.py        # Text extraction logic
├── build/                  # Build artifacts
└── dist/                   # Distribution files
```

## Installation

### Prerequisites

- Python 3.8 or higher
- MongoDB Atlas account (or local MongoDB)
- Groq API key
- Git

### Local Setup

1. Clone the repository
   ```bash
   git clone https://github.com/nourbellaJ0/cv2skills.git
   cd cv2skills
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Create .env file with your credentials
   ```
   GROQ_API_KEY=your_groq_api_key
   MONGODB_URI=your_mongodb_connection_string
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

5. Run the application
   ```bash
   python app.py
   ```

6. Open your browser and navigate to
   ```
   http://localhost:5000
   ```

### Docker Setup

1. Build the Docker image
   ```bash
   docker build -t cv2skills .
   ```

2. Run the container
   ```bash
   docker run -p 5000:5000 --env-file .env cv2skills
   ```

3. Access the application at http://localhost:5000

### Fly.io Deployment

The project includes Fly.io configuration. Deploy with:
```bash
flyctl deploy
```

## API Endpoints

### POST /upload
Upload and analyze a CV document

Request:
```json
{
  "file": "multipart/form-data"
}
```

Response:
```json
{
  "document_id": "string",
  "skills": [],
  "experiences": [],
  "contact_info": {},
  "analysis": {}
}
```

### GET /document/<id>
Retrieve previously analyzed CV data

Response:
```json
{
  "_id": "string",
  "filename": "string",
  "extracted_data": {},
  "upload_date": "datetime",
  "status": "string"
}
```

## Configuration

### Environment Variables

- GROQ_API_KEY: API key for Groq AI service
- MONGODB_URI: Connection string for MongoDB Atlas
- FLASK_ENV: Development or production environment
- FLASK_DEBUG: Enable debug mode

### Supported Document Formats

- PDF (.pdf)
- Microsoft Word (.docx, .doc)
- Plain Text (.txt)

## Usage

1. Open the web interface at http://localhost:5000
2. Click the upload button
3. Select your CV file (PDF, DOCX, DOC, or TXT)
4. Wait for processing to complete
5. View extracted skills, experiences, and professional information
6. Data is automatically saved to MongoDB

## Data Structure

The application extracts and organizes CV data into the following categories:
- Technical Skills (by category)
- Recent Key Experiences
- Professional Work History
- Education
- Certifications
- Languages
- Contact Information

## Dependencies

All required Python packages are listed in requirements.txt:
- Flask: Web framework
- PyPDF2: PDF processing
- docx2txt: DOCX document parsing
- apryse-sdk: Advanced PDF handling
- pymongo: MongoDB integration
- groq: AI API client
- python-dotenv: Environment variable management
- flask-cors: CORS support

## Development

### File Detection
The application automatically detects file types using MIME type analysis and file extension validation in the utils/file_detector.py module.

### Text Extraction
Multiple extraction methods are employed depending on file type:
- PDF: Apryse SDK and PyPDF2
- DOCX: docx2txt library
- TXT: Direct file reading
- DOC: Apryse conversion to PDF then extraction

### AI Analysis
The Groq API is used to intelligently parse extracted text and categorize skills and experiences according to predefined schemas.

## Deployment

The application is configured for deployment on Fly.io. The fly.toml file contains deployment settings.

For Docker deployment on other platforms, use the provided Dockerfile.

## Database

MongoDB Atlas is used for persistent storage of:
- Uploaded CV documents
- Extracted and analyzed data
- User sessions and preferences

## Performance Notes

Document processing time depends on:
- File size and complexity
- API response time from Groq
- MongoDB operations

Large PDFs (100+ pages) may take 30-60 seconds to process completely.

## Troubleshooting

### Connection Issues

If MongoDB connection fails:
1. Check MONGODB_URI in .env file
2. Verify MongoDB Atlas IP whitelist settings
3. Ensure network connectivity

### Groq API Errors

If CV analysis fails:
1. Verify GROQ_API_KEY is set correctly
2. Check Groq API rate limits
3. Review API response logs

### File Upload Issues

If file upload fails:
1. Verify file is in supported format
2. Check file size (should be under 50MB)
3. Ensure proper MIME type detection

## Future Enhancements

- Multi-language CV support
- Advanced skill matching and recommendations
- CV scoring and ranking system
- Duplicate CV detection
- Batch CV processing
- Advanced analytics dashboard

## Contributing

1. Fork the repository
2. Create a feature branch (git checkout -b feature/YourFeature)
3. Commit changes (git commit -m 'Add YourFeature')
4. Push to branch (git push origin feature/YourFeature)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Author

nourbellaJ0
- GitHub: https://github.com/nourbellaJ0
- Email: nour.bellaaj@esprit.tn

## Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.

## Acknowledgments

- Groq for AI-powered analysis capabilities
- MongoDB Atlas for reliable document storage
- Flask and Python communities
- Apryse SDK for advanced PDF processing

---

Note: Ensure all environment variables are properly configured before deploying to production. Always keep API keys and database credentials secure.