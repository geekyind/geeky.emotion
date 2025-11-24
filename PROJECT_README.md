<div align="center">
  <img src="public/LogoLore.svg" alt="Lore Emotion Logo" width="200" />
  <h1>Lore Emotion</h1>
  <p>A privacy-first emotional support platform connecting users with community support and professional care.</p>
</div>

## 🌟 Features

- **Anonymous Posting**: Share thoughts and feelings with complete anonymity
- **Privacy by Design**: Military-grade encryption and data separation
- **Community Support**: Connect with others who understand
- **Professional Care**: Access to trained mental health professionals
- **Crisis Intervention**: 24/7 crisis detection and resource connection
- **Similar Post Discovery**: Find others with shared experiences using ML
- **Content Moderation**: Multi-layered safety systems

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **Authentication**: AWS Cognito with JWT tokens
- **Anonymization**: Cryptographic anonymous ID generation
- **Content Moderation**: ML-powered safety checks
- **Similar Posts**: Sentence transformers for semantic search
- **Database**: Separate PostgreSQL databases for identity and content
- **Caching**: Redis for rate limiting and session management

### Frontend (Next.js 14)
- **Framework**: Next.js with App Router
- **Styling**: Tailwind CSS with Lore.co-inspired design
- **State**: Zustand for global state management
- **Animations**: Framer Motion for smooth interactions
- **Auth**: Amazon Cognito Identity JS

## 📁 Project Structure

```
lore.emotion/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core utilities (config, database, security)
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   ├── middleware/     # Custom middleware
│   │   └── main.py         # Application entry point
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   └── SETUP.md           # Backend setup guide
│
├── frontend/               # Next.js 14 frontend
│   ├── app/               # Next.js App Router
│   │   ├── auth/          # Authentication pages
│   │   ├── dashboard/     # Protected dashboard
│   │   └── page.tsx       # Home page
│   ├── components/        # Reusable React components
│   ├── lib/              # Utilities (auth, API, store)
│   ├── package.json      # Node dependencies
│   ├── tailwind.config.ts # Tailwind configuration
│   └── SETUP.md          # Frontend setup guide
│
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Conda (Anaconda or Miniconda) - recommended
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- AWS Account (for Cognito)

### Backend Setup

```powershell
# Navigate to backend
cd backend

# Create conda environment
conda create -n lore-emotion python=3.10 -y
conda activate lore-emotion

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your configuration

# Run the server
python app/main.py
```

Backend runs on: `http://localhost:8000`

API Docs: `http://localhost:8000/api/docs`

See [backend/SETUP.md](backend/SETUP.md) for detailed instructions.

### Frontend Setup

```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Configure environment
copy .env.local.example .env.local
# Edit .env.local with your configuration

# Run development server
npm run dev
```

Frontend runs on: `http://localhost:3000`

See [frontend/SETUP.md](frontend/SETUP.md) for detailed instructions.

## 🔐 Security & Privacy

### Anonymization Pipeline
1. User identity stored in separate encrypted database
2. Content linked via cryptographic anonymous ID
3. PII automatically scrubbed from posts
4. Timestamps fuzzed to prevent correlation
5. K-anonymity ensures posts can't be uniquely identified

### Content Moderation
1. **Real-time Screening** (<100ms): Profanity, PII, self-harm detection
2. **Risk Assessment** (<5 min): ML-based severity scoring
3. **Human Review**: Professional moderators for flagged content
4. **Crisis Detection**: Immediate intervention for high-risk content

### Data Protection
- AES-256 encryption at rest
- TLS 1.3 for data in transit
- Separate databases for identity and content
- Role-based access control
- Comprehensive audit logging

## 🎨 Design Philosophy

Inspired by **Lore.co**, the design prioritizes:

- **Warm & Calming**: Soft blues, sage greens, and warm purples
- **Empathetic**: Conversational interface with supportive microcopy
- **Accessible**: WCAG 2.1 AA compliant with keyboard navigation
- **Spacious**: Generous whitespace to reduce anxiety
- **Progressive**: Features unlock gradually as trust builds

### Color Palette
- Soft Blue: `#6B9BD1` (calm, support)
- Sage Green: `#8FA998` (growth, healing)
- Warm Purple: `#9B87C4` (wisdom, depth)
- Off-White: `#F9F7F4` (warmth)
- Gentle Orange: `#E8A87C` (encouragement)

## 📊 Key Metrics

### Safety Metrics
- Crisis intervention response time: <1 hour
- False positive rate: <2%
- Bad actor removal time: <24 hours
- User safety rating: >4.2/5

### User Wellbeing
- Resolution rate: >60%
- Connection rate: >40%
- Healthy session duration: 15-30 minutes
- Break acceptance rate: >60%

### Privacy
- Re-identification attempts: 0 successful
- PII leak rate: <0.1%
- Privacy comprehension: >90%

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL (with asyncpg)
- **Cache**: Redis
- **Auth**: AWS Cognito + JWT
- **ML/NLP**: Sentence Transformers, scikit-learn
- **Monitoring**: Prometheus, Sentry

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **State**: Zustand
- **Animation**: Framer Motion
- **Icons**: Lucide React
- **HTTP**: Axios

### Infrastructure (Recommended)
- **Hosting**: AWS (EC2, ECS, or Lambda)
- **Database**: RDS PostgreSQL
- **Cache**: ElastiCache Redis
- **CDN**: CloudFront
- **Storage**: S3
- **Monitoring**: CloudWatch

## 📈 Roadmap

### Phase 1: Foundation (Months 1-3) ✅
- [x] Core anonymization pipeline
- [x] Basic content moderation
- [x] Crisis detection and intervention
- [x] Essential privacy controls
- [x] Professional queue system

### Phase 2: Scale (Months 4-6)
- [ ] Similar post discovery (ML-based)
- [ ] Advanced matching algorithms
- [ ] Community feedback systems
- [ ] Comprehensive audit logging
- [ ] Mobile app (iOS/Android)

### Phase 3: Optimization (Months 7-12)
- [ ] AI model improvements
- [ ] Peer support program
- [ ] Advanced analytics dashboard
- [ ] Internationalization (5+ languages)
- [ ] Research partnerships

### Phase 4: Innovation (Year 2+)
- [ ] Predictive wellbeing insights
- [ ] Healthcare provider integration
- [ ] Virtual support groups
- [ ] Long-term outcome tracking
- [ ] Open-source safety tools

## 🤝 Contributing

We welcome contributions that improve safety, privacy, and user experience.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

[To be determined based on project requirements]

## 📞 Crisis Resources

**If you're in crisis, please reach out immediately:**

- **US**: 988 (Suicide & Crisis Lifeline)
- **US Text**: Text HOME to 741741 (Crisis Text Line)
- **UK**: 116 123 (Samaritans)
- **International**: https://findahelpline.com/

## 📧 Contact

- **Platform Support**: support@lore.emotion (fictional)
- **Privacy Questions**: privacy@lore.emotion (fictional)
- **Security Issues**: security@lore.emotion (fictional)

---

Built with ❤️ for those who need a safe space to share.
