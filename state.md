# Raida Concept - Project State

**Last Updated**: 2025-11-25

## Project Overview

Raida Concept is an AI-powered lesson planning tool that generates structured PDF lesson plans from PowerPoint presentations. The system supports multiple subjects (French, Math) with automatic language adaptation and dynamic content extraction.

---

## ✅ Working Features

### 1. Data Processing & Management

#### PPTX to JSON Conversion
- ✅ Extracts lesson data from PPTX files in `/lessons` directory
- ✅ Parses both short (`FR_N5_P1_SEM1_S3`) and long (`Français_Niv5_Parcour1_Palier3_Séance1`) filename formats
- ✅ Generates structured `lessons.json` with English keys
- ✅ Extracts metadata: subject, level, period, week, session, objective, content
- ✅ Processes 6 lessons currently (3 French, 3 Math)

#### Data Structure
```json
{
  "id": 1,
  "title": "FR N5 P1 SEM1 S3 V2",
  "subject": "français",
  "level": "5",
  "period": "1",
  "week": "1",
  "session": "3",
  "filename": "FR_N5_P1_SEM1_S3_V2.pptx",
  "objective": "...",
  "content": "..."
}
```

### 2. Backend API (Flask)

#### Endpoints
- ✅ `GET /lessons` - Returns all available lessons
- ✅ `POST /generate` - Generates PDF from uploaded PPTX file
- ✅ `POST /generate_from_id/<lesson_id>` - Generates PDF from existing lesson
- ✅ `GET /download_pdf/<filename>` - Downloads generated PDF

#### Features
- ✅ CORS enabled for frontend communication
- ✅ Metadata extraction from filenames
- ✅ PPTX text extraction
- ✅ AI-powered content processing (OpenAI GPT-4o-mini)
- ✅ PDF generation via Playwright

### 3. AI Processing

#### Subject-Specific Prompts
- ✅ **French Lessons**: Extracts content in French with French teaching style
- ✅ **Math Lessons**: Extracts content in Arabic with appropriate terminology

#### Dynamic Lesson Step Extraction
- ✅ Analyzes PPTX content to identify lesson sections
- ✅ Extracts step names, durations, and descriptions
- ✅ Assigns appropriate icons to each step
- ✅ Adapts to different lesson structures automatically

#### Example Output Structure
```json
{
  "subject": "français",
  "level": "5",
  "period": "1",
  "week": "1",
  "session": "3",
  "objective": "Lesson objective...",
  "steps": [
    {
      "name": "Rituel d'ouverture",
      "duration": "10min",
      "icon": "🔁",
      "content": "Activity description..."
    }
  ]
}
```

### 4. PDF Generation

#### Template System
- ✅ **French Template** (`template_french.html`): LTR layout, French labels
- ✅ **Math Template** (`template_math.html`): RTL layout, Arabic labels
- ✅ Automatic template selection based on subject
- ✅ Dynamic rendering of lesson steps
- ✅ Clean, professional design

#### Template Features
- ✅ No Date field
- ✅ No Groupe/Horaire fields
- ✅ Updated labels: Période, Semaine, Séance
- ✅ Dynamic lesson steps with icons and durations
- ✅ Responsive A4 format
- ✅ Print-optimized styling

### 5. Frontend (Next.js + React)

#### Modern UI Design
- ✅ Premium gradient design (Indigo → Purple)
- ✅ Glassmorphism effects
- ✅ Smooth animations and transitions
- ✅ Responsive layout
- ✅ Professional color scheme

#### Multilingual Support
- ✅ **French** and **Arabic** language toggle
- ✅ Complete UI translations
- ✅ RTL layout support for Arabic
- ✅ Persistent language preference (localStorage)

#### Cascading Selection System
- ✅ 5-level hierarchy:
  1. Matière (Subject)
  2. Niveau (Level)
  3. Période (Period)
  4. Semaine (Week)
  5. Séance (Session)
- ✅ Automatic filtering based on selections
- ✅ Disabled states for dependent dropdowns
- ✅ Reset logic when parent selection changes

#### User Experience
- ✅ Error handling with helpful messages
- ✅ Loading states during PDF generation
- ✅ Success indicators
- ✅ Console logging for debugging
- ✅ Selected lesson details display
- ✅ Download functionality

### 6. Development Environment

#### Backend
- ✅ Flask development server running on port 5000
- ✅ Hot reload enabled
- ✅ Environment variables via `.env`
- ✅ OpenAI API integration

#### Frontend
- ✅ Next.js development server running on port 3000
- ✅ Hot reload enabled
- ✅ Tailwind CSS for styling
- ✅ TypeScript for type safety

---

## 🔧 Features Needing Improvement

### 1. Data Processing

#### Objective Extraction
- ⚠️ Currently returns placeholder `"......"`
- 🎯 **Need**: Improve AI extraction of lesson objectives from PPTX content
- 💡 **Suggestion**: Add specific prompts to identify objective sections in slides

#### Content Parsing
- ⚠️ Raw text extraction without structure preservation
- 🎯 **Need**: Better parsing of slide structure (headings, lists, tables)
- 💡 **Suggestion**: Use python-pptx library features to preserve formatting

### 2. AI Processing

#### Consistency
- ⚠️ AI-generated content quality varies
- 🎯 **Need**: More consistent output format and quality
- 💡 **Suggestion**: Add validation layer, retry logic for malformed JSON

#### Language Detection
- ⚠️ Relies on subject name for language selection
- 🎯 **Need**: Automatic language detection from PPTX content
- 💡 **Suggestion**: Analyze content language before processing

#### Step Extraction Accuracy
- ⚠️ May not always identify all lesson steps correctly
- 🎯 **Need**: Improve step identification algorithm
- 💡 **Suggestion**: Add training examples, use few-shot prompting

### 3. PDF Generation

#### Styling
- ⚠️ Basic styling, could be more visually appealing
- 🎯 **Need**: Enhanced visual design with better typography
- 💡 **Suggestion**: Add custom fonts, improved color schemes, better spacing

#### Arabic Font Support
- ⚠️ DejaVu Sans may not render all Arabic characters perfectly
- 🎯 **Need**: Better Arabic font support
- 💡 **Suggestion**: Use Amiri, Cairo, or Tajawal fonts for Arabic

#### Page Breaks
- ⚠️ No intelligent page break handling
- 🎯 **Need**: Prevent content from breaking awkwardly across pages
- 💡 **Suggestion**: Add CSS page-break rules, adjust content sizing

### 4. Frontend

#### Error Handling
- ⚠️ Basic error messages
- 🎯 **Need**: More specific error messages with troubleshooting steps
- 💡 **Suggestion**: Add error codes, detailed error states

#### Loading States
- ⚠️ Simple spinner during PDF generation
- 🎯 **Need**: Progress indicators showing generation stages
- 💡 **Suggestion**: Add step-by-step progress (Analyzing → Generating → Rendering)

#### PDF Preview
- ⚠️ No preview before download
- 🎯 **Need**: In-browser PDF preview
- 💡 **Suggestion**: Embed PDF viewer or show thumbnail

#### Batch Processing
- ⚠️ Can only generate one PDF at a time
- 🎯 **Need**: Bulk PDF generation for multiple lessons
- 💡 **Suggestion**: Add multi-select functionality, queue system

### 5. Data Management

#### Lesson Updates
- ⚠️ No way to update existing lessons without re-running preprocessing
- 🎯 **Need**: CRUD operations for lessons
- 💡 **Suggestion**: Add admin interface for lesson management

#### File Upload
- ⚠️ Manual file placement in `/lessons` directory
- 🎯 **Need**: Web-based file upload interface
- 💡 **Suggestion**: Add drag-and-drop upload in frontend

#### Data Validation
- ⚠️ Limited validation of extracted data
- 🎯 **Need**: Comprehensive validation rules
- 💡 **Suggestion**: Add schema validation, data quality checks

### 6. Performance

#### PDF Generation Speed
- ⚠️ Can be slow for complex lessons (10-30 seconds)
- 🎯 **Need**: Faster generation times
- 💡 **Suggestion**: Cache AI responses, optimize Playwright rendering

#### API Response Times
- ⚠️ No caching of lesson data
- 🎯 **Need**: Faster API responses
- 💡 **Suggestion**: Implement Redis caching, database indexing

### 7. Testing

#### Unit Tests
- ⚠️ No automated tests
- 🎯 **Need**: Comprehensive test coverage
- 💡 **Suggestion**: Add pytest for backend, Jest for frontend

#### Integration Tests
- ⚠️ No end-to-end testing
- 🎯 **Need**: Automated E2E tests
- 💡 **Suggestion**: Use Playwright for E2E testing

### 8. Documentation

#### API Documentation
- ⚠️ No formal API documentation
- 🎯 **Need**: OpenAPI/Swagger documentation
- 💡 **Suggestion**: Add Swagger UI, document all endpoints

#### User Guide
- ⚠️ No user documentation
- 🎯 **Need**: User manual with screenshots
- 💡 **Suggestion**: Create step-by-step guides, video tutorials

### 9. Deployment

#### Production Setup
- ⚠️ Currently development-only setup
- 🎯 **Need**: Production-ready deployment
- 💡 **Suggestion**: Docker containers, environment configs, CI/CD pipeline

#### Database
- ⚠️ Using JSON file for data storage
- 🎯 **Need**: Proper database (PostgreSQL, MongoDB)
- 💡 **Suggestion**: Migrate to database with proper schema

---

## 📊 Technical Stack

### Backend
- **Framework**: Flask
- **AI**: OpenAI GPT-4o-mini
- **PDF Generation**: Playwright (Chromium)
- **Template Engine**: Jinja2
- **PPTX Processing**: python-pptx
- **Language**: Python 3.13

### Frontend
- **Framework**: Next.js 15.5.4
- **UI Library**: React
- **Styling**: Tailwind CSS
- **Language**: TypeScript
- **Build Tool**: Turbopack

### Data
- **Storage**: JSON file (`lessons.json`)
- **Format**: Structured lesson objects with English keys

---

## 🎯 Priority Improvements

### High Priority
1. **Improve objective extraction** - Critical for lesson quality
2. **Better Arabic font support** - Essential for Math PDFs
3. **Add PDF preview** - Improves user experience significantly
4. **Implement caching** - Performance improvement

### Medium Priority
5. **Add file upload interface** - Better workflow
6. **Improve error handling** - Better debugging
7. **Add batch processing** - Efficiency improvement
8. **Create API documentation** - Developer experience

### Low Priority
9. **Add unit tests** - Long-term maintainability
10. **Enhance PDF styling** - Visual polish
11. **Add user guide** - Onboarding improvement
12. **Setup production deployment** - Future scalability

---

## 📁 Project Structure

```
raida-concept/
├── backend/
│   ├── app.py                    # Flask API endpoints
│   ├── main.py                   # AI processing & PDF generation
│   ├── preprocess_data.py        # PPTX extraction & data processing
│   ├── templates/
│   │   ├── template_french.html  # French lesson template
│   │   └── template_math.html    # Math lesson template (Arabic)
│   ├── data/
│   │   └── lessons.json          # Processed lesson data
│   ├── lessons/                  # Source PPTX files
│   ├── output_pdfs/              # Generated PDFs
│   └── temp_html/                # Temporary HTML files
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── index.tsx         # Main application page
│   │   └── styles/
│   │       └── globals.css       # Global styles
│   └── package.json
└── README.md
```

---

## 🔄 Recent Changes

### 2025-11-25
- ✅ Refactored PDF generation with subject-specific templates
- ✅ Added Arabic support for Math lessons
- ✅ Implemented dynamic lesson step extraction
- ✅ Removed Date and Groupe/Horaire fields
- ✅ Updated field labels (Période, Semaine, Séance)
- ✅ Added multilingual frontend (French/Arabic)
- ✅ Implemented 5-level cascading selection
- ✅ Fixed runtime errors and improved error handling
- ✅ Enhanced UI with modern design and animations

---

## 💡 Future Vision

### Short-term (1-3 months)
- Improve data extraction quality
- Add more subjects (Science, History, etc.)
- Implement user authentication
- Add lesson editing capabilities

### Medium-term (3-6 months)
- Database migration
- Advanced analytics and reporting
- Collaborative features (sharing lessons)
- Mobile app

### Long-term (6-12 months)
- AI-powered lesson suggestions
- Integration with learning management systems
- Multi-school support
- Advanced customization options

---

## 🤝 Contributing

To contribute to this project:
1. Review this state document
2. Pick a feature from "Needing Improvement"
3. Create a detailed implementation plan
4. Implement with tests
5. Update this document

---

## 📞 Support

For questions or issues:
- Check the walkthrough documentation
- Review console logs (F12 in browser)
- Check Flask terminal output
- Verify environment variables are set

---

**Status**: ✅ Functional | 🚀 Actively Developing | 📈 Growing
