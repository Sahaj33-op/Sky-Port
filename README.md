# 🚀 Sky-Port

**Comprehensive Hypixel SkyBlock Profile Exporter**

***

## 📋 Overview

**Sky-Port** is a powerful web-based utility designed for the Hypixel SkyBlock community. While tools like SkyCrypt excel at *displaying* data, Sky-Port fills the crucial gap by providing comprehensive **data export capabilities**. Export your entire SkyBlock profile in multiple formats for analysis, archival, or sharing.

Built with Python and Streamlit, Sky-Port offers a clean, minimalist interface that prioritizes functionality and speed, making it the definitive tool for SkyBlock data portability.

### 🎯 Key Features

- **🔍 Complete Profile Analysis** - Mirror SkyCrypt's comprehensive data coverage
- **📊 Multiple Export Formats** - Excel, JSON, CSV, PDF with professional formatting
- **💰 Advanced Calculations** - Networth, Farming Weight, and Enhanced Metrics
- **🚀 One-Click Exports** - Full profile or selective category exports
- **⚡ Fast Performance** - Optimized caching and processing
- **🌐 Cloud Ready** - Deployable on Streamlit Cloud

***

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Hypixel API key (get one with `/api new` in Hypixel)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sahaj33-op/Sky-Port.git
   cd Sky-Port
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API key**
   
   Create `.streamlit/secrets.toml`:
   ```toml
   hypixel_api_key = "your-hypixel-api-key-here"
   ```

4. **Run the application**
   ```bash
   streamlit run main.py
   ```

5. **Access the app**
   
   Open `http://localhost:8501` in your browser

***

## 📊 Features & Data Coverage

### Exportable Data Categories

| Category | Description | Data Points |
|----------|-------------|-------------|
| **👤 Profile Info** | Player stats, game mode, objectives | UUID, last save, fairy souls, deaths |
| **⭐ Skills** | All skill levels and XP progression | 11 skills with levels, XP, and averages |
| **🗡️ Slayers** | Boss kills and tier completions | Zombie, Spider, Wolf, Enderman, Blaze |
| **⚔️ Dungeons** | Catacombs and class progression | Floor completions, class levels, secrets |
| **🎒 Inventories** | Complete item data with NBT | Inventory, Ender Chest, Equipment, Accessories |
| **📚 Collections** | Collection progress and minions | All collection tiers and crafted minions |
| **🐕 Pets** | Pet collection with stats | Levels, rarity, held items, XP |
| **🌾 Farming** | Garden stats and contests | Farming weight, medals, visitor stats |
| **🏛️ Museum** | Donated items and progress | All museum categories and completion |
| **💰 Networth** | Detailed wealth breakdown | Category-wise networth analysis |

### Export Formats

- **📊 Excel (.xlsx)** - Multi-sheet workbooks with formatting and charts
- **🔧 JSON** - Structured data for developers and analysis tools  
- **📈 CSV Bundle** - Individual CSV files for each data category
- **📄 PDF Report** - Formatted reports with visual summaries

***

## 🛠️ Technical Architecture

### Core Components

```
sky_port/
├── main.py                 # Streamlit application entry point
├── api/                    # API integration layer
│   ├── hypixel_client.py  # Official Hypixel API
│   ├── mojang_client.py   # UUID resolution
│   ├── skyhelper_networth.py  # Networth calculations
│   ├── elite_farming.py   # Farming weight integration
│   └── neu_repository.py  # Item data enhancement
├── processors/            # Data processing modules
│   └── profile_processor.py  # Main data processor
├── exporters/            # Export format generators
│   ├── excel_exporter.py # Excel workbook creation
│   ├── json_exporter.py  # JSON formatting
│   ├── csv_exporter.py   # CSV bundle generation
│   └── pdf_exporter.py   # PDF report creation
└── utils/                # Utility functions
    ├── cache.py          # Session management
    └── rate_limiter.py   # API rate limiting
```

### API Integrations

Sky-Port integrates with multiple specialized APIs for comprehensive data:

- **[Hypixel API](https://api.hypixel.net/)** - Official player and profile data
- **[SkyHelper Networth](https://github.com/Altpapier/SkyHelper-Networth)** - Accurate networth calculations
- **[Elite Bot](https://elitebot.dev/)** - Advanced farming weight metrics
- **[NotEnoughUpdates](https://github.com/NotEnoughUpdates/NotEnoughUpdates-REPO)** - Item data repository
- **Mojang API** - Username to UUID resolution

***

## 🎮 Usage Guide

### Basic Workflow

1. **Enter API Key** - Input your Hypixel API key in the configuration section
2. **Search Player** - Enter any Minecraft username to fetch their profiles  
3. **Select Profile** - Choose from available SkyBlock profiles
4. **Process Data** - Click "Process Profile" to analyze all data
5. **Export** - Choose formats and categories, then download your files

### Export Options

#### Full Profile Export
- Exports **all** available data categories
- Includes enhanced calculations (networth, farming weight)
- Perfect for complete profile backups

#### Selective Export  
- Choose specific data categories
- Customize export formats
- Ideal for targeted analysis

### Advanced Features

- **Real-time Processing** - Live progress updates during data processing
- **Enhanced Metrics** - Visual dashboard with key statistics
- **Error Recovery** - Robust handling of API limitations and errors
- **Caching System** - Optimized performance with intelligent data caching

***

## 🚀 Deployment

### Streamlit Cloud Deployment

1. **Fork the repository** to your GitHub account

2. **Create Streamlit Cloud app**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Deploy from your forked repository

3. **Configure secrets**
   - In Advanced settings, add:
   ```toml
   hypixel_api_key = "your-api-key-here"
   ```

4. **Deploy** - Your app will be available at `https://your-app-name.streamlit.app`

### Local Development

```bash
# Install in development mode
pip install -r requirements.txt

# Run with debugging
streamlit run main.py --server.runOnSave true

# Access development server
# http://localhost:8501
```

***

## 📊 Performance & Limitations

### Performance Optimizations

- **Caching Strategy** - 5-minute cache for profile data, 10-minute cache for enhanced calculations
- **Rate Limiting** - Built-in rate limiting to respect API boundaries
- **Efficient Processing** - Pandas-optimized data structures for large profiles
- **Memory Management** - Streaming downloads for large export files

### API Rate Limits

- **Hypixel API** - 120 requests per minute
- **Mojang API** - 600 requests per 10 minutes  
- **Mitigation** - Intelligent caching and request batching

### Known Limitations

- Private profiles cannot be accessed
- Some data requires recent login to SkyBlock
- Export file size limits depend on deployment platform

***

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

1. **Fork and clone**
   ```bash
   git clone https://github.com/your-username/Sky-Port.git
   cd Sky-Port
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Contribution Guidelines

- **Code Style** - Follow PEP 8 standards
- **Documentation** - Update docstrings and README for new features
- **Testing** - Add tests for new functionality
- **Commits** - Use clear, descriptive commit messages

### Priority Areas

- 🔧 Additional export formats (XML, YAML)
- 📊 Enhanced data visualizations  
- 🚀 Performance optimizations
- 🌐 Internationalization support
- 📱 Mobile-responsive design improvements

***

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

***

## 🙏 Acknowledgments & Credits

Sky-Port builds upon the excellent work of the SkyBlock community:

- **[SkyCrypt](https://sky.shiiyu.moe/)** - Inspiration and data structure reference
- **[SkyHelper](https://github.com/Altpapier/SkyHelper-Networth)** - Networth calculation algorithms  
- **[Elite Bot](https://elitebot.dev/)** - Farming weight calculation system
- **[NotEnoughUpdates](https://github.com/NotEnoughUpdates/NotEnoughUpdates-REPO)** - Comprehensive item repository
- **[Hypixel](https://hypixel.net/)** - Official API and game data

Special thanks to the entire Hypixel SkyBlock community for their continued support and feedback.

***

## 📞 Support & Contact

### Getting Help

- **🐛 Bug Reports** - [GitHub Issues](https://github.com/Sahaj33-op/Sky-Port/issues)
- **💡 Feature Requests** - [GitHub Discussions](https://github.com/Sahaj33-op/Sky-Port/discussions)  
- **📚 Documentation** - [Project Wiki](https://github.com/Sahaj33-op/Sky-Port/wiki)

### Community

- **Discord** - Join our community server (coming soon)
- **Reddit** - r/HypixelSkyblock discussions
- **GitHub** - Star the repo and follow for updates

***

## 📈 Project Status

- ✅ **Phase 1**: Core Engine & Basic UI (Complete)
- ✅ **Phase 2**: Advanced Data Processing & Exporting (Complete)  
- ✅ **Phase 3**: UI Refinement & Feature Completion (Complete)
- 🚀 **Phase 4**: Deployment & Community Feedback (Current)

### Recent Updates

- **v2.0.0** - Enhanced API integrations and export system
- **v1.5.0** - Multi-format export capabilities  
- **v1.0.0** - Initial release with core functionality

***

## 🔮 Roadmap

### Upcoming Features

- **📊 Data Visualization** - Interactive charts and graphs
- **🔄 Automatic Updates** - Scheduled profile refreshes
- **👥 Bulk Processing** - Multiple profile analysis
- **🎨 Themes** - Customizable UI themes
- **📱 Mobile App** - Native mobile application

### Long-term Goals

- **🤖 AI Analysis** - Intelligent profile insights and recommendations
- **🏆 Leaderboards** - Community comparison features  
- **📈 Historical Tracking** - Progress tracking over time
- **🌐 API Service** - Public API for developers

***

**Built with ❤️ for the Hypixel SkyBlock community**

*Sky-Port - Your gateway to SkyBlock data ownership*

***

> **Note**: This project is not affiliated with Hypixel Inc. All trademarks and game content are property of their respective owners.
